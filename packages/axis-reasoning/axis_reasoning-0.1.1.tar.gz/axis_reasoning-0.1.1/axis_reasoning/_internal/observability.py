"""
Stub: Local observability logging.
Replaces: antigravity.observability.*
"""
from typing import Dict, Any
import json


def log_event(event_type: str, **metadata: Any) -> None:
    """Log observability event to console."""
    event = {"event_type": event_type, **metadata}
    print(f"[OBSERVABILITY] {json.dumps(event)}")


def observe(*_args: Any, **_kwargs: Any):
    """No-op decorator for observability spans."""
    def decorator(func):
        return func
    return decorator


class CostTrackerStub:
    """Stub cost tracker (no-op)."""

    def track_cost(self, model: str, tokens: int, cost: float) -> None:
        """No-op cost tracking."""
        pass

    def track_generation_cost(
        self,
        agent_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> float:
        """No-op cost tracking for model generations."""
        return 0.0


cost_tracker = CostTrackerStub()
