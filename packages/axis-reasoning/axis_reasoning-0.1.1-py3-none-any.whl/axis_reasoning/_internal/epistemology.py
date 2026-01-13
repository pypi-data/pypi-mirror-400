"""Epistemology store stub for local execution."""
from typing import Any, Dict, List, Optional


class CounterStub:
    """No-op counter stub."""

    def add(self, _value: int, _attributes: Optional[Dict[str, Any]] = None) -> None:
        return None


class MeterStub:
    """No-op meter stub."""

    def create_counter(self, _name: str, description: Optional[str] = None) -> CounterStub:
        return CounterStub()


class EpistemologyStoreStub:
    """Stub implementation for EpistemologyStore protocol."""

    def record_event(self, _event_type: str, _data: Dict[str, Any]) -> None:
        return None

    def get_meter(self, _name: str) -> MeterStub:
        return MeterStub()

    def get_budget_state(self) -> Dict[str, Any]:
        return {}

    def get_remaining_budget(self, _agent_id: str) -> Optional[float]:
        return None

    def check_budget(self, _agent_id: str, _estimated_tokens: int, _priority: str) -> None:
        return None

    def get_fatigue_penalty(self, _agent_id: str) -> float:
        return 0.0

    def record_usage(self, _agent_id: str, _tokens: int, session_id: str, source: Any) -> None:
        return None

    def query_memory(self, _task_id: str) -> Optional[Dict[str, Any]]:
        return None

    def is_memory_available(self) -> bool:
        return False

    def search_memory(self, _query: str, limit: int = 3, success_only: bool = True) -> List[Dict[str, Any]]:
        return []

    def store_memory(
        self,
        agent_id: str,
        task_type: str,
        context: str,
        outcome: str,
        success: bool,
        tokens_used: int,
        metadata: Dict[str, Any],
    ) -> None:
        return None
