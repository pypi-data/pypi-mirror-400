"""
Stub: Environment-based kill switch.
Replaces: antigravity.governance.kill_switch
"""
import os


class KillSwitch:
    """Stub kill switch (checks env var)."""

    @staticmethod
    def is_active() -> bool:
        """Check if kill switch is active via AXIS_KILL_SWITCH env var."""
        return os.getenv("AXIS_KILL_SWITCH", "false").lower() == "true"

    @staticmethod
    def get_autonomous_mode() -> str:
        """Return autonomy mode (false/dry_run/true)."""
        if KillSwitch.is_active():
            return "false"
        return os.getenv("AXIS_AUTONOMY_MODE", "false").lower()

    @staticmethod
    def log_kill_switch_block(session_id: str) -> None:
        """Log a kill switch block event."""
        print(f"[KILL_SWITCH] Blocked autonomy for session {session_id}")


# Global instance
kill_switch = KillSwitch()
