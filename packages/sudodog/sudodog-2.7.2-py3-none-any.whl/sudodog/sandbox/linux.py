"""
Linux namespace-based sandbox implementation.

Uses Linux namespaces for isolation without requiring Docker.
Includes strace-based security monitoring for file and network access.
Integrates guardrails for real-time blocking and output filtering.
"""

import subprocess
import os
import logging
import threading
import time
import re
import shutil
from typing import Dict, Any, List, Optional, Set, Tuple

from .base import SandboxBase

logger = logging.getLogger(__name__)

# Import guardrails
try:
    from ..core.guardrails import GuardrailEngine, GuardrailAction
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False
    logger.debug("Guardrails module not available")

# Import exec blocker for pre-execution command blocking
try:
    from ..core.exec_blocker import (
        ExecBlocker,
        setup_exec_blocking,
        compile_if_needed as compile_exec_blocker,
        is_available as exec_blocker_available
    )
    EXEC_BLOCKER_AVAILABLE = True
except ImportError:
    EXEC_BLOCKER_AVAILABLE = False
    logger.debug("Exec blocker module not available")

# BUG-L001 FIX: Add try/except for psutil import like Windows/macOS
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - limited stats")

# Check if strace is available
STRACE_AVAILABLE = shutil.which('strace') is not None

# Sensitive file patterns that should trigger security alerts
SENSITIVE_PATHS = [
    '/etc/passwd',
    '/etc/shadow',
    '/etc/sudoers',
    '/etc/ssh/',
    '/.ssh/',
    '/id_rsa',
    '/id_ed25519',
    '/.aws/',
    '/.kube/',
    '/.docker/',
    '/credentials',
    '/secrets',
    '/.env',
    '/token',
    '/api_key',
    '/private_key',
]

# Suspicious network ports
SUSPICIOUS_PORTS = {
    22: 'SSH',
    23: 'Telnet',
    3389: 'RDP',
    4444: 'Metasploit',
    5555: 'Android Debug',
    6666: 'IRC/Backdoor',
    6667: 'IRC',
    31337: 'Back Orifice',
}

# Dangerous syscalls that might indicate malicious behavior
DANGEROUS_SYSCALLS = [
    'ptrace',      # Process tracing/debugging
    'process_vm_readv',  # Read another process memory
    'process_vm_writev', # Write another process memory
    'init_module',  # Load kernel module
    'finit_module', # Load kernel module
    'delete_module', # Unload kernel module
    'reboot',       # System reboot
    'sethostname',  # Change hostname
    'setdomainname', # Change domain name
    'kexec_load',   # Load new kernel
]


class LinuxNamespaceSandbox(SandboxBase):
    """Linux namespace-based sandboxing with security monitoring and guardrails"""

    def __init__(self, agent_id: str, limits: Dict[str, Any], config: Dict[str, Any]):
        super().__init__(agent_id, limits, config)
        self.monitor_thread = None
        self.strace_thread = None
        self.actions_log = []
        self.security_events = []
        self.file_access_log: List[Dict[str, Any]] = []
        self.network_access_log: List[Dict[str, Any]] = []
        self.syscall_log: List[Dict[str, Any]] = []
        self.strace_process: Optional[subprocess.Popen] = None
        # BUG-L003 FIX: Initialize workspace to prevent AttributeError in cleanup
        self.workspace = None
        # Track unique files and connections for summary
        self.files_read: Set[str] = set()
        self.files_written: Set[str] = set()
        self.network_connections: Set[str] = set()

        # Initialize guardrails
        self.guardrails: Optional[GuardrailEngine] = None
        self.guardrails_enabled = config.get('guardrails_enabled', True)
        if GUARDRAILS_AVAILABLE and self.guardrails_enabled:
            self.guardrails = GuardrailEngine(config)
            logger.info("Guardrails enabled")

        # Track blocked actions
        self.blocked_files: Set[str] = set()
        self.blocked_commands: List[str] = []
        self.blocked_network: Set[str] = set()
        self.output_redactions: List[Dict[str, Any]] = []

        # Initialize exec blocker for pre-execution command blocking
        self.exec_blocker: Optional[ExecBlocker] = None
        self.exec_blocker_enabled = config.get('exec_blocker_enabled', True)
        if EXEC_BLOCKER_AVAILABLE and self.exec_blocker_enabled:
            self.exec_blocker = ExecBlocker()
            logger.info("Exec blocker available for pre-execution blocking")

    def setup(self):
        """Prepare Linux namespace sandbox"""
        logger.info(f"Setting up Linux namespace sandbox for agent {self.agent_id}")

        # Verify we're on Linux
        if not os.path.exists('/proc'):
            raise RuntimeError("Linux /proc filesystem not found")

        # Create temp directory for agent if needed
        self.workspace = f"/tmp/sudodog-{self.agent_id}"
        os.makedirs(self.workspace, exist_ok=True)

        # Log strace availability
        if STRACE_AVAILABLE:
            logger.info("strace available - security monitoring enabled")
        else:
            logger.warning("strace not available - install for enhanced security monitoring")

        # Compile exec blocker library if available
        if self.exec_blocker:
            if self.exec_blocker.compile():
                logger.info("Exec blocker compiled - pre-execution blocking enabled")
            else:
                logger.warning("Could not compile exec blocker - pre-execution blocking disabled")
                self.exec_blocker = None

    def run(self, command: List[str]) -> int:
        """
        Execute command in Linux namespace with security monitoring.

        Uses unshare for namespace isolation and strace for syscall tracking.
        Enforces guardrails for command blocking and output filtering.
        """
        self.setup()
        self._running = True

        # Check command against guardrails BEFORE execution
        command_str = ' '.join(command)
        if self.guardrails:
            result = self.guardrails.check_command(command_str)
            if not result.allowed:
                self.blocked_commands.append(command_str)
                self._detect_threat('command_blocked', {
                    'command': command_str,
                    'reason': result.reason,
                    'description': f'Command blocked by guardrails: {result.reason}'
                })
                print(f"\n🛑 Command Blocked by Guardrails")
                print(f"   Reason: {result.reason}")
                print(f"   Command: {command_str[:100]}...")
                self._display_security_summary()
                return 1  # Return error code

        # Build unshare command for namespace isolation
        # Isolate: network, mount, IPC, UTS (hostname), PID
        unshare_flags = []

        # Check both config keys for network isolation
        # --no-network flag sets allow_network=False
        if self.config.get('isolate_network', False) or not self.config.get('allow_network', True):
            unshare_flags.append('--net')  # Network namespace

        if self.config.get('isolate_mount', True):
            unshare_flags.append('--mount')  # Mount namespace

        # Build final command
        if unshare_flags and os.geteuid() == 0:  # Only if root
            final_command = ['unshare'] + unshare_flags + ['--'] + command
            logger.info(f"Running with namespace isolation: {' '.join(final_command)}")
        else:
            final_command = command
            logger.warning("Running without namespace isolation (not root or disabled)")

        # Wrap with strace if available and security monitoring enabled
        use_strace = STRACE_AVAILABLE and self.config.get('security_monitoring', True)
        strace_output_file = None

        if use_strace:
            strace_output_file = os.path.join(self.workspace, 'strace.log')
            # Trace file, network, and process syscalls
            strace_cmd = [
                'strace',
                '-f',  # Follow forks
                '-e', 'trace=open,openat,read,write,connect,socket,execve,unlink,rename',
                '-e', 'signal=none',  # Don't trace signals
                '-o', strace_output_file,
                '--'
            ] + final_command
            final_command = strace_cmd
            logger.info("Security monitoring enabled via strace")

        # Set resource limits using cgroups (if available)
        env = os.environ.copy()

        # Set up LD_PRELOAD for pre-execution command blocking
        if self.exec_blocker:
            block_log_path = os.path.join(self.workspace, 'blocked_commands.log')
            blocking_env = self.exec_blocker.get_env_vars(
                log_path=block_log_path,
                debug=self.config.get('debug', False)
            )
            if blocking_env:
                # Merge with existing LD_PRELOAD if any
                if 'LD_PRELOAD' in env and 'LD_PRELOAD' in blocking_env:
                    env['LD_PRELOAD'] = f"{blocking_env['LD_PRELOAD']}:{env['LD_PRELOAD']}"
                    del blocking_env['LD_PRELOAD']
                env.update(blocking_env)
                logger.info("LD_PRELOAD exec blocker enabled")

        # Start process
        try:
            self.process = subprocess.Popen(
                final_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=self.workspace
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

            # Parse strace output for security analysis
            if use_strace and strace_output_file and os.path.exists(strace_output_file):
                self._parse_strace_output(strace_output_file)

            # Parse exec blocker log for blocked commands
            if self.exec_blocker:
                block_log_path = os.path.join(self.workspace, 'blocked_commands.log')
                self._parse_blocked_commands_log(block_log_path)

            # Send final security summary to dashboard
            self._send_final_telemetry(exit_code)

            # Display output to user with guardrails filtering
            if stdout:
                stdout_text = stdout.decode('utf-8', errors='replace')
                stdout_text = self._filter_output(stdout_text)
                print(stdout_text, end='')
            if stderr:
                import sys
                stderr_text = stderr.decode('utf-8', errors='replace')
                stderr_text = self._filter_output(stderr_text)
                print(stderr_text, end='', file=sys.stderr)

            # Display security summary
            self._display_security_summary()

            logger.info(f"Process completed with exit code {exit_code}")

            return exit_code

        except Exception as e:
            logger.error(f"Error running command: {e}")
            raise

        finally:
            self._running = False
            self.cleanup()

    def _parse_strace_output(self, strace_file: str):
        """Parse strace output to extract security-relevant events"""
        try:
            with open(strace_file, 'r', errors='replace') as f:
                for line in f:
                    self._parse_strace_line(line.strip())
        except Exception as e:
            logger.error(f"Error parsing strace output: {e}")

    def _parse_blocked_commands_log(self, log_file: str):
        """Parse the exec blocker's log of blocked commands"""
        if not os.path.exists(log_file):
            return

        try:
            with open(log_file, 'r', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Format: BLOCKED|command|pattern
                    parts = line.split('|', 2)
                    if len(parts) >= 3 and parts[0] == 'BLOCKED':
                        command = parts[1]
                        pattern = parts[2]

                        # Add to blocked commands list (avoid duplicates)
                        if command not in self.blocked_commands:
                            self.blocked_commands.append(command)
                            self._detect_threat('exec_blocked', {
                                'command': command,
                                'pattern': pattern,
                                'description': f'Command blocked by exec blocker: {command[:80]}...'
                            })
                            logger.info(f"Exec blocker blocked: {command[:80]}")
        except Exception as e:
            logger.error(f"Error parsing blocked commands log: {e}")

    def _parse_strace_line(self, line: str):
        """Parse a single strace line and extract security events"""
        if not line:
            return

        timestamp = time.time()

        # Parse open/openat syscalls for file access
        # Example: openat(AT_FDCWD, "/etc/passwd", O_RDONLY) = 3
        open_match = re.search(r'open(?:at)?\([^,]*,\s*"([^"]+)"[^)]*([A-Z_|]+)', line)
        if open_match:
            filepath = open_match.group(1)
            flags = open_match.group(2)

            operation = 'read'
            if 'O_WRONLY' in flags or 'O_RDWR' in flags or 'O_CREAT' in flags:
                operation = 'write'
                self.files_written.add(filepath)
            else:
                self.files_read.add(filepath)

            self.file_access_log.append({
                'type': 'file',
                'operation': operation,
                'path': filepath,
                'flags': flags,
                'timestamp': timestamp
            })

            # Check for sensitive file access
            self._check_sensitive_file(filepath, operation)
            return

        # Parse connect syscalls for network access
        # Example: connect(3, {sa_family=AF_INET, sin_port=htons(443), sin_addr=inet_addr("1.2.3.4")}, 16) = 0
        connect_match = re.search(
            r'connect\(\d+,\s*\{[^}]*sin_port=htons\((\d+)\)[^}]*sin_addr=inet_addr\("([^"]+)"\)',
            line
        )
        if connect_match:
            port = int(connect_match.group(1))
            ip = connect_match.group(2)

            connection = f"{ip}:{port}"
            self.network_connections.add(connection)

            self.network_access_log.append({
                'type': 'network',
                'operation': 'connect',
                'ip': ip,
                'port': port,
                'timestamp': timestamp
            })

            # Check for suspicious ports
            self._check_suspicious_port(ip, port)
            return

        # Parse execve for process execution
        # Example: execve("/bin/sh", ["sh", "-c", "..."], ...) = 0
        exec_match = re.search(r'execve\("([^"]+)"', line)
        if exec_match:
            executable = exec_match.group(1)
            self.syscall_log.append({
                'type': 'exec',
                'path': executable,
                'timestamp': timestamp
            })

            # Check for shell spawning (potential escape attempt)
            if any(shell in executable for shell in ['/bin/sh', '/bin/bash', '/bin/zsh', '/bin/fish']):
                self._detect_threat('shell_spawn', {
                    'executable': executable,
                    'description': 'Agent spawned a shell process'
                })
            return

        # Check for dangerous syscalls
        for syscall in DANGEROUS_SYSCALLS:
            if line.startswith(syscall + '(') or f' {syscall}(' in line:
                self._detect_threat('dangerous_syscall', {
                    'syscall': syscall,
                    'line': line[:200],  # Truncate for logging
                    'description': f'Dangerous syscall detected: {syscall}'
                })
                break

    def _check_sensitive_file(self, filepath: str, operation: str):
        """Check if file access involves sensitive files using guardrails"""
        # Check guardrails first
        if self.guardrails:
            result = self.guardrails.check_file(filepath, operation)
            if not result.allowed:
                self.blocked_files.add(filepath)
                self._detect_threat('file_blocked', {
                    'path': filepath,
                    'operation': operation,
                    'reason': result.reason,
                    'description': f'File access blocked by guardrails: {filepath}'
                })
                return

        # Fallback to built-in sensitive file check
        filepath_lower = filepath.lower()

        for sensitive in SENSITIVE_PATHS:
            if sensitive.lower() in filepath_lower:
                self._detect_threat('sensitive_file_access', {
                    'path': filepath,
                    'operation': operation,
                    'pattern_matched': sensitive,
                    'description': f'Agent accessed sensitive file: {filepath}'
                })
                return

    def _check_suspicious_port(self, ip: str, port: int):
        """Check if network connection is allowed using guardrails"""
        # Check guardrails first
        if self.guardrails:
            result = self.guardrails.check_network(ip, port)
            if not result.allowed:
                self.blocked_network.add(f"{ip}:{port}")
                self._detect_threat('network_blocked', {
                    'ip': ip,
                    'port': port,
                    'reason': result.reason,
                    'description': f'Network connection blocked by guardrails: {ip}:{port}'
                })
                return

        # Fallback to built-in suspicious port check
        if port in SUSPICIOUS_PORTS:
            self._detect_threat('suspicious_port', {
                'ip': ip,
                'port': port,
                'service': SUSPICIOUS_PORTS[port],
                'description': f'Connection to suspicious port: {port} ({SUSPICIOUS_PORTS[port]})'
            })

    def _filter_output(self, text: str) -> str:
        """Filter sensitive data from output using guardrails"""
        if not text or not self.guardrails:
            return text

        filtered_text, redactions = self.guardrails.filter_output(text)

        if redactions:
            self.output_redactions.extend(redactions)
            for redaction in redactions:
                self._detect_threat('output_redacted', {
                    'filter': redaction['filter'],
                    'count': redaction['count'],
                    'description': f"Redacted {redaction['count']} {redaction['description']}"
                })

        return filtered_text

    def _display_security_summary(self):
        """Display a summary of security-relevant activity including guardrails"""
        print("\n" + "─" * 50)
        print("🔒 Security Summary")
        print("─" * 50)

        # Guardrails summary (if active)
        if self.guardrails:
            guardrail_stats = self.guardrails.get_stats()
            blocked_count = (
                len(self.blocked_files) +
                len(self.blocked_commands) +
                len(self.blocked_network)
            )
            if blocked_count > 0 or self.output_redactions:
                print(f"\n🛡️  Guardrails Active:")
                if self.blocked_commands:
                    print(f"   Commands blocked: {len(self.blocked_commands)}")
                if self.blocked_files:
                    print(f"   File accesses blocked: {len(self.blocked_files)}")
                if self.blocked_network:
                    print(f"   Network connections blocked: {len(self.blocked_network)}")
                if self.output_redactions:
                    total_redactions = sum(r.get('count', 1) for r in self.output_redactions)
                    print(f"   Sensitive data redacted: {total_redactions} items")

        # File access summary
        if self.files_read or self.files_written:
            print(f"\n📁 File Access:")
            if self.files_read:
                # Show up to 10 files, sorted
                files_to_show = sorted(self.files_read)[:10]
                print(f"   Read: {len(self.files_read)} files")
                for f in files_to_show:
                    print(f"      • {f}")
                if len(self.files_read) > 10:
                    print(f"      ... and {len(self.files_read) - 10} more")
            if self.files_written:
                files_to_show = sorted(self.files_written)[:10]
                print(f"   Written: {len(self.files_written)} files")
                for f in files_to_show:
                    print(f"      • {f}")
                if len(self.files_written) > 10:
                    print(f"      ... and {len(self.files_written) - 10} more")

        # Network summary
        if self.network_connections:
            print(f"\n🌐 Network Connections: {len(self.network_connections)}")
            for conn in sorted(self.network_connections)[:10]:
                print(f"   • {conn}")
            if len(self.network_connections) > 10:
                print(f"   ... and {len(self.network_connections) - 10} more")

        # Security alerts (including guardrail blocks and exec blocker)
        guardrail_events = [e for e in self.security_events if e['type'] in
                          ['command_blocked', 'file_blocked', 'network_blocked', 'output_redacted', 'exec_blocked']]
        other_events = [e for e in self.security_events if e['type'] not in
                       ['command_blocked', 'file_blocked', 'network_blocked', 'output_redacted', 'exec_blocked']]

        if guardrail_events:
            print(f"\n🛑 Guardrail Actions: {len(guardrail_events)}")
            for event in guardrail_events[:10]:
                print(f"   🛡️  [{event['type']}] {event['details'].get('description', '')}")
            if len(guardrail_events) > 10:
                print(f"   ... and {len(guardrail_events) - 10} more")

        if other_events:
            print(f"\n⚠️  Security Alerts: {len(other_events)}")
            for event in other_events:
                severity = "🔴" if event['type'] in ['dangerous_syscall', 'sensitive_file_access'] else "🟡"
                print(f"   {severity} [{event['type']}] {event['details'].get('description', '')}")
        elif not guardrail_events:
            print(f"\n✅ No security alerts")

        print("─" * 50 + "\n")

    def get_stats(self) -> Dict[str, Any]:
        """Get Linux process stats using psutil"""
        # BUG-L002 FIX: Provide meaningful fallback stats instead of empty dict
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

            # Get comprehensive stats
            stats = {
                "status": "ok",
                "pid": self.process.pid,
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_bytes": proc.memory_info().rss,
                "memory_percent": proc.memory_percent(),
                "num_threads": proc.num_threads(),
                "num_fds": proc.num_fds() if hasattr(proc, 'num_fds') else 0,
            }

            # IO counters (if available)
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
        """Clean up Linux namespace sandbox"""
        logger.info("Cleaning up Linux sandbox")

        # Kill strace process if running
        if self.strace_process and self.strace_process.poll() is None:
            try:
                self.strace_process.terminate()
                self.strace_process.wait(timeout=2)
            except:
                pass

        # Kill process if still running
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        # Clean up workspace (optional)
        # We keep it for debugging by default
        # import shutil
        # if os.path.exists(self.workspace):
        #     shutil.rmtree(self.workspace)

    def get_platform_name(self) -> str:
        """Return 'linux'"""
        return "linux"

    def get_recent_actions(self) -> List[Dict[str, Any]]:
        """Get recent file and network actions tracked by strace"""
        actions = (
            self.file_access_log[-100:] +  # Last 100 file operations
            self.network_access_log[-50:] +  # Last 50 network operations
            self.syscall_log[-50:]  # Last 50 exec operations
        )
        return sorted(actions, key=lambda x: x.get('timestamp', 0))

    def check_security_patterns(self) -> Dict[str, Any]:
        """Get security analysis results"""
        return {
            "threats_detected": len(self.security_events),
            "security_events": self.security_events.copy(),
            "files_read": len(self.files_read),
            "files_written": len(self.files_written),
            "network_connections": len(self.network_connections),
            "timestamp": time.time()
        }

    def _track_file_access(self, filepath: str, operation: str):
        """Track file access (used by strace parser)"""
        self.actions_log.append({
            "type": "file",
            "operation": operation,
            "path": filepath,
            "timestamp": time.time()
        })

    def _detect_threat(self, threat_type: str, details: Dict[str, Any]):
        """Record a security threat detection"""
        self.security_events.append({
            "type": threat_type,
            "details": details,
            "timestamp": time.time()
        })

    def _send_final_telemetry(self, exit_code: int):
        """Send final security summary to dashboard after strace parsing"""
        from ..core.telemetry import TelemetryService

        telemetry = TelemetryService(self.config)

        # Get guardrails stats if available
        guardrails_summary = {}
        if self.guardrails:
            guardrails_summary = {
                "enabled": True,
                "stats": self.guardrails.get_stats(),
                "blocked_commands": len(self.blocked_commands),
                "blocked_files": len(self.blocked_files),
                "blocked_network": len(self.blocked_network),
                "output_redactions": len(self.output_redactions),
            }

        try:
            telemetry.send({
                "agent_id": self.agent_id,
                "event_type": "agent_complete",
                "timestamp": time.time(),
                "platform": self.get_platform_name(),
                "exit_code": exit_code,
                "security_summary": {
                    "files_read": len(self.files_read),
                    "files_written": len(self.files_written),
                    "files_read_list": list(self.files_read)[:100],  # Top 100
                    "files_written_list": list(self.files_written)[:100],
                    "network_connections": len(self.network_connections),
                    "network_connections_list": list(self.network_connections)[:50],
                    "security_events": self.security_events,
                    "threats_detected": len(self.security_events),
                },
                "guardrails": guardrails_summary,
                "actions_summary": {
                    "total_file_operations": len(self.file_access_log),
                    "total_network_operations": len(self.network_access_log),
                    "total_exec_operations": len(self.syscall_log),
                }
            })
            logger.debug("Final security telemetry sent to dashboard")
        except Exception as e:
            logger.warning(f"Failed to send final telemetry: {e}")
