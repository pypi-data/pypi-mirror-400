"""
SudoDog - Cross-Platform AI Agent Monitoring & Security

Monitor, secure, and control your AI agents across Linux, Windows, and macOS.
"""

__version__ = '2.7.2'
__author__ = 'SudoDog Team'
__email__ = 'team@sudodog.com'
__url__ = 'https://sudodog.com'

from .sandbox.factory import SandboxFactory
from .core.config import Config, load_config
from .core.telemetry import TelemetryService

__all__ = [
    'SandboxFactory',
    'Config',
    'load_config',
    'TelemetryService',
]
