"""
ERX Contracts Module
Defines the data structures for the Sovereign Agent Architecture.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from axis_reasoning._internal.timestamp_contract import timestamp  # Phase 9: Bucket 4 Gate 4.A
from typing import Dict, Any, Optional, List
import uuid
import hashlib

from enum import Enum

class AuthorityLevel(str, Enum):
    L0_GOVERNANCE = "L0"   # Invariants
    L1_CANONICAL = "L1"    # Stable docs (Context7)
    L2_PROJECT = "L2"      # Architecture patterns
    L3_HISTORY = "L3"      # Session context

class EnforcementMode(str, Enum):
    OBSERVATIONAL = "OBSERVATIONAL"
    GUIDED = "GUIDED"
    STRICT = "STRICT"

class TaskPhase(str, Enum):
    ANALYSIS = "analysis"
    PLANNING = "planning"
    SOLUTIONING = "solutioning"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"

class TaskTrack(str, Enum):
    BUG_FIX = "bug_fix"
    FEATURE = "feature_track"
    ENTERPRISE = "enterprise_track"

@dataclass
class BindingProfile:
    """Configuration for how binding behaves in a specific phase."""
    allowed_authorities: List[AuthorityLevel]
    binding_mode: EnforcementMode
    creativity_budget: float # 0.0 to 1.0
    enforcement_action: str  # e.g., BLOCK_ON_DEVIATION
    exit_gate: Optional[Dict[str, Any]] = None

@dataclass
class TaskContract:
    """
    The governing contract for a specific task.
    Determined by TaskContractResolver based on BMAD track and phase.
    """
    task_id: str
    track: TaskTrack
    active_phase: TaskPhase
    binding_profile: BindingProfile
    
    # Context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata for audit
    created_at: str = field(default_factory=lambda: timestamp.now().isoformat())  # Phase 9: Bucket 4 Gate 4.A
    overrides: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class BindingContract:
    """
    A specific piece of knowledge bound to a task with authority and scope.
    """
    content: str
    authority: AuthorityLevel
    enforcement: EnforcementMode
    scope: str # Description of where this applies
    binding_strength: float # 0.0 to 1.0
    source_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SovereignAction:
    """
    Represents the Intent/Decision made by the Sovereign Agent (Planner).
    This is extracted from the LLM's tool call or structured output.
    """
    tool_name: str          # e.g., "github_ops", "shell_safe"
    action_name: str        # e.g., "create_file", "search"
    arguments: Dict[str, Any]
    reasoning: str          # Short justification for audit logs
    timestamp: str = field(default_factory=lambda: timestamp.now().isoformat())  # Phase 9: Bucket 4 Gate 4.A

@dataclass
class GatewayDecision:
    """
    Represents the verdict from the Governance Gateway (ERX).
    """
    allowed: bool
    verdict_code: str       # "APPROVED", "POLICY_BLOCK", "BUDGET_EXCEEDED", "UNKNOWN_TOOL"
    risk_score: float       # 0.0 (Safe) to 1.0 (Critical)
    reason: str             # Human readable reason
    modifications: Optional[Dict[str, Any]] = None # Sanitized arguments if modified

@dataclass
class ToolInvocation:
    """
    The normalized, safe package delivered to the ToolServer (Executor).
    """
    adapter_path: str       # e.g., "antigravity.runtime.adapters.system:SystemAdapter"
    method: str             # e.g., "execute_command"
    safe_payload: Dict[str, Any]
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    security_tier: int = 0

@dataclass
class IntentAnchor:
    """
    Intent Lock mechanism to prevent task drift.
    """
    task_id: str
    original_task: str
    task_hash: str              # SHA256 of normalized task
    intent_keywords: List[str]  # Extracted semantic anchors
    created_at: str = field(default_factory=lambda: timestamp.now().isoformat())  # Phase 9: Bucket 4 Gate 4.A
    locked: bool = True

def create_intent_anchor(task: str, task_id: str = None) -> IntentAnchor:
    """Create an IntentAnchor from a task."""
    # Generate task_id if not provided
    if task_id is None:
        task_id = str(uuid.uuid4())
    
    normalized = task.lower().strip()
    task_hash = hashlib.sha256(normalized.encode()).hexdigest()
    
    # Extract keywords (simple heuristic: words > 3 chars, exclude common words)
    stop_words = {"the", "and", "for", "with", "this", "that", "from", "about"}
    keywords = [w for w in normalized.split() if len(w) > 3 and w not in stop_words]
    
    return IntentAnchor(
        task_id=task_id,
        original_task=task,
        task_hash=task_hash,
        intent_keywords=keywords[:10]  # Top 10
    )

def check_intent_drift(action: SovereignAction, anchor: IntentAnchor) -> tuple[bool, int]:
    """
    Check if action drifts from original intent.
    Returns: (is_drift, keyword_overlap)
    """
    action_context = f"{action.tool_name} {action.action_name} {str(action.arguments)} {action.reasoning}"
    action_context = action_context.lower()
    
    overlap = sum(1 for kw in anchor.intent_keywords if kw in action_context)
    
    # High drift = 0 overlap, Low drift = 1 overlap
    is_drift = overlap == 0
    
    return is_drift, overlap

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    security_tier: int = 0
