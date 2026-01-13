"""
Windows Job Object-based sandbox implementation.

Uses Windows Job Objects for process isolation and resource limiting.
"""

import subprocess
import logging
import threading
import time
from typing import Dict, Any, List

from .base import SandboxBase

logger = logging.getLogger(__name__)

# Windows-specific imports (only loaded on Windows)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - limited stats")

# Try to import Windows-specific modules
try:
    import win32job
    import win32process
    import win32api
    import win32con
    import pywintypes
    WINDOWS_MODULES_AVAILABLE = True
except ImportError:
    WINDOWS_MODULES_AVAILABLE = False
    logger.warning("pywin32 not available - Job Object features disabled")


class WindowsJobObjectSandbox(SandboxBase):
    """Windows Job Object-based sandboxing"""

    def __init__(self, agent_id: str, limits: Dict[str, Any], config: Dict[str, Any]):
        super().__init__(agent_id, limits, config)
        self.job = None
        self.monitor_thread = None
        self.actions_log = []
        self.security_events = []

        if not WINDOWS_MODULES_AVAILABLE:
            logger.warning(
                "Windows Job Object features unavailable. "
                "Install pywin32: pip install pywin32"
            )

    def setup(self):
        """Create Windows Job Object for isolation"""
        logger.info(f"Setting up Windows Job Object sandbox for agent {self.agent_id}")

        if not WINDOWS_MODULES_AVAILABLE:
            logger.warning("Running without Job Object isolation")
            return

        try:
            # Create job object
            self.job = win32job.CreateJobObject(None, f"SudoDog-{self.agent_id}")

            # Get current limits
            limits_info = win32job.QueryInformationJobObject(
                self.job,
                win32job.JobObjectExtendedLimitInformation
            )

            # Set CPU limit (if specified)
            if 'cpu_limit' in self.limits:
                # CPU limit in 100-nanosecond units
                cpu_seconds = float(self.limits['cpu_limit'])
                cpu_limit = int(cpu_seconds * 10_000_000)  # Convert to 100ns units
                limits_info['BasicLimitInformation']['PerProcessUserTimeLimit'] = cpu_limit
                # BUG-002 FIX: Must set the flag for CPU limit to be enforced
                limits_info['BasicLimitInformation']['LimitFlags'] |= (
                    win32job.JOB_OBJECT_LIMIT_PROCESS_TIME
                )
                logger.info(f"Set CPU limit: {cpu_seconds} seconds")

            # Set memory limit (if specified)
            if 'memory_limit' in self.limits:
                memory_bytes = self._parse_memory_limit(self.limits['memory_limit'])
                # Per-process memory limit
                limits_info['ProcessMemoryLimit'] = memory_bytes
                limits_info['BasicLimitInformation']['LimitFlags'] |= (
                    win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY
                )
                # BUG-011 FIX: Also set job-wide memory limit for total memory across all processes
                limits_info['JobMemoryLimit'] = memory_bytes
                limits_info['BasicLimitInformation']['LimitFlags'] |= (
                    win32job.JOB_OBJECT_LIMIT_JOB_MEMORY
                )
                logger.info(f"Set memory limit: {memory_bytes} bytes (per-process and job-wide)")

            # Kill all processes when job handle closes
            limits_info['BasicLimitInformation']['LimitFlags'] |= (
                win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            )

            # Apply limits
            win32job.SetInformationJobObject(
                self.job,
                win32job.JobObjectExtendedLimitInformation,
                limits_info
            )

            logger.info("Job Object created and configured successfully")

        except Exception as e:
            logger.error(f"Failed to create Job Object: {e}")
            self.job = None

    def run(self, command: List[str]) -> int:
        """Execute command in Windows Job Object"""
        self.setup()
        self._running = True
        process_handle = None

        try:
            # Start process
            logger.info(f"Starting process: {' '.join(command)}")

            # BUG-001 FIX: Start process suspended to prevent race condition
            # Process won't execute until we assign it to Job Object and resume it
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            if self.job and WINDOWS_MODULES_AVAILABLE:
                creation_flags |= win32con.CREATE_SUSPENDED

            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creation_flags
            )

            logger.info(f"Started process PID {self.process.pid}")

            # Assign to job object (if available)
            if self.job and WINDOWS_MODULES_AVAILABLE:
                try:
                    process_handle = win32api.OpenProcess(
                        win32con.PROCESS_ALL_ACCESS,
                        False,
                        self.process.pid
                    )
                    win32job.AssignProcessToJobObject(self.job, process_handle)
                    logger.info("Process assigned to Job Object")

                    # Resume the suspended process now that it's in the Job Object
                    # Get the main thread handle and resume it
                    thread_handle = win32api.OpenThread(
                        win32con.THREAD_SUSPEND_RESUME,
                        False,
                        self._get_main_thread_id(self.process.pid)
                    )
                    try:
                        win32process.ResumeThread(thread_handle)
                        logger.info("Process resumed after Job Object assignment")
                    finally:
                        win32api.CloseHandle(thread_handle)

                except Exception as e:
                    logger.warning(f"Could not assign process to Job Object: {e}")
                    # If assignment failed but process is suspended, resume it anyway
                    try:
                        thread_handle = win32api.OpenThread(
                            win32con.THREAD_SUSPEND_RESUME,
                            False,
                            self._get_main_thread_id(self.process.pid)
                        )
                        win32process.ResumeThread(thread_handle)
                        win32api.CloseHandle(thread_handle)
                    except Exception:
                        pass
                finally:
                    # BUG-004 FIX: Always close the process handle to prevent leak
                    if process_handle:
                        win32api.CloseHandle(process_handle)
                        process_handle = None

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
        """Get Windows process stats"""
        # BUG-015 FIX: Provide meaningful fallback stats instead of empty dict
        if not self.process:
            return {
                "status": "no_process",
                "error": "Process not started"
            }

        if not PSUTIL_AVAILABLE:
            # Provide basic stats using subprocess when psutil unavailable
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
        """Clean up Windows Job Object"""
        logger.info("Cleaning up Windows sandbox")

        # Kill process if still running
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        # Close job object handle
        if self.job and WINDOWS_MODULES_AVAILABLE:
            try:
                win32api.CloseHandle(self.job)
                logger.info("Job Object closed")
            except Exception as e:
                logger.error(f"Error closing Job Object: {e}")

    def get_platform_name(self) -> str:
        """Return 'windows'"""
        return "windows"

    def get_recent_actions(self) -> List[Dict[str, Any]]:
        """
        Track actions on Windows.

        For full implementation, would use:
        - Windows ETW (Event Tracing for Windows)
        - File system minifilter driver
        - Windows API hooking
        """
        actions = self.actions_log.copy()
        self.actions_log.clear()
        return actions

    def check_security_patterns(self) -> Dict[str, Any]:
        """
        Check for dangerous patterns on Windows.

        For full implementation, would check:
        - Registry modifications
        - PowerShell execution
        - Network connections to C2 servers
        - Credential theft attempts
        """
        events = self.security_events.copy()
        self.security_events.clear()

        return {
            "threats_detected": len(events),
            "patterns_blocked": events,
            "timestamp": time.time()
        }

    def _get_main_thread_id(self, pid: int) -> int:
        """
        Get the main thread ID of a process.

        Args:
            pid: Process ID

        Returns:
            Main thread ID
        """
        if PSUTIL_AVAILABLE:
            try:
                proc = psutil.Process(pid)
                threads = proc.threads()
                if threads:
                    # Return the first thread (main thread)
                    return threads[0].id
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Fallback: use Windows API to enumerate threads
        if WINDOWS_MODULES_AVAILABLE:
            try:
                import ctypes
                from ctypes import wintypes

                TH32CS_SNAPTHREAD = 0x00000004

                class THREADENTRY32(ctypes.Structure):
                    _fields_ = [
                        ('dwSize', wintypes.DWORD),
                        ('cntUsage', wintypes.DWORD),
                        ('th32ThreadID', wintypes.DWORD),
                        ('th32OwnerProcessID', wintypes.DWORD),
                        ('tpBasePri', wintypes.LONG),
                        ('tpDeltaPri', wintypes.LONG),
                        ('dwFlags', wintypes.DWORD),
                    ]

                kernel32 = ctypes.windll.kernel32
                snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)

                if snapshot != -1:
                    try:
                        te32 = THREADENTRY32()
                        te32.dwSize = ctypes.sizeof(THREADENTRY32)

                        if kernel32.Thread32First(snapshot, ctypes.byref(te32)):
                            while True:
                                if te32.th32OwnerProcessID == pid:
                                    return te32.th32ThreadID
                                if not kernel32.Thread32Next(snapshot, ctypes.byref(te32)):
                                    break
                    finally:
                        kernel32.CloseHandle(snapshot)
            except Exception as e:
                logger.warning(f"Could not get main thread ID: {e}")

        # Last resort: return pid (won't work but prevents crash)
        logger.warning(f"Could not find main thread for PID {pid}, using PID as fallback")
        return pid

    @staticmethod
    def _parse_memory_limit(limit_str: str) -> int:
        """
        Parse memory limit string (e.g., '1g', '500m') to bytes.

        Args:
            limit_str: Memory limit as string (e.g., "1g", "512m") or integer bytes

        Returns:
            Memory limit in bytes
        """
        if isinstance(limit_str, int):
            return limit_str

        limit_str = str(limit_str).lower().strip()

        # BUG-005 FIX: Handle numeric strings without suffix (treat as bytes)
        if limit_str.isdigit():
            return int(limit_str)

        # Check if last character is a valid unit
        unit = limit_str[-1]
        multipliers = {
            'b': 1,  # bytes
            'k': 1024,
            'm': 1024 * 1024,
            'g': 1024 * 1024 * 1024,
            't': 1024 * 1024 * 1024 * 1024
        }

        if unit not in multipliers:
            # No valid suffix, try to parse as number
            try:
                return int(float(limit_str))
            except ValueError:
                logger.warning(f"Invalid memory limit: {limit_str}, using 1GB default")
                return 1024 * 1024 * 1024

        # Extract number and apply multiplier
        try:
            value = float(limit_str[:-1])
        except ValueError:
            logger.warning(f"Invalid memory limit: {limit_str}, using 1GB default")
            return 1024 * 1024 * 1024

        return int(value * multipliers[unit])
