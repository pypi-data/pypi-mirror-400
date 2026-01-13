"""
Configuration management for SudoDog CLI.

Handles loading and saving configuration from ~/.sudodog/config.json
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager"""

    DEFAULT_CONFIG = {
        'api_key': '',
        'endpoint': 'https://api.sudodog.com/api/v1/telemetry',
        'telemetry_enabled': True,
        'use_docker': False,
        'allow_network': True,
        'allow_home': True,
        'allow_temp': True,
        'isolate_network': False,
        'isolate_mount': True,
        'log_level': 'INFO'
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config file (default: ~/.sudodog/config.json)
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default config location
            self.config_path = Path.home() / '.sudodog' / 'config.json'

        self.config = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dict
        """
        if not self.config_path.exists():
            logger.info(f"Config file not found: {self.config_path}")
            logger.info("Using default configuration")
            return self.config

        try:
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)

            # Merge with defaults
            self.config.update(user_config)

            logger.info(f"Configuration loaded from {self.config_path}")
            return self.config

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return self.config

        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.config

    def save(self) -> bool:
        """
        Save configuration to file.

        Returns:
            True if successful
        """
        try:
            # Create directory if needed
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

            logger.info(f"Configuration saved to {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Value to set

        Returns:
            True if successful
        """
        self.config[key] = value
        return self.save()

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dict.

        Returns:
            Configuration dict
        """
        return self.config.copy()

    def init(self, api_key: str = '') -> bool:
        """
        Initialize configuration (first-time setup).

        Args:
            api_key: API key for SudoDog backend

        Returns:
            True if successful
        """
        self.config['api_key'] = api_key

        # Create config directory
        config_dir = self.config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)

        # Save configuration
        success = self.save()

        if success:
            logger.info(f"SudoDog initialized at {config_dir}")

        return success

    def is_initialized(self) -> bool:
        """
        Check if SudoDog is initialized.

        Returns:
            True if config file exists
        """
        return self.config_path.exists()

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access: config['key']"""
        return self.config[key]

    def __setitem__(self, key: str, value: Any):
        """Allow dict-like assignment: config['key'] = value"""
        self.config[key] = value

    def __contains__(self, key: str) -> bool:
        """Allow 'key in config' checks"""
        return key in self.config


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration (convenience function).

    Args:
        config_path: Path to config file

    Returns:
        Configuration dict
    """
    config = Config(config_path)
    return config.to_dict()


def save_config(config_dict: Dict[str, Any], config_path: Optional[str] = None) -> bool:
    """
    Save configuration (convenience function).

    Args:
        config_dict: Configuration to save
        config_path: Path to config file

    Returns:
        True if successful
    """
    config = Config(config_path)
    config.config = config_dict
    return config.save()
