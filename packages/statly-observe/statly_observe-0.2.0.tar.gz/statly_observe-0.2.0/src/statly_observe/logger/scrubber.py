"""
Secret Scrubber
Detects and redacts sensitive data from log entries
"""

import re
from typing import Any, Callable, Optional, Set

# Redaction placeholder
REDACTED = "[REDACTED]"

# Sensitive key names (case insensitive)
SENSITIVE_KEYS: Set[str] = {
    "password", "passwd", "pwd", "secret",
    "api_key", "apikey", "api-key",
    "token", "access_token", "accesstoken", "refresh_token",
    "auth", "authorization", "bearer",
    "credential", "credentials",
    "private_key", "privatekey", "private-key",
    "secret_key", "secretkey", "secret-key",
    "session_id", "sessionid", "session-id", "session",
    "cookie", "x-api-key", "x-auth-token", "x-access-token",
}

# Built-in scrub patterns
SCRUB_PATTERNS: dict[str, re.Pattern] = {
    "apiKey": re.compile(
        r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
        re.IGNORECASE
    ),
    "password": re.compile(
        r'(?:password|passwd|pwd|secret)\s*[=:]\s*["\']?([^"\'\s]{3,})["\']?',
        re.IGNORECASE
    ),
    "token": re.compile(
        r'(?:bearer\s+|token\s*[=:]\s*["\']?)([a-zA-Z0-9_\-\.]{20,})["\']?',
        re.IGNORECASE
    ),
    "creditCard": re.compile(
        r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|'
        r'6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b'
    ),
    "ssn": re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'),
    "email": re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'),
    "ipAddress": re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    ),
    "awsKey": re.compile(r'(?:AKIA|ABIA|ACCA)[A-Z0-9]{16}'),
    "privateKey": re.compile(
        r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----[\s\S]*?'
        r'-----END (?:RSA |EC |DSA )?PRIVATE KEY-----'
    ),
    "jwt": re.compile(r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'),
}

DEFAULT_PATTERNS = ["apiKey", "password", "token", "creditCard", "ssn", "awsKey", "privateKey", "jwt"]


class Scrubber:
    """Secret scrubber for log entries"""

    def __init__(
        self,
        enabled: bool = True,
        patterns: Optional[list[str]] = None,
        custom_patterns: Optional[list[str]] = None,
        allowlist: Optional[list[str]] = None,
        custom_scrubber: Optional[Callable[[str, Any], Any]] = None,
    ):
        self.enabled = enabled
        self.allowlist = set(k.lower() for k in (allowlist or []))
        self.custom_scrubber = custom_scrubber

        # Build active patterns
        self.patterns: list[re.Pattern] = []
        pattern_names = patterns if patterns is not None else DEFAULT_PATTERNS
        for name in pattern_names:
            if name in SCRUB_PATTERNS:
                self.patterns.append(SCRUB_PATTERNS[name])

        # Add custom regex patterns
        if custom_patterns:
            for pattern in custom_patterns:
                try:
                    self.patterns.append(re.compile(pattern))
                except re.error:
                    pass  # Invalid pattern, skip

    def scrub(self, value: Any) -> Any:
        """Scrub sensitive data from a value"""
        if not self.enabled:
            return value
        return self._scrub_value(value, "")

    def scrub_message(self, message: str) -> str:
        """Scrub sensitive data from a log message"""
        if not self.enabled:
            return message

        result = message
        for pattern in self.patterns:
            result = pattern.sub(REDACTED, result)
        return result

    def _scrub_value(self, value: Any, key: str) -> Any:
        """Recursively scrub sensitive data"""
        # Check allowlist
        if key and key.lower() in self.allowlist:
            return value

        # Apply custom scrubber
        if self.custom_scrubber and key:
            result = self.custom_scrubber(key, value)
            if result is not value:
                return result

        # Check if key indicates sensitive data
        if key and self._is_sensitive_key(key):
            return REDACTED

        # Handle different types
        if value is None:
            return value

        if isinstance(value, str):
            return self._scrub_string(value)

        if isinstance(value, (list, tuple)):
            return [self._scrub_value(item, "") for item in value]

        if isinstance(value, dict):
            return {k: self._scrub_value(v, k) for k, v in value.items()}

        return value

    def _scrub_string(self, value: str) -> str:
        """Scrub patterns from a string"""
        result = value
        for pattern in self.patterns:
            result = pattern.sub(REDACTED, result)
        return result

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key name indicates sensitive data"""
        return key.lower() in SENSITIVE_KEYS

    def add_pattern(self, pattern: str) -> None:
        """Add a custom regex pattern"""
        try:
            self.patterns.append(re.compile(pattern))
        except re.error:
            pass

    def add_to_allowlist(self, key: str) -> None:
        """Add a key to the allowlist"""
        self.allowlist.add(key.lower())

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable scrubbing"""
        self.enabled = enabled
