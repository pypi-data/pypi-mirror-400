"""
Vendored: antigravity.config.paths
Source: /Users/emilyveiga/Documents/AXIS/antigravity/config/paths.py
"""
from dataclasses import dataclass
from pathlib import Path
import os


@dataclass
class Paths:
    """Project path configuration."""

    root: Path
    data: Path
    logs: Path
    config: Path

    @classmethod
    def from_env(cls) -> "Paths":
        """Initialize paths from AXIS_ROOT environment variable."""
        root = Path(os.getenv("AXIS_ROOT", Path.cwd()))
        return cls(
            root=root,
            data=root / "data",
            logs=root / "logs",
            config=root / "config",
        )


# Global instance
paths = Paths.from_env()
