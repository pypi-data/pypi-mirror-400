"""
Abstract base class for all platform sandboxes.

This provides a common interface that all platform-specific sandbox
implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
import logging

logger = logging.getLogger(__name__)


class SandboxBase(ABC):
    """Abstract base class for all platform sandboxes"""

    def __init__(self, agent_id: str, limits: Dict[str, Any], config: Dict[str, Any]):
        """
        Initialize sandbox.

        Args:
            agent_id: Unique identifier for the agent
            limits: Resource limits (cpu_limit, memory_limit, etc.)
            config: Configuration dict (api_key, endpoint, etc.)
        """
        self.agent_id = agent_id
        self.limits = limits
        self.config = config
        self.start_time = None
        self.process = None
        self._running = False
        self._access_service = None
        self._init_access_service()

    def _init_access_service(self):
        """Initialize access control service"""
        try:
            from ..core.access import AccessService
            self._access_service = AccessService(self.config)
        except Exception as e:
            logger.debug(f"Access service init failed: {e}")
            self._access_service = None

    def check_access(
        self,
        resource_type: str,
        resource_path: str,
        action: str = "read"
    ) -> bool:
        """
        Check if access to a resource is allowed.

        Args:
            resource_type: Type of resource (file, api, command, etc.)
            resource_path: Path or identifier of the resource
            action: Action to perform (read, write, execute)

        Returns:
            True if access is allowed, False otherwise
        """
        if not self._access_service:
            return True

        result = self._access_service.check_permission(
            self.agent_id,
            resource_type,
            resource_path,
            action
        )

        allowed = result.get('allowed', True)

        # Log the access attempt
        self._access_service.log_access_async(
            self.agent_id,
            resource_type,
            resource_path,
            action,
            was_allowed=allowed,
            denial_reason=result.get('reason') if not allowed else None
        )

        if not allowed:
            logger.warning(f"Access denied: {resource_type} {resource_path} ({action})")

        return allowed

    def log_access(
        self,
        resource_type: str,
        resource_path: str,
        action: str,
        was_allowed: bool = True,
        details: Dict[str, Any] = None
    ):
        """
        Log a resource access event.

        Args:
            resource_type: Type of resource accessed
            resource_path: Path or identifier of the resource
            action: Action performed
            was_allowed: Whether access was allowed
            details: Additional details
        """
        if self._access_service:
            self._access_service.log_access_async(
                self.agent_id,
                resource_type,
                resource_path,
                action,
                was_allowed=was_allowed,
                details=details
            )

    @abstractmethod
    def setup(self):
        """
        Platform-specific sandbox setup.

        This is called before running the command. Should prepare
        the sandbox environment (namespaces, job objects, profiles, etc.)
        """
        pass

    @abstractmethod
    def run(self, command: List[str]) -> int:
        """
        Execute command in sandbox.

        Args:
            command: Command to execute as list (e.g., ['python', 'agent.py'])

        Returns:
            Exit code of the command
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current resource usage stats.

        Returns:
            Dict with resource usage: cpu_percent, memory_bytes, io_counters, etc.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Platform-specific cleanup.

        Called after the command completes or on error.
        Should clean up any resources (processes, namespaces, temp files, etc.)
        """
        pass

    def monitor_loop(self):
        """
        Shared monitoring logic (same for all platforms).

        This runs while the process is active and sends telemetry
        data to the backend dashboard.
        """
        from ..core.telemetry import TelemetryService

        telemetry = TelemetryService(self.config)

        while self._running and self.process and self.process.poll() is None:
            try:
                stats = self.get_stats()

                # Send telemetry (shared across platforms)
                telemetry.send({
                    "agent_id": self.agent_id,
                    "timestamp": time.time(),
                    "platform": self.get_platform_name(),
                    "resources": stats,
                    "actions": self.get_recent_actions(),
                    "security": self.check_security_patterns()
                })

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            time.sleep(1)  # Send telemetry every second

    @abstractmethod
    def get_platform_name(self) -> str:
        """
        Return platform identifier.

        Returns:
            One of: 'linux', 'windows', 'darwin', 'docker'
        """
        pass

    @abstractmethod
    def get_recent_actions(self) -> List[Dict[str, Any]]:
        """
        Get actions performed since last check.

        Returns:
            List of actions (file operations, network calls, API calls, etc.)
        """
        pass

    @abstractmethod
    def check_security_patterns(self) -> Dict[str, Any]:
        """
        Check for security threats.

        Returns:
            Dict with security analysis: threats_detected, patterns_blocked, etc.
        """
        pass

    def __enter__(self):
        """Context manager entry"""
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self._running = False
        self.cleanup()
        return False
