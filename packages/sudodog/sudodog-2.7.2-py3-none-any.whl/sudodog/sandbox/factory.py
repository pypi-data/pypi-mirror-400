"""
Factory for creating platform-specific sandboxes.

Automatically detects the current platform and creates the appropriate sandbox.
"""

import platform
import logging
from typing import Dict, Any, List

from .base import SandboxBase

logger = logging.getLogger(__name__)


class SandboxFactory:
    """Factory for creating platform-specific sandboxes"""

    @staticmethod
    def create(
        agent_id: str,
        limits: Dict[str, Any],
        config: Dict[str, Any]
    ) -> SandboxBase:
        """
        Create appropriate sandbox for current platform.

        Args:
            agent_id: Unique identifier for the agent
            limits: Resource limits dict
            config: Configuration dict

        Returns:
            Platform-specific sandbox instance

        Raises:
            RuntimeError: If platform is unsupported and Docker is not available
        """
        system = platform.system()

        # Check if user explicitly requested Docker
        if config.get('use_docker', False):
            logger.info("Using Docker sandbox (explicitly requested)")
            from .docker import DockerSandbox
            return DockerSandbox(agent_id, limits, config)

        # Auto-detect platform
        if system == 'Linux':
            logger.info("Detected Linux - using namespace sandbox")
            from .linux import LinuxNamespaceSandbox
            return LinuxNamespaceSandbox(agent_id, limits, config)

        elif system == 'Windows':
            logger.info("Detected Windows - using Job Object sandbox")
            from .windows import WindowsJobObjectSandbox
            return WindowsJobObjectSandbox(agent_id, limits, config)

        elif system == 'Darwin':  # macOS
            logger.info("Detected macOS - using sandbox-exec sandbox")
            from .macos import MacOSSandboxExecSandbox
            return MacOSSandboxExecSandbox(agent_id, limits, config)

        else:
            # Unknown platform - try to fallback to Docker
            logger.warning(f"Unknown platform: {system}. Attempting Docker fallback.")
            try:
                from .docker import DockerSandbox
                return DockerSandbox(agent_id, limits, config)
            except Exception as e:
                raise RuntimeError(
                    f"Unsupported platform '{system}' and Docker fallback failed: {e}"
                )

    @staticmethod
    def get_available_platforms() -> List[str]:
        """
        Return list of supported platforms.

        Returns:
            List of platform names: ['linux', 'windows', 'darwin', 'docker']
        """
        return ['linux', 'windows', 'darwin', 'docker']

    @staticmethod
    def is_platform_supported(target_platform: str = None) -> bool:
        """
        Check if current or specified platform is supported.

        Args:
            target_platform: Platform to check (default: current platform)

        Returns:
            True if platform is supported
        """
        # BUG-012 FIX: Renamed parameter to avoid shadowing 'platform' module
        if target_platform is None:
            target_platform = platform.system()

        # Normalize to lowercase
        target_platform = target_platform.lower()

        supported = {
            'linux': True,
            'windows': True,
            'darwin': True,
            'docker': True
        }

        return supported.get(target_platform, False)

    @staticmethod
    def get_current_platform() -> str:
        """
        Get current platform name.

        Returns:
            Platform name: 'linux', 'windows', or 'darwin'
        """
        system = platform.system()
        return system.lower() if system in ['Linux', 'Windows', 'Darwin'] else 'unknown'

    @staticmethod
    def get_platform_emoji(target_platform: str = None) -> str:
        """
        Get emoji for platform.

        Args:
            target_platform: Platform name (default: current platform)

        Returns:
            Emoji representing the platform
        """
        # BUG-012 FIX: Renamed parameter to avoid shadowing 'platform' module
        if target_platform is None:
            target_platform = SandboxFactory.get_current_platform()

        emojis = {
            'linux': '🐧',
            'windows': '🪟',
            'darwin': '🍎',
            'docker': '🐳'
        }

        return emojis.get(target_platform.lower(), '💻')
