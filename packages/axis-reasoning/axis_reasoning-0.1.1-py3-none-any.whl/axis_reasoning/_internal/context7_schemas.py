"""
Context7 Telemetry Schemas (vendored).
Observability for Context7 activation and shadow mode validation.
"""
from datetime import datetime, timezone
from typing import Optional, List, Literal

from pydantic import BaseModel, Field


class ShadowModeEvent(BaseModel):
    """Shadow mode validation telemetry."""

    event_type: Literal["context7_shadow_detection"] = Field(
        default="context7_shadow_detection"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    detected_use_case: Optional[str] = None
    libraries: List[str] = Field(default_factory=list)
    query_hash: str

    expected_use_case: Optional[str] = None
    correct: Optional[bool] = None
    session_id: Optional[str] = None


class Context7ActivationEvent(BaseModel):
    event_type: Literal["context7_activation"] = Field(default="context7_activation")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str

    use_case_id: Optional[str] = None
    use_case_matched: bool = False

    library: Optional[str] = None
    topic: Optional[str] = None
    cache_hit: bool = False

    fetch_status: str
    detection_latency_ms: int = 0
    cache_lookup_latency_ms: int = 0
    fetch_latency_ms: Optional[int] = None
    total_latency_ms: int = 0

    docs_tokens: int = 0
    query_tokens: int = 0
    total_tokens: int = 0

    query_hash: str

    docs_relevance: Optional[float] = None
    user_feedback: Optional[str] = None


class Context7ErrorEvent(BaseModel):
    """Error tracking for Context7 operations."""

    event_type: Literal["context7_error"] = Field(default="context7_error")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str

    error_type: str
    error_message: str
    operation: str

    use_case_id: Optional[str] = None
    library: Optional[str] = None
    retry_attempt: int = 0

    query_hash: str


def sanitize_query(query: str) -> str:
    """Sanitize query for telemetry (hash only, no PII)."""
    import hashlib

    return hashlib.sha256(query.encode()).hexdigest()[:8]
