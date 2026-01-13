"""
Guardrails module for SudoDog CLI.

Provides real-time blocking and filtering for AI agent actions:
- File access blocking (prevent reads/writes to sensitive files)
- Output filtering (redact PII, secrets, credentials)
- Network firewall (block unauthorized domains)
- Command blocking (prevent dangerous commands)
"""

import re
import fnmatch
import logging
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class GuardrailAction(Enum):
    """Actions that can be taken by guardrails"""
    ALLOW = "allow"
    BLOCK = "block"
    REDACT = "redact"
    WARN = "warn"
    LOG = "log"


class ResourceType(Enum):
    """Types of resources that guardrails can protect"""
    FILE = "file"
    NETWORK = "network"
    COMMAND = "command"
    OUTPUT = "output"
    ENV = "environment"
    SECRET = "secret"


@dataclass
class GuardrailRule:
    """A single guardrail rule"""
    name: str
    resource_type: ResourceType
    pattern: str
    action: GuardrailAction
    description: str = ""
    enabled: bool = True
    priority: int = 0  # Higher priority rules are checked first


@dataclass
class GuardrailResult:
    """Result of a guardrail check"""
    allowed: bool
    action: GuardrailAction
    rule_name: Optional[str] = None
    reason: Optional[str] = None
    original_value: Optional[str] = None
    filtered_value: Optional[str] = None


@dataclass
class GuardrailPolicy:
    """Collection of guardrail rules forming a policy"""
    name: str
    description: str = ""
    rules: List[GuardrailRule] = field(default_factory=list)
    default_action: GuardrailAction = GuardrailAction.ALLOW

    def add_rule(self, rule: GuardrailRule):
        self.rules.append(rule)
        # Keep rules sorted by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)


class OutputFilter:
    """Filters sensitive data from agent output"""

    # Patterns for sensitive data detection
    PATTERNS = {
        'credit_card': {
            'pattern': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
            'replacement': '[CREDIT_CARD_REDACTED]',
            'description': 'Credit card numbers'
        },
        'ssn': {
            'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
            'replacement': '[SSN_REDACTED]',
            'description': 'Social Security Numbers'
        },
        'api_key_generic': {
            'pattern': r'\b(?:api[_-]?key|apikey|api[_-]?token)["\s:=]+["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            'replacement': r'api_key=[API_KEY_REDACTED]',
            'description': 'Generic API keys'
        },
        'aws_access_key': {
            'pattern': r'\b(AKIA[0-9A-Z]{16})\b',
            'replacement': '[AWS_ACCESS_KEY_REDACTED]',
            'description': 'AWS Access Key IDs'
        },
        'aws_secret_key': {
            'pattern': r'\b([a-zA-Z0-9+/]{40})\b',
            'replacement': '[AWS_SECRET_REDACTED]',
            'description': 'AWS Secret Access Keys (potential)'
        },
        'github_token': {
            'pattern': r'\b(ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|ghu_[a-zA-Z0-9]{36}|ghs_[a-zA-Z0-9]{36}|ghr_[a-zA-Z0-9]{36})\b',
            'replacement': '[GITHUB_TOKEN_REDACTED]',
            'description': 'GitHub tokens'
        },
        'slack_token': {
            'pattern': r'\b(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*)\b',
            'replacement': '[SLACK_TOKEN_REDACTED]',
            'description': 'Slack tokens'
        },
        'private_key': {
            'pattern': r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
            'replacement': '[PRIVATE_KEY_REDACTED]',
            'description': 'Private keys'
        },
        'password_field': {
            'pattern': r'(?:password|passwd|pwd)["\s:=]+["\']?([^\s"\']{8,})["\']?',
            'replacement': r'password=[PASSWORD_REDACTED]',
            'description': 'Password fields'
        },
        'email': {
            'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'replacement': '[EMAIL_REDACTED]',
            'description': 'Email addresses'
        },
        'phone_us': {
            'pattern': r'\b(?:\+1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'replacement': '[PHONE_REDACTED]',
            'description': 'US phone numbers'
        },
        'ip_address': {
            'pattern': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            'replacement': '[IP_REDACTED]',
            'description': 'IP addresses'
        },
        'jwt_token': {
            'pattern': r'\beyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\b',
            'replacement': '[JWT_REDACTED]',
            'description': 'JWT tokens'
        },
        'bearer_token': {
            'pattern': r'Bearer\s+[a-zA-Z0-9_\-\.]+',
            'replacement': 'Bearer [TOKEN_REDACTED]',
            'description': 'Bearer tokens'
        },
        'connection_string': {
            'pattern': r'(?:mongodb|postgres|mysql|redis|amqp):\/\/[^\s]+',
            'replacement': '[CONNECTION_STRING_REDACTED]',
            'description': 'Database connection strings'
        },
    }

    def __init__(self, enabled_filters: Optional[List[str]] = None):
        """
        Initialize output filter.

        Args:
            enabled_filters: List of filter names to enable. None means all.
        """
        self.enabled_filters = enabled_filters or list(self.PATTERNS.keys())
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for performance"""
        for name in self.enabled_filters:
            if name in self.PATTERNS:
                self._compiled_patterns[name] = re.compile(
                    self.PATTERNS[name]['pattern'],
                    re.IGNORECASE
                )

    def filter(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Filter sensitive data from text.

        Args:
            text: Text to filter

        Returns:
            Tuple of (filtered_text, list of redactions made)
        """
        if not text:
            return text, []

        redactions = []
        filtered_text = text

        for name, pattern in self._compiled_patterns.items():
            matches = pattern.findall(filtered_text)
            if matches:
                replacement = self.PATTERNS[name]['replacement']
                filtered_text = pattern.sub(replacement, filtered_text)
                redactions.append({
                    'filter': name,
                    'count': len(matches),
                    'description': self.PATTERNS[name]['description']
                })

        return filtered_text, redactions

    def contains_sensitive(self, text: str) -> List[str]:
        """
        Check if text contains sensitive data without filtering.

        Returns:
            List of filter names that matched
        """
        if not text:
            return []

        matches = []
        for name, pattern in self._compiled_patterns.items():
            if pattern.search(text):
                matches.append(name)

        return matches


class FileGuardrail:
    """Guards against unauthorized file access"""

    # Default blocked file patterns
    DEFAULT_BLOCKED_PATTERNS = [
        # Credentials and secrets
        '/etc/shadow',
        '/etc/passwd',
        '/etc/sudoers',
        '**/.ssh/*',
        '**/.gnupg/*',
        '**/.aws/credentials',
        '**/.aws/config',
        '**/.env',
        '**/.env.*',
        '**/secrets.*',
        '**/credentials.*',
        '**/*.pem',
        '**/*.key',
        '**/*.p12',
        '**/*.pfx',
        # System files
        '/etc/hosts',
        '/etc/resolv.conf',
        '/proc/*/mem',
        '/dev/mem',
        '/dev/kmem',
        # Config files with potential secrets
        '**/.netrc',
        '**/.npmrc',
        '**/.pypirc',
        '**/config.json',
        '**/settings.json',
        '**/.git/config',
    ]

    # Default allowed patterns (override blocks)
    DEFAULT_ALLOWED_PATTERNS = [
        '/tmp/*',
        '/var/tmp/*',
    ]

    def __init__(
        self,
        blocked_patterns: Optional[List[str]] = None,
        allowed_patterns: Optional[List[str]] = None,
        enable_defaults: bool = True
    ):
        """
        Initialize file guardrail.

        Args:
            blocked_patterns: Additional patterns to block
            allowed_patterns: Patterns to explicitly allow (override blocks)
            enable_defaults: Whether to use default blocked patterns
        """
        self.blocked_patterns: Set[str] = set()
        self.allowed_patterns: Set[str] = set()

        if enable_defaults:
            self.blocked_patterns.update(self.DEFAULT_BLOCKED_PATTERNS)
            self.allowed_patterns.update(self.DEFAULT_ALLOWED_PATTERNS)

        if blocked_patterns:
            self.blocked_patterns.update(blocked_patterns)
        if allowed_patterns:
            self.allowed_patterns.update(allowed_patterns)

    def check(self, file_path: str, action: str = "read") -> GuardrailResult:
        """
        Check if file access should be allowed.

        Args:
            file_path: Path to the file
            action: Action being performed (read, write, execute)

        Returns:
            GuardrailResult with allow/block decision
        """
        # Check allowed patterns first (they override blocks)
        for pattern in self.allowed_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return GuardrailResult(
                    allowed=True,
                    action=GuardrailAction.ALLOW,
                    reason=f"Explicitly allowed by pattern: {pattern}"
                )

        # Check blocked patterns
        for pattern in self.blocked_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return GuardrailResult(
                    allowed=False,
                    action=GuardrailAction.BLOCK,
                    rule_name="file_block",
                    reason=f"Blocked by pattern: {pattern}"
                )

        # Default allow
        return GuardrailResult(
            allowed=True,
            action=GuardrailAction.ALLOW,
            reason="No blocking rules matched"
        )

    def add_blocked_pattern(self, pattern: str):
        """Add a pattern to block"""
        self.blocked_patterns.add(pattern)

    def add_allowed_pattern(self, pattern: str):
        """Add a pattern to explicitly allow"""
        self.allowed_patterns.add(pattern)


class NetworkGuardrail:
    """Guards against unauthorized network access"""

    # Default blocked domains
    DEFAULT_BLOCKED_DOMAINS = [
        '*.onion',  # Tor hidden services
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '*.local',
        '169.254.*.*',  # Link-local
        '10.*.*.*',  # Private networks
        '192.168.*.*',
        '172.16.*.*',
    ]

    # Suspicious ports
    SUSPICIOUS_PORTS = {22, 23, 25, 445, 3389, 5900}  # SSH, Telnet, SMTP, SMB, RDP, VNC

    def __init__(
        self,
        blocked_domains: Optional[List[str]] = None,
        allowed_domains: Optional[List[str]] = None,
        blocked_ports: Optional[Set[int]] = None,
        enable_defaults: bool = True,
        mode: str = "blocklist"  # "blocklist" or "allowlist"
    ):
        """
        Initialize network guardrail.

        Args:
            blocked_domains: Domains to block
            allowed_domains: Domains to allow (for allowlist mode)
            blocked_ports: Ports to block
            enable_defaults: Whether to use default blocked domains
            mode: "blocklist" blocks specified, "allowlist" only allows specified
        """
        self.mode = mode
        self.blocked_domains: Set[str] = set()
        self.allowed_domains: Set[str] = set()
        self.blocked_ports: Set[int] = set()

        if enable_defaults and mode == "blocklist":
            self.blocked_domains.update(self.DEFAULT_BLOCKED_DOMAINS)
            self.blocked_ports.update(self.SUSPICIOUS_PORTS)

        if blocked_domains:
            self.blocked_domains.update(blocked_domains)
        if allowed_domains:
            self.allowed_domains.update(allowed_domains)
        if blocked_ports:
            self.blocked_ports.update(blocked_ports)

    def check(self, host: str, port: Optional[int] = None) -> GuardrailResult:
        """
        Check if network access should be allowed.

        Args:
            host: Hostname or IP address
            port: Port number (optional)

        Returns:
            GuardrailResult with allow/block decision
        """
        # Allowlist mode: only allow specified domains
        if self.mode == "allowlist":
            for pattern in self.allowed_domains:
                if fnmatch.fnmatch(host, pattern):
                    return GuardrailResult(
                        allowed=True,
                        action=GuardrailAction.ALLOW,
                        reason=f"Allowed domain: {pattern}"
                    )
            return GuardrailResult(
                allowed=False,
                action=GuardrailAction.BLOCK,
                rule_name="network_allowlist",
                reason=f"Domain not in allowlist: {host}"
            )

        # Blocklist mode: block specified domains
        for pattern in self.blocked_domains:
            if fnmatch.fnmatch(host, pattern):
                return GuardrailResult(
                    allowed=False,
                    action=GuardrailAction.BLOCK,
                    rule_name="network_block",
                    reason=f"Blocked domain: {pattern}"
                )

        # Check port
        if port and port in self.blocked_ports:
            return GuardrailResult(
                allowed=False,
                action=GuardrailAction.BLOCK,
                rule_name="port_block",
                reason=f"Blocked port: {port}"
            )

        return GuardrailResult(
            allowed=True,
            action=GuardrailAction.ALLOW,
            reason="No blocking rules matched"
        )


class CommandGuardrail:
    """Guards against dangerous command execution"""

    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        # Destructive commands
        r'rm\s+(-[rf]+\s+)?/',  # rm with root path
        r'rm\s+-rf\s+\*',  # rm -rf *
        r'mkfs\.',  # Format filesystem
        r'dd\s+.*of=/dev/',  # Direct disk write
        r'>\s*/dev/sd',  # Redirect to disk
        # System modification
        r'chmod\s+777',  # Overly permissive
        r'chmod\s+.*\s+/etc',  # Modify /etc permissions
        r'chown\s+.*\s+/',  # Change ownership of root
        # Privilege escalation
        r'sudo\s+su',
        r'sudo\s+-i',
        r'sudo\s+bash',
        # Network exfiltration
        r'curl.*\|\s*bash',  # Pipe curl to bash
        r'wget.*\|\s*bash',
        r'curl.*\|\s*sh',
        r'wget.*\|\s*sh',
        # Reverse shells
        r'nc\s+-[e]',  # Netcat with execute
        r'/dev/tcp/',  # Bash TCP
        r'bash\s+-i',  # Interactive bash (often in reverse shells)
        # Crypto mining indicators
        r'stratum\+tcp',
        r'xmrig',
        r'minerd',
        # History/log tampering
        r'history\s+-c',
        r'>\s*/var/log/',
        r'rm\s+.*\.bash_history',
        r'unset\s+HISTFILE',
    ]

    # Commands that should always be blocked
    BLOCKED_COMMANDS = {
        'shutdown', 'reboot', 'poweroff', 'halt', 'init',
        'mkfs', 'fdisk', 'parted',
        'iptables', 'firewalld', 'ufw',
        'useradd', 'userdel', 'usermod',
        'passwd',
        'visudo',
    }

    def __init__(
        self,
        additional_patterns: Optional[List[str]] = None,
        blocked_commands: Optional[Set[str]] = None,
        enable_defaults: bool = True
    ):
        """
        Initialize command guardrail.

        Args:
            additional_patterns: Additional regex patterns to block
            blocked_commands: Additional commands to block
            enable_defaults: Whether to use default patterns
        """
        self.patterns: List[re.Pattern] = []
        self.blocked_commands: Set[str] = set()

        if enable_defaults:
            for pattern in self.DANGEROUS_PATTERNS:
                self.patterns.append(re.compile(pattern, re.IGNORECASE))
            self.blocked_commands.update(self.BLOCKED_COMMANDS)

        if additional_patterns:
            for pattern in additional_patterns:
                self.patterns.append(re.compile(pattern, re.IGNORECASE))

        if blocked_commands:
            self.blocked_commands.update(blocked_commands)

    def check(self, command: str) -> GuardrailResult:
        """
        Check if command should be allowed.

        Args:
            command: Command string to check

        Returns:
            GuardrailResult with allow/block decision
        """
        if not command:
            return GuardrailResult(allowed=True, action=GuardrailAction.ALLOW)

        # Extract base command
        parts = command.strip().split()
        if not parts:
            return GuardrailResult(allowed=True, action=GuardrailAction.ALLOW)

        base_command = parts[0].split('/')[-1]  # Handle full paths

        # Check blocked commands
        if base_command in self.blocked_commands:
            return GuardrailResult(
                allowed=False,
                action=GuardrailAction.BLOCK,
                rule_name="blocked_command",
                reason=f"Blocked command: {base_command}"
            )

        # Check dangerous patterns
        for pattern in self.patterns:
            if pattern.search(command):
                return GuardrailResult(
                    allowed=False,
                    action=GuardrailAction.BLOCK,
                    rule_name="dangerous_pattern",
                    reason=f"Dangerous command pattern detected"
                )

        return GuardrailResult(
            allowed=True,
            action=GuardrailAction.ALLOW,
            reason="Command passed guardrail checks"
        )


class GuardrailEngine:
    """
    Main guardrails engine that coordinates all guardrail checks.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize guardrail engine with configuration.

        Args:
            config: Configuration dict with guardrail settings
        """
        self.config = config or {}
        self.enabled = self.config.get('guardrails_enabled', True)

        # Initialize sub-guardrails
        self.file_guardrail = FileGuardrail(
            blocked_patterns=self.config.get('file_blocked_patterns'),
            allowed_patterns=self.config.get('file_allowed_patterns'),
            enable_defaults=self.config.get('file_enable_defaults', True)
        )

        self.network_guardrail = NetworkGuardrail(
            blocked_domains=self.config.get('network_blocked_domains'),
            allowed_domains=self.config.get('network_allowed_domains'),
            mode=self.config.get('network_mode', 'blocklist'),
            enable_defaults=self.config.get('network_enable_defaults', True)
        )

        self.command_guardrail = CommandGuardrail(
            additional_patterns=self.config.get('command_patterns'),
            blocked_commands=self.config.get('blocked_commands'),
            enable_defaults=self.config.get('command_enable_defaults', True)
        )

        self.output_filter = OutputFilter(
            enabled_filters=self.config.get('output_filters')
        )

        # Statistics
        self.stats = {
            'file_checks': 0,
            'file_blocks': 0,
            'network_checks': 0,
            'network_blocks': 0,
            'command_checks': 0,
            'command_blocks': 0,
            'output_redactions': 0,
        }

        # Event log
        self.events: List[Dict[str, Any]] = []

    def check_file(self, file_path: str, action: str = "read") -> GuardrailResult:
        """Check file access"""
        if not self.enabled:
            return GuardrailResult(allowed=True, action=GuardrailAction.ALLOW)

        self.stats['file_checks'] += 1
        result = self.file_guardrail.check(file_path, action)

        if not result.allowed:
            self.stats['file_blocks'] += 1
            self._log_event('file_block', file_path, result)

        return result

    def check_network(self, host: str, port: Optional[int] = None) -> GuardrailResult:
        """Check network access"""
        if not self.enabled:
            return GuardrailResult(allowed=True, action=GuardrailAction.ALLOW)

        self.stats['network_checks'] += 1
        result = self.network_guardrail.check(host, port)

        if not result.allowed:
            self.stats['network_blocks'] += 1
            self._log_event('network_block', f"{host}:{port}", result)

        return result

    def check_command(self, command: str) -> GuardrailResult:
        """Check command execution"""
        if not self.enabled:
            return GuardrailResult(allowed=True, action=GuardrailAction.ALLOW)

        self.stats['command_checks'] += 1
        result = self.command_guardrail.check(command)

        if not result.allowed:
            self.stats['command_blocks'] += 1
            self._log_event('command_block', command, result)

        return result

    def filter_output(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Filter sensitive data from output"""
        if not self.enabled:
            return text, []

        filtered_text, redactions = self.output_filter.filter(text)

        if redactions:
            self.stats['output_redactions'] += len(redactions)
            self._log_event('output_redaction', f"{len(redactions)} items", None)

        return filtered_text, redactions

    def _log_event(self, event_type: str, target: str, result: Optional[GuardrailResult]):
        """Log a guardrail event"""
        import time
        self.events.append({
            'timestamp': time.time(),
            'type': event_type,
            'target': target,
            'reason': result.reason if result else None
        })

        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events = self.events[-1000:]

    def get_stats(self) -> Dict[str, Any]:
        """Get guardrail statistics"""
        return {
            **self.stats,
            'events_count': len(self.events)
        }

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent guardrail events"""
        return self.events[-limit:]


# Convenience function for quick guardrail checking
_default_engine: Optional[GuardrailEngine] = None

def get_guardrail_engine(config: Optional[Dict[str, Any]] = None) -> GuardrailEngine:
    """Get or create the default guardrail engine"""
    global _default_engine
    if _default_engine is None or config is not None:
        _default_engine = GuardrailEngine(config)
    return _default_engine
