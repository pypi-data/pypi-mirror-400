from __future__ import annotations

from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from axis_reasoning.engine import Engine
    from axis_reasoning.planner.planner import SovereignPlanner

# Global context variable to store the latest routing decision ID
# used to correlate the decision with the execution outcome downstream.
_latest_decision_id: ContextVar[Optional[str]] = ContextVar("latest_decision_id", default=None)

def set_latest_decision_id(decision_id: str):
    """Set the decision_id for the current context."""
    _latest_decision_id.set(decision_id)

def get_latest_decision_id() -> Optional[str]:
    """Get the decision_id for the current context."""
    return _latest_decision_id.get()

def clear_decision_id():
    """Clear the decision_id."""
    _latest_decision_id.set(None)
