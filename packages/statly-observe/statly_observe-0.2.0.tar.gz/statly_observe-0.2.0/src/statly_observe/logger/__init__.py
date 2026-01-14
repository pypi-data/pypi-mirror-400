"""
Statly Observe Logger

A comprehensive logging framework with multi-destination output,
secret scrubbing, sampling, and AI-powered analysis.

Example:
    >>> from statly_observe.logger import Logger
    >>>
    >>> # Create a logger with default settings
    >>> logger = Logger(
    ...     dsn="https://sk_live_xxx@statly.live/your-org",
    ...     logger_name="my-app",
    ...     environment="production",
    ...     release="1.0.0",
    ... )
    >>>
    >>> # Basic logging
    >>> logger.info("Application started")
    >>> logger.debug("Processing request", {"request_id": "123"})
    >>> logger.warn("Deprecated API used", {"endpoint": "/old-api"})
    >>> logger.error("Failed to process", {"error": "timeout"})
    >>>
    >>> # Log with Exception
    >>> try:
    ...     risky_operation()
    ... except Exception as e:
    ...     logger.error(e)
    >>>
    >>> # Audit logging (always logged, never sampled)
    >>> logger.audit("User login", {"user_id": "123", "ip": "10.0.0.1"})
    >>>
    >>> # AI-powered analysis
    >>> explanation = logger.explain_error(error)
    >>> fix = logger.suggest_fix(error)
    >>>
    >>> # Child loggers
    >>> request_logger = logger.child(
    ...     name="request",
    ...     context={"request_id": "456"},
    ... )
    >>> request_logger.info("Handling request")
    >>>
    >>> # Configure destinations
    >>> logger.add_destination(my_custom_destination)
    >>>
    >>> # Cleanup
    >>> logger.close()
"""

from .logger import Logger
from .scrubber import Scrubber, SENSITIVE_KEYS, SCRUB_PATTERNS, REDACTED
from .destinations import ConsoleDestination, ObserveDestination, FileDestination
from .types import (
    LogLevel,
    LogEntry,
    LoggerConfig,
    Destination,
    ConsoleDestinationConfig,
    FileDestinationConfig,
    ObserveDestinationConfig,
    ScrubbingConfig,
    ErrorExplanation,
    FixSuggestion,
    LEVEL_NAMES,
    LEVEL_FROM_NAME,
    DEFAULT_LEVELS,
    EXTENDED_LEVELS,
)

__all__ = [
    # Main class
    "Logger",
    # Destinations
    "ConsoleDestination",
    "ObserveDestination",
    "FileDestination",
    # Scrubbing
    "Scrubber",
    "SENSITIVE_KEYS",
    "SCRUB_PATTERNS",
    "REDACTED",
    # Types
    "LogLevel",
    "LogEntry",
    "LoggerConfig",
    "Destination",
    "ConsoleDestinationConfig",
    "FileDestinationConfig",
    "ObserveDestinationConfig",
    "ScrubbingConfig",
    "ErrorExplanation",
    "FixSuggestion",
    # Constants
    "LEVEL_NAMES",
    "LEVEL_FROM_NAME",
    "DEFAULT_LEVELS",
    "EXTENDED_LEVELS",
]

# Default logger instance
_default_logger: Logger | None = None


def get_default_logger() -> Logger:
    """Get or create the default logger instance"""
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger()
    return _default_logger


def set_default_logger(logger: Logger) -> None:
    """Set the default logger instance"""
    global _default_logger
    _default_logger = logger


# Convenience functions using default logger
def trace(message: str, context: dict | None = None) -> None:
    """Log a trace message using the default logger"""
    get_default_logger().trace(message, context)


def debug(message: str, context: dict | None = None) -> None:
    """Log a debug message using the default logger"""
    get_default_logger().debug(message, context)


def info(message: str, context: dict | None = None) -> None:
    """Log an info message using the default logger"""
    get_default_logger().info(message, context)


def warn(message: str, context: dict | None = None) -> None:
    """Log a warning message using the default logger"""
    get_default_logger().warn(message, context)


def warning(message: str, context: dict | None = None) -> None:
    """Log a warning message using the default logger (alias)"""
    get_default_logger().warning(message, context)


def error(message_or_error: str | BaseException, context: dict | None = None) -> None:
    """Log an error message using the default logger"""
    get_default_logger().error(message_or_error, context)


def fatal(message_or_error: str | BaseException, context: dict | None = None) -> None:
    """Log a fatal message using the default logger"""
    get_default_logger().fatal(message_or_error, context)


def audit(message: str, context: dict | None = None) -> None:
    """Log an audit message using the default logger"""
    get_default_logger().audit(message, context)
