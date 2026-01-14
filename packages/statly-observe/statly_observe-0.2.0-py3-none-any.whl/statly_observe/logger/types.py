"""
Logger Types
Type definitions for the Statly Observe logging framework
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any, Callable, Optional, Protocol, TypedDict


class LogLevel(IntEnum):
    """Log levels - syslog compatible with extensions"""
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5
    AUDIT = 6  # Special: always logged, never sampled


# Level name mappings
LEVEL_NAMES = {
    LogLevel.TRACE: "trace",
    LogLevel.DEBUG: "debug",
    LogLevel.INFO: "info",
    LogLevel.WARN: "warn",
    LogLevel.ERROR: "error",
    LogLevel.FATAL: "fatal",
    LogLevel.AUDIT: "audit",
}

LEVEL_FROM_NAME = {v: k for k, v in LEVEL_NAMES.items()}

DEFAULT_LEVELS = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.FATAL]
EXTENDED_LEVELS = list(LogLevel)


class SourceInfo(TypedDict, total=False):
    """Source code location"""
    file: str
    line: int
    function: str


@dataclass
class LogEntry:
    """A single log entry"""
    level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    logger_name: Optional[str] = None
    context: Optional[dict[str, Any]] = None
    tags: Optional[dict[str, str]] = None
    source: Optional[SourceInfo] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    session_id: Optional[str] = None
    environment: Optional[str] = None
    release: Optional[str] = None
    sdk_name: str = "statly-observe-python"
    sdk_version: str = "0.2.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "level": LEVEL_NAMES[self.level],
            "message": self.message,
            "timestamp": int(self.timestamp.timestamp() * 1000),
            "loggerName": self.logger_name,
            "context": self.context,
            "tags": self.tags,
            "source": self.source,
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "sessionId": self.session_id,
            "environment": self.environment,
            "release": self.release,
            "sdkName": self.sdk_name,
            "sdkVersion": self.sdk_version,
        }


@dataclass
class ConsoleDestinationConfig:
    """Console destination configuration"""
    enabled: bool = True
    colors: bool = True
    format: str = "pretty"  # "pretty" or "json"
    timestamps: bool = True
    levels: Optional[list[LogLevel]] = None


@dataclass
class FileDestinationConfig:
    """File destination configuration"""
    enabled: bool = True
    path: str = "./logs/app.log"
    format: str = "json"  # "json" or "text"
    rotation_type: str = "size"  # "size" or "time"
    max_size: str = "10MB"
    max_files: int = 5
    rotation_interval: str = "daily"  # "hourly", "daily", "weekly"
    retention_days: Optional[int] = None
    compress: bool = False
    levels: Optional[list[LogLevel]] = None


@dataclass
class ObserveDestinationConfig:
    """Observe (remote) destination configuration"""
    enabled: bool = True
    batch_size: int = 50
    flush_interval: float = 5.0
    sampling: Optional[dict[LogLevel, float]] = None
    levels: Optional[list[LogLevel]] = None


@dataclass
class ScrubbingConfig:
    """Secret scrubbing configuration"""
    enabled: bool = True
    patterns: Optional[list[str]] = None  # Built-in pattern names
    custom_patterns: Optional[list[str]] = None  # Regex patterns
    allowlist: Optional[list[str]] = None  # Keys to not scrub
    custom_scrubber: Optional[Callable[[str, Any], Any]] = None


@dataclass
class LoggerConfig:
    """Logger configuration"""
    dsn: Optional[str] = None
    level: LogLevel = LogLevel.DEBUG
    logger_name: str = "default"
    environment: Optional[str] = None
    release: Optional[str] = None
    console: Optional[ConsoleDestinationConfig] = None
    file: Optional[FileDestinationConfig] = None
    observe: Optional[ObserveDestinationConfig] = None
    scrubbing: Optional[ScrubbingConfig] = None
    context: Optional[dict[str, Any]] = None
    tags: Optional[dict[str, str]] = None


class Destination(Protocol):
    """Protocol for log destinations"""
    name: str

    def write(self, entry: LogEntry) -> None:
        """Write a log entry"""
        ...

    def flush(self) -> None:
        """Flush pending writes"""
        ...

    def close(self) -> None:
        """Close the destination"""
        ...


@dataclass
class ErrorExplanation:
    """AI-powered error explanation"""
    summary: str
    possible_causes: list[str]
    stack_analysis: Optional[str] = None
    related_docs: Optional[list[str]] = None


@dataclass
class FixSuggestion:
    """AI-powered fix suggestion"""
    summary: str
    suggested_fixes: list[dict[str, Any]]
    prevention_tips: Optional[list[str]] = None
