"""
Logger Class
Main entry point for the Statly Observe logging framework
"""

import inspect
import os
import uuid
from datetime import datetime
from typing import Any, Callable, Optional

import requests

from .types import (
    LoggerConfig,
    LogEntry,
    LogLevel,
    Destination,
    ErrorExplanation,
    FixSuggestion,
    ConsoleDestinationConfig,
    FileDestinationConfig,
    ObserveDestinationConfig,
    ScrubbingConfig,
    LEVEL_NAMES,
    LEVEL_FROM_NAME,
)
from .scrubber import Scrubber
from .destinations import ConsoleDestination, ObserveDestination, FileDestination


class Logger:
    """
    Statly Observe Logger

    A comprehensive logging framework with multi-destination output,
    secret scrubbing, sampling, and AI-powered analysis.

    Example:
        >>> from statly_observe.logger import Logger
        >>>
        >>> logger = Logger(
        ...     dsn="https://sk_live_xxx@statly.live/your-org",
        ...     logger_name="my-app",
        ...     environment="production",
        ... )
        >>>
        >>> logger.info("Application started")
        >>> logger.error("Something went wrong", {"error": "details"})
        >>>
        >>> # AI-powered analysis
        >>> explanation = await logger.explain_error(error)
    """

    def __init__(self, config: Optional[LoggerConfig] = None, **kwargs):
        """
        Initialize the logger.

        Args:
            config: Logger configuration object
            **kwargs: Alternative configuration as keyword arguments
        """
        # Build config from kwargs if not provided
        if config is None:
            config = LoggerConfig(
                dsn=kwargs.get("dsn") or os.environ.get("STATLY_DSN"),
                level=kwargs.get("level", LogLevel.DEBUG),
                logger_name=kwargs.get("logger_name", "default"),
                environment=kwargs.get("environment") or os.environ.get("STATLY_ENVIRONMENT"),
                release=kwargs.get("release"),
                console=kwargs.get("console"),
                file=kwargs.get("file"),
                observe=kwargs.get("observe"),
                scrubbing=kwargs.get("scrubbing"),
                context=kwargs.get("context"),
                tags=kwargs.get("tags"),
            )

        self.name = config.logger_name
        self.config = config
        self.min_level = config.level
        self.context: dict[str, Any] = config.context.copy() if config.context else {}
        self.tags: dict[str, str] = config.tags.copy() if config.tags else {}

        # Generate session ID
        self.session_id = str(uuid.uuid4())
        self.trace_id: Optional[str] = None
        self.span_id: Optional[str] = None

        # Initialize scrubber
        scrub_config = config.scrubbing or ScrubbingConfig()
        self.scrubber = Scrubber(
            enabled=scrub_config.enabled,
            patterns=scrub_config.patterns,
            custom_patterns=scrub_config.custom_patterns,
            allowlist=scrub_config.allowlist,
            custom_scrubber=scrub_config.custom_scrubber,
        )

        # Initialize destinations
        self.destinations: list[Destination] = []
        self._init_destinations()

    def _init_destinations(self) -> None:
        """Initialize destinations from config"""
        # Console destination (default enabled)
        console_config = self.config.console or ConsoleDestinationConfig()
        if console_config.enabled:
            self.destinations.append(ConsoleDestination(console_config))

        # File destination
        if self.config.file and self.config.file.enabled:
            self.destinations.append(FileDestination(self.config.file))

        # Observe destination (requires DSN)
        if self.config.dsn:
            observe_config = self.config.observe or ObserveDestinationConfig()
            if observe_config.enabled:
                self.destinations.append(ObserveDestination(self.config.dsn, observe_config))

    def _should_log(self, level: LogLevel) -> bool:
        """Check if a level should be logged"""
        # Audit logs are always logged
        if level == LogLevel.AUDIT:
            return True
        return level >= self.min_level

    def _get_source(self) -> Optional[dict[str, Any]]:
        """Get source location"""
        try:
            # Walk up the stack to find the caller
            frame = inspect.currentframe()
            if frame is None:
                return None

            # Skip logger internals
            for _ in range(10):
                frame = frame.f_back
                if frame is None:
                    return None

                filename = frame.f_code.co_filename
                if "logger" not in filename.lower() or "logger.py" not in filename:
                    return {
                        "file": filename,
                        "line": frame.f_lineno,
                        "function": frame.f_code.co_name,
                    }

            return None
        except Exception:
            return None

    def _create_entry(
        self,
        level: LogLevel,
        message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> LogEntry:
        """Create a log entry"""
        merged_context = {**self.context, **(context or {})}

        return LogEntry(
            level=level,
            message=self.scrubber.scrub_message(message),
            timestamp=datetime.now(),
            logger_name=self.name,
            context=self.scrubber.scrub(merged_context) if merged_context else None,
            tags=self.tags if self.tags else None,
            source=self._get_source(),
            trace_id=self.trace_id,
            span_id=self.span_id,
            session_id=self.session_id,
            environment=self.config.environment,
            release=self.config.release,
        )

    def _write(self, entry: LogEntry) -> None:
        """Write to all destinations"""
        for dest in self.destinations:
            try:
                dest.write(entry)
            except Exception as e:
                print(f"[Statly Logger] Failed to write to {dest.name}: {e}")

    # ==================== Public Logging Methods ====================

    def trace(self, message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log a trace message"""
        if not self._should_log(LogLevel.TRACE):
            return
        self._write(self._create_entry(LogLevel.TRACE, message, context))

    def debug(self, message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log a debug message"""
        if not self._should_log(LogLevel.DEBUG):
            return
        self._write(self._create_entry(LogLevel.DEBUG, message, context))

    def info(self, message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log an info message"""
        if not self._should_log(LogLevel.INFO):
            return
        self._write(self._create_entry(LogLevel.INFO, message, context))

    def warn(self, message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log a warning message"""
        if not self._should_log(LogLevel.WARN):
            return
        self._write(self._create_entry(LogLevel.WARN, message, context))

    def warning(self, message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log a warning message (alias for warn)"""
        self.warn(message, context)

    def error(
        self,
        message_or_error: str | BaseException,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an error message"""
        if not self._should_log(LogLevel.ERROR):
            return

        if isinstance(message_or_error, BaseException):
            import traceback
            ctx = {**(context or {}), "stack": traceback.format_exc(), "errorType": type(message_or_error).__name__}
            self._write(self._create_entry(LogLevel.ERROR, str(message_or_error), ctx))
        else:
            self._write(self._create_entry(LogLevel.ERROR, message_or_error, context))

    def fatal(
        self,
        message_or_error: str | BaseException,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a fatal message"""
        if not self._should_log(LogLevel.FATAL):
            return

        if isinstance(message_or_error, BaseException):
            import traceback
            ctx = {**(context or {}), "stack": traceback.format_exc(), "errorType": type(message_or_error).__name__}
            self._write(self._create_entry(LogLevel.FATAL, str(message_or_error), ctx))
        else:
            self._write(self._create_entry(LogLevel.FATAL, message_or_error, context))

    def audit(self, message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log an audit message (always logged, never sampled)"""
        self._write(self._create_entry(LogLevel.AUDIT, message, context))

    def log(
        self,
        level: LogLevel | str,
        message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log at a specific level"""
        if isinstance(level, str):
            level = LEVEL_FROM_NAME.get(level.lower(), LogLevel.INFO)

        if not self._should_log(level):
            return
        self._write(self._create_entry(level, message, context))

    # ==================== Context & Tags ====================

    def set_context(self, context: dict[str, Any]) -> None:
        """Set persistent context"""
        self.context.update(context)

    def clear_context(self) -> None:
        """Clear context"""
        self.context.clear()

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag"""
        self.tags[key] = value

    def set_tags(self, tags: dict[str, str]) -> None:
        """Set multiple tags"""
        self.tags.update(tags)

    def clear_tags(self) -> None:
        """Clear tags"""
        self.tags.clear()

    # ==================== Tracing ====================

    def set_trace_id(self, trace_id: str) -> None:
        """Set trace ID for distributed tracing"""
        self.trace_id = trace_id

    def set_span_id(self, span_id: str) -> None:
        """Set span ID"""
        self.span_id = span_id

    def clear_tracing(self) -> None:
        """Clear tracing context"""
        self.trace_id = None
        self.span_id = None

    # ==================== Child Loggers ====================

    def child(
        self,
        name: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> "Logger":
        """Create a child logger with additional context"""
        child_config = LoggerConfig(
            dsn=self.config.dsn,
            level=self.min_level,
            logger_name=name or f"{self.name}.child",
            environment=self.config.environment,
            release=self.config.release,
            context={**self.context, **(context or {})},
            tags={**self.tags, **(tags or {})},
            # Disable auto-init of destinations - we'll share parent's
            console=ConsoleDestinationConfig(enabled=False),
            observe=ObserveDestinationConfig(enabled=False),
        )

        child = Logger(child_config)
        # Share destinations with parent
        child.destinations = self.destinations
        child.trace_id = self.trace_id
        child.span_id = self.span_id
        child.session_id = self.session_id

        return child

    # ==================== AI Features ====================

    def explain_error(
        self,
        error: BaseException | str,
        api_key: Optional[str] = None,
    ) -> ErrorExplanation:
        """Explain an error using AI"""
        if not self.config.dsn:
            return ErrorExplanation(
                summary="AI features not available (no DSN configured)",
                possible_causes=[],
            )

        endpoint = self._get_ai_endpoint() + "/explain"

        if isinstance(error, BaseException):
            import traceback
            error_data = {
                "message": str(error),
                "type": type(error).__name__,
                "stack": traceback.format_exc(),
            }
        else:
            error_data = {"message": error}

        try:
            response = requests.post(
                endpoint,
                json={"error": error_data},
                headers={
                    "Content-Type": "application/json",
                    "X-Statly-DSN": self.config.dsn,
                    **({"X-AI-API-Key": api_key} if api_key else {}),
                },
                timeout=30,
            )

            if response.ok:
                data = response.json()
                return ErrorExplanation(
                    summary=data.get("summary", ""),
                    possible_causes=data.get("possibleCauses", []),
                    stack_analysis=data.get("stackAnalysis"),
                    related_docs=data.get("relatedDocs"),
                )

        except Exception as e:
            print(f"[Statly Logger] AI explain error: {e}")

        return ErrorExplanation(
            summary="Failed to get AI explanation",
            possible_causes=[],
        )

    def suggest_fix(
        self,
        error: BaseException | str,
        code: Optional[str] = None,
        file: Optional[str] = None,
        language: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> FixSuggestion:
        """Suggest fixes for an error using AI"""
        if not self.config.dsn:
            return FixSuggestion(
                summary="AI features not available (no DSN configured)",
                suggested_fixes=[],
            )

        endpoint = self._get_ai_endpoint() + "/suggest-fix"

        if isinstance(error, BaseException):
            import traceback
            error_data = {
                "message": str(error),
                "type": type(error).__name__,
                "stack": traceback.format_exc(),
            }
        else:
            error_data = {"message": error}

        context = {}
        if code:
            context["code"] = code
        if file:
            context["file"] = file
        if language:
            context["language"] = language

        try:
            response = requests.post(
                endpoint,
                json={"error": error_data, "context": context if context else None},
                headers={
                    "Content-Type": "application/json",
                    "X-Statly-DSN": self.config.dsn,
                    **({"X-AI-API-Key": api_key} if api_key else {}),
                },
                timeout=30,
            )

            if response.ok:
                data = response.json()
                return FixSuggestion(
                    summary=data.get("summary", ""),
                    suggested_fixes=data.get("suggestedFixes", []),
                    prevention_tips=data.get("preventionTips"),
                )

        except Exception as e:
            print(f"[Statly Logger] AI suggest fix error: {e}")

        return FixSuggestion(
            summary="Failed to get AI fix suggestion",
            suggested_fixes=[],
        )

    def _get_ai_endpoint(self) -> str:
        """Get AI endpoint from DSN"""
        if not self.config.dsn:
            return "https://statly.live/api/v1/logs/ai"

        from urllib.parse import urlparse
        try:
            parsed = urlparse(self.config.dsn)
            return f"{parsed.scheme}://{parsed.hostname}/api/v1/logs/ai"
        except Exception:
            return "https://statly.live/api/v1/logs/ai"

    # ==================== Destination Management ====================

    def add_destination(self, destination: Destination) -> None:
        """Add a custom destination"""
        self.destinations.append(destination)

    def remove_destination(self, name: str) -> None:
        """Remove a destination by name"""
        self.destinations = [d for d in self.destinations if d.name != name]

    def get_destinations(self) -> list[Destination]:
        """Get all destinations"""
        return list(self.destinations)

    # ==================== Level Configuration ====================

    def set_level(self, level: LogLevel | str) -> None:
        """Set minimum log level"""
        if isinstance(level, str):
            level = LEVEL_FROM_NAME.get(level.lower(), LogLevel.DEBUG)
        self.min_level = level

    def get_level(self) -> LogLevel:
        """Get current minimum level"""
        return self.min_level

    def is_level_enabled(self, level: LogLevel | str) -> bool:
        """Check if a level is enabled"""
        if isinstance(level, str):
            level = LEVEL_FROM_NAME.get(level.lower(), LogLevel.DEBUG)
        return self._should_log(level)

    # ==================== Lifecycle ====================

    def flush(self) -> None:
        """Flush all destinations"""
        for dest in self.destinations:
            try:
                dest.flush()
            except Exception as e:
                print(f"[Statly Logger] Failed to flush {dest.name}: {e}")

    def close(self) -> None:
        """Close the logger and all destinations"""
        for dest in self.destinations:
            try:
                dest.close()
            except Exception as e:
                print(f"[Statly Logger] Failed to close {dest.name}: {e}")

    def get_name(self) -> str:
        """Get logger name"""
        return self.name

    def get_session_id(self) -> str:
        """Get session ID"""
        return self.session_id

    # ==================== Context Manager ====================

    def __enter__(self) -> "Logger":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
