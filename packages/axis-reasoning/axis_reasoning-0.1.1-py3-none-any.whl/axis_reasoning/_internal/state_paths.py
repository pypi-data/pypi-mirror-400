"""
State path resolution with context isolation.

Provides context-aware paths for all state files, enabling
concurrent execution without race conditions.
"""
from pathlib import Path
from typing import List

from axis_reasoning._internal.config import paths
from axis_reasoning._internal.context_detector import ContextDetector


class StatePathResolver:
    """
    Resolves state file paths with context isolation.

    When context_isolation=true:
        budget_state.json -> antigravity_budget_state.json
        budget_state.json -> cli_budget_state.json

    When context_isolation=false:
        budget_state.json -> budget_state.json (shared, legacy)
    """

    def __init__(self, enable_isolation: bool = True):
        self.enable_isolation = enable_isolation
        self._prefix = ContextDetector.get_state_prefix() if enable_isolation else ""

    def get_budget_state_path(self) -> Path:
        """Returns path to budget state file."""
        filename = f"{self._prefix}budget_state.json"
        return paths.data / filename

    def get_performance_feedback_path(self) -> Path:
        """Returns path to performance feedback file."""
        filename = f"{self._prefix}performance_feedback.json"
        return paths.data / filename

    def get_semantic_cache_path(self) -> Path:
        """Returns path to semantic cache file."""
        filename = f"{self._prefix}semantic_cache.json"
        return paths.logs / filename

    def get_decision_ledger_path(self) -> Path:
        """Returns path to decision ledger file (contextual write)."""
        filename = f"{self._prefix}decision_ledger.jsonl"
        return paths.logs / filename

    def get_all_decision_ledgers(self) -> List[Path]:
        """Returns all decision ledger files for unified reading."""
        ledgers = []

        ag_ledger = paths.logs / "antigravity_decision_ledger.jsonl"
        if ag_ledger.exists():
            ledgers.append(ag_ledger)

        cli_ledger = paths.logs / "cli_decision_ledger.jsonl"
        if cli_ledger.exists():
            ledgers.append(cli_ledger)

        legacy_ledger = paths.logs / "decision_ledger.jsonl"
        if legacy_ledger.exists():
            ledgers.append(legacy_ledger)

        return ledgers

    def get_shadow_mode_log_path(self) -> Path:
        """Returns path to shadow mode log."""
        filename = f"{self._prefix}shadow_mode_log.jsonl"
        return paths.data / filename

    def list_legacy_files(self) -> List[Path]:
        """Lists legacy (unprefixed) state files for migration."""
        legacy_files = []

        legacy_candidates = [
            paths.data / "budget_state.json",
            paths.data / "performance_feedback.json",
            paths.logs / "semantic_cache.json",
            paths.logs / "decision_ledger.jsonl",
            paths.data / "shadow_mode_log.jsonl",
        ]

        for file_path in legacy_candidates:
            if file_path.exists():
                legacy_files.append(file_path)

        return legacy_files
