"""
Stub: No-op telemetry decorators.
Replaces: antigravity.telemetry
"""
from typing import Callable, Any
import functools


class TelemetryEngineStub:
    """Stub telemetry engine (no-op)."""

    def track_event(self, event_name: str) -> Callable:
        """No-op decorator that returns function unchanged."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # No telemetry tracking, just execute
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def trace_span(self, span_name: str) -> Callable:
        """No-op decorator for tracing spans."""
        return self.track_event(span_name)

    def log_event(self, event_type: str, **metadata: Any) -> None:
        """No-op event logging."""
        pass


# Global instance
telemetry_engine = TelemetryEngineStub()
