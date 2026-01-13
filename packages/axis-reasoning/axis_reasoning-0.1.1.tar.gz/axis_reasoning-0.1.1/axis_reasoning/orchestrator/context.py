"""
Sovereign Context — Unified state object for orchestration loops.
Encapsulates optimization signals, budget, and performance metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from axis_reasoning.engine import Engine
    from axis_reasoning.planner.planner import SovereignPlanner

@dataclass
class SovereignContext:
    """
    Unified context object that flows through Engine -> Executor -> ModelSelector.
    Reduces parameter bloat and ensures signal consistency.
    """
    session_id: str
    agent_id: str
    task_description: str
    forced_model: Optional[str] = None  # Benchmark/Override flag
    
    # Optimization Signals (Signal Contract v0.1)
    recent_lucidity: Optional[float] = None  # Backward compat (deprecated - use lucidity_guarded)
    lucidity_estimate: Optional[float] = None  # Raw EMA signal (unguarded)
    lucidity_guarded: Optional[float] = None   # Governance-protected (max 10% drop/turn)
    budget_remaining: Optional[int] = None
    entropy_score: float = 0.5
    
    # Fatigue & State
    fatigue_penalty: float = 0.0
    is_dry_run: bool = False
    
    # Selection Feedback
    selected_model: Optional[str] = None
    selection_reasoning: Optional[str] = None
    
    # Tooling
    cache_id: Optional[str] = None
    system_prompt: Optional[str] = None  # Planner system prompt for caching
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_with_selection(self, model: str, reasoning: str):
        self.selected_model = model
        self.selection_reasoning = reasoning
