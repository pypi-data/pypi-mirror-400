"""
Access management service for SudoDog CLI.

Handles permission checking, access logging, and access request creation
for controlled resource access by AI agents.
"""

import requests
import logging
import time
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that can be accessed"""
    FILE = "file"
    API = "api"
    DATABASE = "database"
    SECRET = "secret"
    SERVICE = "service"
    NETWORK = "network"
    COMMAND = "command"
    CUSTOM = "custom"


class PermissionLevel(Enum):
    """Permission levels for resource access"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


class AccessService:
    """Service for managing access control and logging"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize access service.

        Args:
            config: Configuration dict with api_key and endpoint
        """
        self.config = config
        self.api_key = config.get('api_key', '')
        self.base_endpoint = config.get('endpoint', 'https://api.sudodog.com/api/v1')
        self.enabled = config.get('access_control_enabled', True) and bool(self.api_key)
        self.session = requests.Session()
        self._permission_cache: Dict[str, Dict] = {}
        self._cache_ttl = 60  # Cache permissions for 60 seconds

        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SudoDog-CLI/2.1.0',
        })

        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })

    def check_permission(
        self,
        agent_id: str,
        resource_type: str,
        resource_pattern: str,
        permission_level: str = "read"
    ) -> Dict[str, Any]:
        """
        Check if an agent has permission to access a resource.

        Args:
            agent_id: The agent's ID
            resource_type: Type of resource (file, api, database, etc.)
            resource_pattern: Pattern or path of the resource
            permission_level: Required permission level (read, write, execute, admin)

        Returns:
            Dict with 'allowed' (bool), 'reason' (str), and 'permission_id' (str if found)
        """
        if not self.enabled:
            return {"allowed": True, "reason": "Access control disabled", "permission_id": None}

        # Check cache first
        cache_key = f"{agent_id}:{resource_type}:{resource_pattern}:{permission_level}"
        cached = self._get_cached_permission(cache_key)
        if cached is not None:
            return cached

        try:
            response = self.session.get(
                f"{self.base_endpoint}/access/check",
                params={
                    "agent_id": agent_id,
                    "resource_type": resource_type,
                    "resource_pattern": resource_pattern,
                    "permission_level": permission_level
                },
                timeout=2
            )

            if response.status_code == 200:
                result = response.json()
                self._cache_permission(cache_key, result)
                return result
            elif response.status_code == 403:
                result = {
                    "allowed": False,
                    "reason": "Permission denied by policy",
                    "permission_id": None
                }
                self._cache_permission(cache_key, result)
                return result
            else:
                # On error, default to allowed (fail-open for availability)
                logger.warning(f"Permission check failed: {response.status_code}")
                return {"allowed": True, "reason": "Permission check failed, defaulting to allowed", "permission_id": None}

        except requests.exceptions.Timeout:
            logger.warning("Permission check timed out, defaulting to allowed")
            return {"allowed": True, "reason": "Timeout", "permission_id": None}

        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return {"allowed": True, "reason": f"Error: {e}", "permission_id": None}

    def log_access(
        self,
        agent_id: str,
        resource_type: str,
        resource_path: str,
        action: str,
        was_allowed: bool,
        denial_reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an access attempt to the backend.

        Args:
            agent_id: The agent's ID
            resource_type: Type of resource accessed
            resource_path: Path or identifier of the resource
            action: Action performed (read, write, execute, etc.)
            was_allowed: Whether the access was allowed
            denial_reason: Reason for denial if not allowed
            details: Additional details about the access

        Returns:
            True if logged successfully
        """
        if not self.enabled:
            return False

        try:
            payload = {
                "agent_id": agent_id,
                "resource_type": resource_type,
                "resource_path": resource_path,
                "action": action,
                "was_allowed": was_allowed,
                "denial_reason": denial_reason,
                "details": details or {},
                "timestamp": time.time()
            }

            # Send async to avoid blocking
            response = self.session.post(
                f"{self.base_endpoint}/access/logs",
                json=payload,
                timeout=2
            )

            return response.status_code in (200, 201)

        except Exception as e:
            logger.debug(f"Access log failed: {e}")
            return False

    def log_access_async(
        self,
        agent_id: str,
        resource_type: str,
        resource_path: str,
        action: str,
        was_allowed: bool,
        denial_reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log access attempt asynchronously (fire and forget).
        Used during normal operation to avoid blocking.
        """
        import threading

        def _log():
            self.log_access(
                agent_id, resource_type, resource_path,
                action, was_allowed, denial_reason, details
            )

        thread = threading.Thread(target=_log, daemon=True)
        thread.start()

    def create_access_request(
        self,
        agent_id: str,
        resource_type: str,
        resource_pattern: str,
        permission_level: str,
        reason: str,
        priority: str = "medium"
    ) -> Optional[str]:
        """
        Create an access request for human approval.

        Args:
            agent_id: The agent's ID
            resource_type: Type of resource
            resource_pattern: Pattern for the resource
            permission_level: Requested permission level
            reason: Reason for the request
            priority: Priority level (low, medium, high, critical)

        Returns:
            Request ID if created, None otherwise
        """
        if not self.enabled:
            return None

        try:
            payload = {
                "agent_id": agent_id,
                "resource_type": resource_type,
                "resource_pattern": resource_pattern,
                "requested_level": permission_level,
                "reason": reason,
                "priority": priority
            }

            response = self.session.post(
                f"{self.base_endpoint}/access/requests",
                json=payload,
                timeout=5
            )

            if response.status_code in (200, 201):
                data = response.json()
                return data.get("id")
            else:
                logger.warning(f"Access request creation failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Access request creation error: {e}")
            return None

    def _get_cached_permission(self, key: str) -> Optional[Dict]:
        """Get permission from cache if still valid"""
        if key in self._permission_cache:
            cached = self._permission_cache[key]
            if time.time() - cached.get('_cached_at', 0) < self._cache_ttl:
                return cached
            else:
                del self._permission_cache[key]
        return None

    def _cache_permission(self, key: str, result: Dict):
        """Cache a permission check result"""
        result['_cached_at'] = time.time()
        self._permission_cache[key] = result

    def clear_cache(self):
        """Clear the permission cache"""
        self._permission_cache.clear()

    def close(self):
        """Close the session"""
        self.session.close()


class AccessControlledAction:
    """Context manager for access-controlled actions"""

    def __init__(
        self,
        access_service: AccessService,
        agent_id: str,
        resource_type: str,
        resource_path: str,
        action: str,
        auto_request: bool = False
    ):
        self.access_service = access_service
        self.agent_id = agent_id
        self.resource_type = resource_type
        self.resource_path = resource_path
        self.action = action
        self.auto_request = auto_request
        self.allowed = False
        self.denial_reason = None

    def __enter__(self):
        """Check permission before action"""
        result = self.access_service.check_permission(
            self.agent_id,
            self.resource_type,
            self.resource_path,
            self.action
        )

        self.allowed = result.get('allowed', True)
        self.denial_reason = result.get('reason')

        if not self.allowed:
            # Log the denied access
            self.access_service.log_access_async(
                self.agent_id,
                self.resource_type,
                self.resource_path,
                self.action,
                was_allowed=False,
                denial_reason=self.denial_reason
            )

            # Optionally create an access request
            if self.auto_request:
                self.access_service.create_access_request(
                    self.agent_id,
                    self.resource_type,
                    self.resource_path,
                    self.action,
                    reason=f"Auto-requested: Agent attempted to {self.action} {self.resource_path}"
                )

            raise PermissionError(f"Access denied: {self.denial_reason}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log successful access on exit"""
        if self.allowed and exc_type is None:
            self.access_service.log_access_async(
                self.agent_id,
                self.resource_type,
                self.resource_path,
                self.action,
                was_allowed=True
            )
        return False
