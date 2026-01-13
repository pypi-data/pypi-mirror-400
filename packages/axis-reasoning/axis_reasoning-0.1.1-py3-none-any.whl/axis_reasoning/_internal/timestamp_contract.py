"""
Timestamp contract v0.1.

Provides timezone-aware datetime utilities with backward compatibility
for legacy naive datetime handling.
"""
from datetime import datetime, timezone
import warnings


class TimestampContract:
    """
    Canonical timestamp provider with legacy compatibility layer.
    """

    VERSION = "0.1"

    @staticmethod
    def now() -> datetime:
        """Canonical timestamp: timezone-aware UTC datetime."""
        return datetime.now(timezone.utc)

    @staticmethod
    def to_iso(dt: datetime, legacy_compat: bool = False) -> str:
        """Convert datetime to ISO 8601 string."""
        if dt.tzinfo is None:
            if legacy_compat:
                warnings.warn(
                    f"Naive datetime encountered: {dt}. Assuming UTC (legacy compat mode).",
                    DeprecationWarning,
                    stacklevel=2,
                )
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                raise ValueError(
                    f"Naive datetime not allowed: {dt}. Use legacy_compat=True or provide timezone-aware datetime."
                )

        return dt.isoformat()

    @staticmethod
    def from_iso(iso_string: str, legacy_compat: bool = False) -> datetime:
        """Parse ISO 8601 string to datetime."""
        dt = datetime.fromisoformat(iso_string)

        if dt.tzinfo is None and legacy_compat:
            warnings.warn(
                f"Naive datetime in ISO string: {iso_string}. Assuming UTC.",
                DeprecationWarning,
                stacklevel=2,
            )
            dt = dt.replace(tzinfo=timezone.utc)

        return dt


# Canonical instance
timestamp = TimestampContract()
