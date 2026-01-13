"""Decision logger using internal telemetry stubs."""
import logging
import time
from typing import Dict, Any, Optional

from axis_reasoning._internal.ingestor import ingestor
from axis_reasoning._internal.schemas import EventType, ActorType, TelemetrySource

logger = logging.getLogger(__name__)


def log_decision(
    actor_id: str,
    session_id: str,
    decision_kind: str,
    metadata: Dict[str, Any],
    verdict: str,
    evidence_ref: Optional[str] = None,
    accounting_source: TelemetrySource = TelemetrySource.SDK,
) -> None:
    """Log a governance decision via the internal ingestor."""
    if not evidence_ref:
        evidence_ref = f"dec_{int(time.time()*1000)}"

    ingestor.emit(
        event_type=EventType.DECISION,
        actor_id=actor_id,
        actor_type=ActorType.SYSTEM,
        session_id=session_id,
        decision_kind=decision_kind,
        metadata=metadata,
        verdict=verdict,
        evidence_ref=evidence_ref,
        accounting_source=accounting_source,
    )

    logger.info(
        f"Decision Logged: [{decision_kind}] by {actor_id} -> {verdict}"
    )
