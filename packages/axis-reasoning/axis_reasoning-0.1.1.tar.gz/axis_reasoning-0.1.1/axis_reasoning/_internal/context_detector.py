"""
Context detection for state isolation.

Detects execution context to route state files accordingly:
- antigravity: Managed execution
- cli: Direct CLI execution
"""
from enum import Enum
import os


class ExecutionContext(Enum):
    """Execution context identifier."""

    ANTIGRAVITY = "antigravity"
    CLI = "cli"


class ContextDetector:
    """
    Detects current execution context.

    Detection Strategy (precedence order):
    1. AXIS_EXECUTION_CONTEXT env var (explicit override)
    2. Stack inspection for axis_reasoning.orchestrator presence
    3. CLI markers (CLAUDE_CODE_SESSION)
    4. Safe fallback -> CLI (for isolation safety)
    """

    @staticmethod
    def detect() -> ExecutionContext:
        """Returns current execution context."""
        env_context = os.getenv("AXIS_EXECUTION_CONTEXT")
        if env_context:
            try:
                return ExecutionContext(env_context)
            except ValueError:
                pass

        import traceback

        stack = traceback.extract_stack()
        for frame in stack:
            if "axis_reasoning/orchestrator" in frame.filename:
                return ExecutionContext.ANTIGRAVITY

        if os.getenv("CLAUDE_CODE_SESSION"):
            return ExecutionContext.CLI

        return ExecutionContext.CLI

    @staticmethod
    def get_state_prefix() -> str:
        """Returns file prefix for state isolation."""
        context = ContextDetector.detect()
        return f"{context.value}_"

    @staticmethod
    def is_antigravity() -> bool:
        """Returns True if running in Antigravity context."""
        return ContextDetector.detect() == ExecutionContext.ANTIGRAVITY

    @staticmethod
    def is_cli() -> bool:
        """Returns True if running in CLI context."""
        return ContextDetector.detect() == ExecutionContext.CLI
