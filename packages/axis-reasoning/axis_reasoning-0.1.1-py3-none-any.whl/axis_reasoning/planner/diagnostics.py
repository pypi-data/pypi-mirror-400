"""
Planner Diagnostics & Logging
Integrates with ReflectionEngine for cognitive observability.
"""
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from axis_reasoning._internal.timestamp_contract import timestamp  # Phase 9: Bucket 4 Gate 4.A

@dataclass
class PlannerEvent:
    """A single event in the Planner's reasoning chain."""
    timestamp: str
    event_type: str  # "reasoning", "action_proposed", "gateway_decision", "execution_result", "replan"
    data: Dict[str, Any]

@dataclass
class PlannerSession:
    """Tracks a complete Planner session for diagnostics."""
    session_id: str
    task: str
    events: List[PlannerEvent] = field(default_factory=list)
    reasoning_tokens_total: int = 0
    actions_proposed: int = 0
    actions_denied: int = 0
    actions_executed: int = 0
    replans: int = 0
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        self.events.append(PlannerEvent(
            timestamp=timestamp.now().isoformat(),  # Phase 9: Bucket 4 Gate 4.A
            event_type=event_type,
            data=data
        ))
        
        # Update counters
        if event_type == "action_proposed":
            self.actions_proposed += 1
        elif event_type == "gateway_decision":
            if not data.get("allowed"):
                self.actions_denied += 1
        elif event_type == "execution_result":
            self.actions_executed += 1
        elif event_type == "replan":
            self.replans += 1
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "task": self.task[:100],
            "total_events": len(self.events),
            "actions_proposed": self.actions_proposed,
            "actions_denied": self.actions_denied,
            "actions_executed": self.actions_executed,
            "replans": self.replans,
            "reasoning_tokens": self.reasoning_tokens_total
        }

class PlannerDiagnostics:
    """
    Diagnostic engine for Planner sessions.
    """
    def __init__(self):
        self.logger = logging.getLogger("antigravity.planner.diagnostics")
        self.sessions: Dict[str, PlannerSession] = {}
    
    def start_session(self, session_id: str, task: str) -> PlannerSession:
        session = PlannerSession(session_id=session_id, task=task)
        self.sessions[session_id] = session
        self.logger.info(f"📊 Started Planner session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[PlannerSession]:
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str):
        session = self.sessions.get(session_id)
        if session:
            summary = session.get_summary()
            self.logger.info(f"📊 Planner session ended: {summary}")
            return summary
        return None

# Global diagnostics instance
diagnostics = PlannerDiagnostics()
