import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from axis_reasoning._internal.config import paths
from axis_reasoning._internal.logging import log_error, log_info, log_warning


class SessionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


@dataclass
class SessionState:
    session_id: str
    task_type: str
    status: str  # created, running, completed, failed
    start_time: str
    end_time: Optional[str] = None
    agents: List[str] = None
    artifacts: List[str] = None
    metadata: Dict[str, Any] = None

    # Cognitive State (Double Ledger) [M-020]
    verified_facts: List[str] = None
    pending_investigations: List[str] = None
    current_plan_steps: List[str] = None

    # Adaptive Control [M-020]
    stall_counter: int = 0
    replan_triggers: List[str] = None
    cognitive_metrics: Dict[str, float] = None

    # Mirror Layer [M-023]
    reflection_trace: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.agents is None:
            self.agents = []
        if self.artifacts is None:
            self.artifacts = []
        if self.metadata is None:
            self.metadata = {}
        if self.verified_facts is None:
            self.verified_facts = []
        if self.pending_investigations is None:
            self.pending_investigations = []
        if self.current_plan_steps is None:
            self.current_plan_steps = []
        if self.replan_triggers is None:
            self.replan_triggers = []
        if self.cognitive_metrics is None:
            self.cognitive_metrics = {}
        if self.reflection_trace is None:
            self.reflection_trace = []


class SessionLedger:
    """
    Manages session state and persistence.
    Replaces session-ledger.sh.
    """

    def __init__(self):
        self.session_file = paths.logs / "session-ledger.yml"
        self.sessions_dir = paths.logs / "sessions"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure session directories exist."""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _get_session_path(self, session_id: str) -> Path:
        """Get path to session file."""
        return self.sessions_dir / f"{session_id}.json"

    def get_active_sessions_count(self) -> int:
        """Count number of active (running) sessions."""
        try:
            count = 0
            for session_file in self.sessions_dir.glob("sess_*.json"):
                try:
                    with open(session_file, "r") as f:
                        data = json.load(f)
                        if data.get("status") == "running":
                            count += 1
                except Exception:
                    continue
            return count
        except Exception:
            return 0

    def create_session(
        self, task_type: str, agents: List[str] = None, metadata: Dict = None
    ) -> str:
        """Create a new session."""
        session_id = f"sess_{int(time.time())}"
        timestamp = datetime.now().isoformat()

        state = SessionState(
            session_id=session_id,
            task_type=task_type,
            status="created",
            start_time=timestamp,
            agents=agents or [],
            artifacts=[],
            metadata=metadata or {},
        )

        self._save_session(state)
        log_info(f"Session created: {session_id}")
        return session_id

    def update_status(
        self, session_id: str, status: str, artifacts: List[str] = None
    ) -> bool:
        """Update session status."""
        state = self.get_session(session_id)
        if not state:
            log_error(f"Session not found: {session_id}")
            return False

        state.status = status
        if artifacts:
            state.artifacts.extend(artifacts)

        if status in ["completed", "failed"]:
            state.end_time = datetime.now().isoformat()

        self._save_session(state)
        return True

    def update_cognitive_state(
        self,
        session_id: str,
        facts: List[str] = None,
        plan: List[str] = None,
        investigations: List[str] = None,
        metrics: Dict[str, float] = None,
        stall_increment: int = 0,
        reflection_event: Dict[str, Any] = None,
    ) -> bool:
        """Update cognitive state of the session [M-020]."""
        state = self.get_session(session_id)
        if not state:
            return False

        if facts:
            state.verified_facts.extend(facts)
        if plan:
            state.current_plan_steps = plan  # Overwrite plan usually
        if investigations:
            state.pending_investigations = investigations
        if metrics:
            state.cognitive_metrics.update(metrics)
        if reflection_event:
            state.reflection_trace.append(reflection_event)

        state.stall_counter += stall_increment

        self._save_session(state)
        return True

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve session state."""
        path = self._get_session_path(session_id)
        if not path.exists():
            return None

        try:
            with open(path, "r") as f:
                data = json.load(f)
            return SessionState(**data)
        except Exception as e:
            log_error(f"Failed to load session {session_id}: {e}")
            return None

    def _save_session(self, state: SessionState):
        """Persist session state."""
        path = self._get_session_path(state.session_id)
        try:
            with open(path, "w") as f:
                json.dump(asdict(state), f, indent=2, cls=SessionEncoder)
        except Exception as e:
            log_error(f"Failed to save session {state.session_id}: {e}")


# Global instance
ledger = SessionLedger()
