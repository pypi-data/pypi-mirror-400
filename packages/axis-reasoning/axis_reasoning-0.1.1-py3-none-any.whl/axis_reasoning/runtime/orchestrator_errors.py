"""Custom exceptions for the AXIS Orchestrator runtime."""


class OrchestratorError(Exception):
    """Base class for all orchestrator-related errors."""


class OrchestratorBudgetExceeded(OrchestratorError):
    """Raised when a task or daily budget is exceeded."""


class OrchestratorTimeout(OrchestratorError):
    """Raised when an orchestration task exceeds the hard timeout limit."""


class OrchestratorIntentDrift(OrchestratorError):
    """Raised when the agent's actions drift significantly from the user's intent."""


class OrchestratorReasoningSpiral(OrchestratorError):
    """Raised when the agent enters a repetitive reasoning loop."""


class OrchestratorGovernanceBlocked(OrchestratorError):
    """Raised when a task is blocked by governance rules (policy enforcement)."""
