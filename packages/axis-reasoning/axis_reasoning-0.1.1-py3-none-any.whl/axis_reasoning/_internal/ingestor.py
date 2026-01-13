"""
Stub: File-based telemetry ingestor.
Replaces: antigravity.telemetry.unified_ingestor
"""
from typing import Dict, Any
from pathlib import Path
import json
from datetime import datetime


class IngestorStub:
    """Stub ingestor that writes to local file."""

    def __init__(self, log_path: Path = Path("./logs/telemetry.jsonl")):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def ingest(self, event: Dict[str, Any]) -> None:
        """Write event to JSONL file (fallback to console)."""
        try:
            with open(self.log_path, "a") as f:
                event["ingested_at"] = datetime.utcnow().isoformat()
                f.write(json.dumps(event) + "\n")
        except Exception:
            # Fallback: print to console
            print(f"[TELEMETRY] {json.dumps(event)}")

    def emit(self, **event: Any) -> None:
        """Compatibility shim for ingestor.emit()."""
        self.ingest(event)


# Global instance
ingestor = IngestorStub()
