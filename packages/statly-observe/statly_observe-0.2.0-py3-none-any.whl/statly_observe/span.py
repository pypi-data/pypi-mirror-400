"""
Span module for Statly Observe SDK.

Handles distributed tracing spans.
"""

import uuid
import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SpanStatus(str, Enum):
    """Status of a span."""
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanContext:
    """Context for a span, used for hierarchy."""
    trace_id: str
    span_id: str
    parent_id: Optional[str] = None


class Span:
    """
    Represents a single operation in a trace.
    """

    def __init__(
        self,
        name: str,
        context: SpanContext,
        start_time: Optional[float] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.name = name
        self.context = context
        self.start_time = start_time or time.time()
        self.end_time: Optional[float] = None
        self.duration_ms: Optional[float] = None
        self.status = SpanStatus.OK
        self.tags = tags or {}
        self.metadata: dict[str, Any] = {}
        self._finished = False

    def finish(self, end_time: Optional[float] = None) -> None:
        """Finish the span and calculate duration."""
        if self._finished:
            return

        self.end_time = end_time or time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self._finished = True

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag on the span."""
        self.tags[key] = value

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata on the span."""
        self.metadata[key] = value

    def set_status(self, status: SpanStatus) -> None:
        """Set the status of the span."""
        self.status = status

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary for serialization."""
        return {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_id": self.context.parent_id,
            "start_time": int(self.start_time * 1000),
            "end_time": int(self.end_time * 1000) if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class TraceContext:
    """Thread-local storage for the active span."""
    _storage = threading.local()

    @classmethod
    def get_current_span(cls) -> Optional[Span]:
        """Get the active span for the current thread."""
        return getattr(cls._storage, "current_span", None)

    @classmethod
    def set_current_span(cls, span: Optional[Span]) -> None:
        """Set the active span for the current thread."""
        cls._storage.current_span = span
