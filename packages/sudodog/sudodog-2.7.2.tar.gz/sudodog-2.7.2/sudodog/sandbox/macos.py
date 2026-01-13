"""
macOS sandbox-exec based sandbox implementation.

Uses macOS sandbox-exec for application sandboxing.
"""

import subprocess
import logging
import threading
import tempfile
import os
import time
from typing import Dict, Any, List

from .base import SandboxBase

logger = logging.getLogger(__name__)

# Try to import psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - limited stats")


class MacOSSandboxExecSandbox(SandboxBase):
    """macOS sandbox-exec based sandboxing"""

    def __init__(self, agent_id: str, limits: Dict[str, Any], config: Dict[str, Any]):
        super().__init__(agent_id, limits, config)
        self.sandbox_profile = None
        # BUG-M003 FIX: Initialize profile_path to prevent AttributeError in cleanup
        self.profile_path = None
        self.monitor_thread = None
        self.actions_log = []
        self.security_events = []
        self._deprecation_warned = False

    def setup(self):
        """Create macOS sandbox profile"""
        logger.info(f"Setting up macOS sandbox for agent {self.agent_id}")

        # BUG-M004 FIX: Warn about sandbox-exec deprecation
        if not self._deprecation_warned:
            logger.warning(
                "Note: sandbox-exec is deprecated by Apple since macOS 10.15. "
                "For stronger isolation, consider using Docker: sudodog run --docker"
            )
            self._deprecation_warned = True

        # Generate sandbox profile
        self.sandbox_profile = self._generate_sandbox_profile()

        # Write profile to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.sb',
            delete=False
        ) as f:
            f.write(self.sandbox_profile)
            self.profile_path = f.name

        logger.info(f"Sandbox profile created: {self.profile_path}")

    def _generate_sandbox_profile(self) -> str:
        """
        Generate macOS sandbox profile.

        Returns:
            Sandbox profile as string (Scheme-like syntax)
        """
        # Determine access permissions
        allow_network = self.config.get('allow_network', True)
        allow_home = self.config.get('allow_home', True)
        allow_temp = self.config.get('allow_temp', True)

        # BUG-M002 FIX: Build profile with proper conditionals to avoid empty lines
        profile_lines = [
            "(version 1)",
            "(debug deny)",
            "",
            "; Default behavior",
            "(allow default)",
            "",
            "; Deny dangerous operations",
            '(deny file-write* (subpath "/System"))',
            '(deny file-write* (subpath "/usr") (subpath "/usr/local"))',
            '(deny file-write* (subpath "/bin"))',
            '(deny file-write* (subpath "/sbin"))',
            '(deny file-write* (subpath "/Library"))',
        ]

        # Conditionally add home directory access
        if allow_home:
            home_path = os.path.expanduser("~")
            profile_lines.extend([
                "",
                "; Allow user home directory",
                f'(allow file-read* file-write* (subpath "{home_path}"))',
            ])

        # Conditionally add temp directory access
        if allow_temp:
            profile_lines.extend([
                "",
                "; Allow tmp directories",
                '(allow file-read* file-write* (subpath "/tmp"))',
                '(allow file-read* file-write* (subpath "/var/tmp"))',
            ])

        # Network access
        profile_lines.extend([
            "",
            "; Network access",
            "(allow network*)" if allow_network else "(deny network*)",
        ])

        # Common allowances
        profile_lines.extend([
            "",
            "; Allow process operations",
            "(allow process-fork)",
            "(allow process-exec*)",
            "",
            "; Allow IPC",
            "(allow ipc-posix-shm)",
            "(allow mach-lookup)",
            "",
            "; Deny some dangerous operations",
            "(deny system-socket)",
            '(deny file-ioctl (path "/dev/random"))',
            "",
            "; Allow reading /dev/urandom (needed by Python)",
            '(allow file-read* (path "/dev/urandom"))',
            '(allow file-read* (path "/dev/random"))',
        ])

        return "\n".join(profile_lines) + "\n"

    def run(self, command: List[str]) -> int:
        """Execute command in macOS sandbox"""
        self.setup()
        self._running = True

        try:
            # Build sandbox-exec command
            sandbox_command = [
                'sandbox-exec',
                '-f', self.profile_path
            ] + command

            logger.info(f"Starting sandboxed process: {' '.join(command)}")

            # Start process
            self.process = subprocess.Popen(
                sandbox_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info(f"Started process PID {self.process.pid}")

            # Start monitoring thread
            self.monitor_thread = threading.Thread(
                target=self.monitor_loop,
                daemon=True
            )
            self.monitor_thread.start()

            # Wait for completion
            stdout, stderr = self.process.communicate()

            exit_code = self.process.returncode

            # Log output
            if stdout:
                logger.debug(f"STDOUT:\n{stdout.decode('utf-8', errors='replace')}")
            if stderr:
                logger.debug(f"STDERR:\n{stderr.decode('utf-8', errors='replace')}")

            logger.info(f"Process completed with exit code {exit_code}")

            return exit_code

        except Exception as e:
            logger.error(f"Error running command: {e}")
            raise

        finally:
            self._running = False
            self.cleanup()

    def get_stats(self) -> Dict[str, Any]:
        """Get macOS process stats"""
        # BUG-M001 FIX: Provide meaningful fallback stats instead of empty dict
        if not self.process:
            return {
                "status": "no_process",
                "error": "Process not started"
            }

        if not PSUTIL_AVAILABLE:
            return {
                "status": "limited",
                "pid": self.process.pid,
                "running": self.process.poll() is None,
                "error": "psutil not available - install with: pip install psutil"
            }

        try:
            proc = psutil.Process(self.process.pid)

            stats = {
                "status": "ok",
                "pid": self.process.pid,
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_bytes": proc.memory_info().rss,
                "memory_percent": proc.memory_percent(),
                "num_threads": proc.num_threads(),
            }

            # IO counters (if available on macOS)
            try:
                io = proc.io_counters()
                stats["io_counters"] = {
                    "read_bytes": io.read_bytes,
                    "write_bytes": io.write_bytes,
                    "read_count": io.read_count,
                    "write_count": io.write_count
                }
            except (psutil.AccessDenied, AttributeError):
                stats["io_counters"] = {}

            # Network connections
            try:
                connections = proc.connections()
                stats["network_connections"] = len(connections)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                stats["network_connections"] = 0

            # macOS-specific: Get process info
            try:
                stats["process_status"] = proc.status()
                stats["create_time"] = proc.create_time()
            except Exception:
                pass

            return stats

        except psutil.NoSuchProcess:
            return {
                "status": "exited",
                "pid": self.process.pid,
                "running": False
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "status": "error",
                "pid": self.process.pid,
                "error": str(e)
            }

    def cleanup(self):
        """Clean up macOS sandbox"""
        logger.info("Cleaning up macOS sandbox")

        # Kill process if still running
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        # Remove temporary sandbox profile
        if self.profile_path and os.path.exists(self.profile_path):
            try:
                os.remove(self.profile_path)
                logger.info("Sandbox profile removed")
            except Exception as e:
                logger.error(f"Error removing sandbox profile: {e}")

    def get_platform_name(self) -> str:
        """Return 'darwin'"""
        return "darwin"

    def get_recent_actions(self) -> List[Dict[str, Any]]:
        """
        Track actions on macOS.

        For full implementation, would use:
        - macOS Endpoint Security framework
        - fs_usage for file system monitoring
        - DTTrace for system call tracing
        - macOS Unified Logging
        """
        actions = self.actions_log.copy()
        self.actions_log.clear()
        return actions

    def check_security_patterns(self) -> Dict[str, Any]:
        """
        Check for dangerous patterns on macOS.

        For full implementation, would check:
        - Keychain access attempts
        - Code signing violations
        - Suspicious process spawning
        - Privacy database access (TCC)
        """
        events = self.security_events.copy()
        self.security_events.clear()

        return {
            "threats_detected": len(events),
            "patterns_blocked": events,
            "timestamp": time.time()
        }

    def _track_file_access(self, filepath: str, operation: str):
        """Track file access (helper for future implementation)"""
        self.actions_log.append({
            "type": "file",
            "operation": operation,
            "path": filepath,
            "timestamp": time.time()
        })

    def _detect_threat(self, threat_type: str, details: Dict[str, Any]):
        """Detect security threat (helper for future implementation)"""
        self.security_events.append({
            "type": threat_type,
            "details": details,
            "timestamp": time.time()
        })
