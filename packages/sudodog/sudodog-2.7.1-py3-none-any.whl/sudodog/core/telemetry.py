"""
Telemetry service for sending data to SudoDog backend.

Handles all communication with the dashboard backend.
Supports anonymous telemetry for users without API keys.
"""

import requests
import logging
import json
import hashlib
import platform
import socket
import os
from typing import Dict, Any, Optional
from pathlib import Path
import time

logger = logging.getLogger(__name__)


def get_anonymous_id() -> str:
    """
    Generate a consistent anonymous device ID.

    Uses SHA256 hash of machine info (hostname + platform + architecture).
    This creates a non-reversible, consistent ID per machine.

    Returns:
        Anonymous ID string like 'anon-a1b2c3d4e5f6g7h8'
    """
    try:
        # Combine machine-specific info
        machine_info = f"{socket.gethostname()}:{platform.system()}:{platform.machine()}"

        # Create SHA256 hash (non-reversible)
        hash_obj = hashlib.sha256(machine_info.encode())
        hash_hex = hash_obj.hexdigest()[:16]  # Use first 16 chars

        return f"anon-{hash_hex}"
    except Exception:
        # Fallback to random-ish ID based on process
        import uuid
        return f"anon-{uuid.uuid4().hex[:16]}"


def sanitize_path(path: str) -> str:
    """
    Sanitize file paths to remove sensitive information.

    Replaces usernames, home directories with placeholders.
    """
    if not path:
        return path

    # Replace home directory
    home = str(Path.home())
    if home in path:
        path = path.replace(home, "~")

    # Replace common username patterns
    username = os.getenv('USER') or os.getenv('USERNAME') or ''
    if username and username in path:
        path = path.replace(username, "<user>")

    return path


class TelemetryService:
    """Service for sending telemetry data to backend"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize telemetry service.

        Args:
            config: Configuration dict with api_key and endpoint
        """
        self.config = config
        self.api_key = config.get('api_key', '')
        # BUG-003 FIX: Standardize endpoint URL to match backend route
        self.endpoint = config.get('endpoint', 'https://api.sudodog.com/api/v1/telemetry')
        self.enabled = config.get('telemetry_enabled', True)
        self.session = requests.Session()

        # Generate anonymous ID for users without API key
        self.anonymous_id = get_anonymous_id()
        self.user_id = config.get('user_id') or self.api_key[:16] if self.api_key else self.anonymous_id

        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SudoDog-CLI/2.1.0',
        })

        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })

    def send(self, data: Dict[str, Any]) -> bool:
        """
        Send telemetry data to backend.

        Args:
            data: Telemetry data to send

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Telemetry disabled, skipping send")
            return False

        try:
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = time.time()

            # Ensure user_id is set (use anonymous ID if no API key)
            if 'user_id' not in data:
                data['user_id'] = self.user_id

            # Mark as anonymous if no API key
            if not self.api_key:
                data['is_anonymous'] = True

            # Send to backend
            response = self.session.post(
                self.endpoint,
                json=data,
                timeout=5  # 5 second timeout
            )

            if response.status_code in (200, 202):
                logger.debug("Telemetry sent successfully")
                return True
            else:
                logger.warning(
                    f"Telemetry send failed: {response.status_code} - {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            logger.warning("Telemetry send timed out")
            return False

        except requests.exceptions.RequestException as e:
            logger.warning(f"Telemetry send failed: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error sending telemetry: {e}")
            return False

    def send_batch(self, data_list: list) -> bool:
        """
        Send batch of telemetry data.

        Args:
            data_list: List of telemetry data dicts

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            response = self.session.post(
                f"{self.endpoint}/batch",
                json={"events": data_list},
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Batch telemetry send failed: {e}")
            return False

    def send_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Send a single event.

        Args:
            event_type: Type of event (e.g., 'agent_start', 'agent_stop')
            event_data: Event data

        Returns:
            True if successful
        """
        data = {
            "event_type": event_type,
            "data": event_data,
            "timestamp": time.time()
        }

        return self.send(data)

    def close(self):
        """Close the telemetry session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
