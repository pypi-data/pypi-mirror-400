"""
Telemetry module for Statly Observe SDK.

Provides high-level tracing and performance monitoring utilities.
"""

import functools
import uuid
import time
import inspect
from typing import Any, Callable, Optional, TypeVar, cast

from .span import Span, SpanContext, SpanStatus, TraceContext

F = TypeVar("F", bound=Callable[..., Any])


class TelemetryProvider:
    """
    Singleton provider for managing trace lifecycle.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryProvider, cls).__new__(cls)
            cls._instance._client = None
        return cls._instance

    def set_client(self, client: Any) -> None:
        """Set the Statly client for reporting spans."""
        self._client = client

    def start_span(self, name: str, tags: Optional[dict[str, str]] = None) -> Span:
        """Start a new span, linking to parent if exists."""
        parent = TraceContext.get_current_span()
        
        if parent:
            trace_id = parent.context.trace_id
            parent_id = parent.context.span_id
        else:
            trace_id = uuid.uuid4().hex
            parent_id = None

        context = SpanContext(
            trace_id=trace_id,
            span_id=uuid.uuid4().hex,
            parent_id=parent_id
        )

        span = Span(name=name, context=context, tags=tags)
        TraceContext.set_current_span(span)
        return span

    def finish_span(self, span: Span) -> None:
        """Finish the span and report it."""
        span.finish()
        
        # Pop current span from thread local (return to parent if any)
        if span.context.parent_id:
            # This is simplified - real nested tracing would need a stack
            # But for thread-local we'll just set back to parent if we can find it
            # In Phase 2 we will implement a proper Span Stack
            pass
        
        TraceContext.set_current_span(None)

        if self._client:
            self._client.capture_span(span)


def trace(name: Optional[str] = None, tags: Optional[dict[str, str]] = None) -> Callable[[F], F]:
    """
    Decorator to automatically trace a function execution.
    """
    def decorator(func: F) -> F:
        span_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            provider = TelemetryProvider()
            span = provider.start_span(span_name, tags=tags)
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                span.set_status(SpanStatus.ERROR)
                span.set_tag("error", "true")
                span.set_tag("exception.type", type(e).__name__)
                span.set_tag("exception.message", str(e))
                raise
            finally:
                provider.finish_span(span)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            provider = TelemetryProvider()
            span = provider.start_span(span_name, tags=tags)
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                span.set_status(SpanStatus.ERROR)
                span.set_tag("error", "true")
                span.set_tag("exception.type", type(e).__name__)
                span.set_tag("exception.message", str(e))
                raise
            finally:
                provider.finish_span(span)

        if inspect.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, wrapper)

    return decorator
