"""
Vendored: antigravity.telemetry.schemas
Source: /Users/emilyveiga/Documents/AXIS/antigravity/telemetry/schemas.py
"""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class EventType(str, Enum):
    """Telemetry event types."""

    AGENT_CALL = "agent_call"
    ROUTING_DECISION = "routing_decision"
    GOVERNANCE_CHECK = "governance_check"
    COST_TRACKING = "cost_tracking"
    ERROR = "error"


class ActorType(str, Enum):
    """Actor types in the system."""

    HUMAN = "human"
    AGENT = "agent"
    SYSTEM = "system"


class TelemetrySource(str, Enum):
    """Source of telemetry data."""

    SDK = "sdk"
    CLI = "cli"
    INTERNAL = "internal"


class TelemetryEvent(BaseModel):
    """Base telemetry event."""

    event_type: EventType
    actor_type: ActorType
    source: TelemetrySource
    timestamp: datetime
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
