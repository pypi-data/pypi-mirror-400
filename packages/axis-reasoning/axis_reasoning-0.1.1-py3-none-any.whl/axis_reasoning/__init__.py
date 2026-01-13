"""
AXIS Reasoning

Internal reasoning and orchestration logic for AXIS agents.

**License:** Proprietary - Enterprise Antigravity Labs
"""

__version__ = "0.1.1"
__description__ = "AXIS Reasoning - Internal reasoning and orchestration logic"

# Core modules migrated from legacy orchestration.

try:
    from axis_reasoning.engine import Engine
    from axis_reasoning.executor import AgentExecutor
    from axis_reasoning.model_selector import ModelSelector

    __all__ = ["Engine", "AgentExecutor", "ModelSelector"]
except ImportError:
    # Modules not yet fully migrated
    __all__ = []
