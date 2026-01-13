"""
Docker-based sandbox implementation.

Provides strong isolation using Docker containers.
Works on all platforms (Linux, Windows, macOS).
"""

import subprocess
import logging
import threading
import time
import json
import os
from typing import Dict, Any, List, Tuple

from .base import SandboxBase

logger = logging.getLogger(__name__)


class DockerSandbox(SandboxBase):
    """Docker-based sandboxing (cross-platform)"""

    def __init__(self, agent_id: str, limits: Dict[str, Any], config: Dict[str, Any]):
        super().__init__(agent_id, limits, config)
        self.container_id = None
        self.container_name = f"sudodog-{agent_id}"
        self.monitor_thread = None
        self.actions_log = []
        self.security_events = []

    def _prepare_mounts_and_command(self, command: List[str]) -> Tuple[List[str], List[str]]:
        """
        Prepare volume mounts and adjust command paths for Docker.

        Args:
            command: Original command list (e.g., ['python', '/tmp/script.py'])

        Returns:
            Tuple of (volume_args, adjusted_command)
        """
        volume_args = []
        adjusted_command = list(command)
        mounted_paths = {}  # host_path -> container_path mapping

        # Always mount current working directory as /workspace
        cwd = os.getcwd()
        volume_args.extend(['-v', f'{cwd}:/workspace:rw'])
        volume_args.extend(['-w', '/workspace'])
        mounted_paths[cwd] = '/workspace'

        # Scan command for file paths and mount them
        for i, arg in enumerate(command):
            # Skip if it's a flag or the executable itself (first arg)
            if arg.startswith('-'):
                continue

            # Check if this argument looks like a file path
            if '/' in arg or (os.path.sep in arg):
                # Resolve to absolute path
                if os.path.isabs(arg):
                    abs_path = arg
                else:
                    abs_path = os.path.abspath(arg)

                # Check if the file/directory exists
                if os.path.exists(abs_path):
                    # Check if already covered by an existing mount
                    already_mounted = False
                    for host_mount, container_mount in mounted_paths.items():
                        if abs_path.startswith(host_mount + os.sep) or abs_path == host_mount:
                            # Path is under an existing mount, adjust the path
                            rel_path = os.path.relpath(abs_path, host_mount)
                            if rel_path == '.':
                                adjusted_command[i] = container_mount
                            else:
                                adjusted_command[i] = f"{container_mount}/{rel_path}"
                            already_mounted = True
                            break

                    if not already_mounted:
                        # Need to create a new mount
                        if os.path.isfile(abs_path):
                            # Mount the parent directory
                            parent_dir = os.path.dirname(abs_path)
                            filename = os.path.basename(abs_path)
                            # Create unique mount point
                            mount_name = f"/mnt/sudodog_{len(mounted_paths)}"
                            volume_args.extend(['-v', f'{parent_dir}:{mount_name}:ro'])
                            mounted_paths[parent_dir] = mount_name
                            adjusted_command[i] = f"{mount_name}/{filename}"
                        else:
                            # It's a directory
                            mount_name = f"/mnt/sudodog_{len(mounted_paths)}"
                            volume_args.extend(['-v', f'{abs_path}:{mount_name}:ro'])
                            mounted_paths[abs_path] = mount_name
                            adjusted_command[i] = mount_name

                    logger.debug(f"Mounted {abs_path} -> {adjusted_command[i]}")

        return volume_args, adjusted_command

    def setup(self):
        """Prepare Docker environment"""
        logger.info(f"Setting up Docker sandbox for agent {self.agent_id}")

        # Check if Docker is available
        try:
            subprocess.run(
                ['docker', '--version'],
                check=True,
                capture_output=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Docker not found. Please install Docker: "
                "https://docs.docker.com/get-docker/"
            )

        # Check if Docker daemon is running
        try:
            subprocess.run(
                ['docker', 'info'],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            raise RuntimeError(
                "Docker daemon not running. Please start Docker."
            )

    def run(self, command: List[str]) -> int:
        """Execute command in Docker container"""
        self.setup()
        self._running = True

        try:
            # Build Docker run command
            docker_command = [
                'docker', 'run',
                '--rm',  # Remove container after exit
                '--name', self.container_name,
            ]

            # Add resource limits
            if 'cpu_limit' in self.limits:
                cpu_limit = self.limits['cpu_limit']
                docker_command.extend(['--cpus', str(cpu_limit)])

            if 'memory_limit' in self.limits:
                memory_limit = self.limits['memory_limit']
                docker_command.extend(['--memory', memory_limit])

            # Network isolation (optional)
            if not self.config.get('allow_network', True):
                docker_command.append('--network=none')

            # Prepare volume mounts and adjust command paths
            volume_args, adjusted_command = self._prepare_mounts_and_command(command)
            docker_command.extend(volume_args)

            logger.info(f"Volume mounts: {volume_args}")
            logger.info(f"Adjusted command: {adjusted_command}")

            # Use Python base image
            docker_command.append('python:3.11-slim')

            # Add the adjusted command to run
            docker_command.extend(adjusted_command)

            logger.info(f"Starting Docker container: {' '.join(docker_command)}")

            # Start container
            self.process = subprocess.Popen(
                docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info(f"Started Docker container: {self.container_name}")

            # Get container ID
            self._get_container_id()

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

            logger.info(f"Docker container completed with exit code {exit_code}")

            return exit_code

        except Exception as e:
            logger.error(f"Error running Docker container: {e}")
            raise

        finally:
            self._running = False
            self.cleanup()

    def _get_container_id(self):
        """Get Docker container ID"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-q', '-f', f'name={self.container_name}'],
                capture_output=True,
                text=True,
                check=True
            )
            self.container_id = result.stdout.strip()
            if self.container_id:
                logger.info(f"Container ID: {self.container_id}")
        except Exception as e:
            logger.warning(f"Could not get container ID: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get Docker container stats"""
        if not self.container_id:
            return {}

        try:
            # Get stats from Docker
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', 'json', self.container_id],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0 and result.stdout:
                # Parse JSON stats
                stats_json = json.loads(result.stdout)

                # Parse CPU percentage
                cpu_str = stats_json.get('CPUPerc', '0%').rstrip('%')
                try:
                    cpu_percent = float(cpu_str)
                except ValueError:
                    cpu_percent = 0.0

                # Parse memory
                mem_usage = stats_json.get('MemUsage', '0B / 0B').split('/')[0].strip()
                memory_bytes = self._parse_size_to_bytes(mem_usage)

                return {
                    "cpu_percent": cpu_percent,
                    "memory_bytes": memory_bytes,
                    "memory_usage": stats_json.get('MemUsage', 'N/A'),
                    "network_io": stats_json.get('NetIO', 'N/A'),
                    "block_io": stats_json.get('BlockIO', 'N/A'),
                    "pids": stats_json.get('PIDs', 0)
                }

        except Exception as e:
            logger.debug(f"Error getting Docker stats: {e}")

        return {}

    @staticmethod
    def _parse_size_to_bytes(size_str: str) -> int:
        """Parse Docker size string (e.g., '100MiB') to bytes"""
        try:
            size_str = size_str.strip()
            # Extract number and unit
            num_str = ''
            unit = ''
            for char in size_str:
                if char.isdigit() or char == '.':
                    num_str += char
                else:
                    unit += char

            value = float(num_str)
            unit = unit.strip().upper()

            multipliers = {
                'B': 1,
                'KB': 1000,
                'MB': 1000 ** 2,
                'GB': 1000 ** 3,
                'TB': 1000 ** 4,
                'KIB': 1024,
                'MIB': 1024 ** 2,
                'GIB': 1024 ** 3,
                'TIB': 1024 ** 4
            }

            return int(value * multipliers.get(unit, 1))

        except Exception:
            return 0

    def cleanup(self):
        """Clean up Docker container"""
        logger.info("Cleaning up Docker container")

        # Kill container if still running
        if self.container_name:
            try:
                subprocess.run(
                    ['docker', 'kill', self.container_name],
                    capture_output=True,
                    timeout=5
                )
                logger.info(f"Docker container {self.container_name} killed")
            except Exception:
                pass  # Container may already be stopped

            # Remove container (if not using --rm)
            try:
                subprocess.run(
                    ['docker', 'rm', '-f', self.container_name],
                    capture_output=True,
                    timeout=5
                )
                logger.info(f"Docker container {self.container_name} removed")
            except Exception:
                pass

    def get_platform_name(self) -> str:
        """Return 'docker'"""
        return "docker"

    def get_recent_actions(self) -> List[Dict[str, Any]]:
        """
        Track actions in Docker.

        For full implementation, would use:
        - Docker event stream
        - Container logs analysis
        - Network traffic inspection
        """
        actions = self.actions_log.copy()
        self.actions_log.clear()
        return actions

    def check_security_patterns(self) -> Dict[str, Any]:
        """
        Check for dangerous patterns in Docker.

        For full implementation, would check:
        - Container escape attempts
        - Privileged operations
        - Suspicious network traffic
        - Volume mount abuse
        """
        events = self.security_events.copy()
        self.security_events.clear()

        return {
            "threats_detected": len(events),
            "patterns_blocked": events,
            "timestamp": time.time()
        }
