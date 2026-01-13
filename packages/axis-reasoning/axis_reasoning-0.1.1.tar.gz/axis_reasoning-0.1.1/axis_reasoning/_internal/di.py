"""
Stub: Minimal dependency injection container.
Replaces: antigravity.bridge.di
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ConfigStub:
    """Default DI config with safe fallbacks."""

    authority_via_di: bool = False
    runtime_via_di: bool = False
    epistemology_via_di: bool = False
    context_isolation: bool = True


class ContainerStub:
    """Stub DI container (returns empty dict)."""

    def __init__(self):
        self._registry: Dict[str, Any] = {}
        self.config = ConfigStub()

    def get(self, key: str, default: Any = None) -> Any:
        """Get service from container."""
        return self._registry.get(key, default)

    def register(self, key: str, value: Any) -> None:
        """Register service in container."""
        self._registry[key] = value

    def resolve(self, key: str, default: Any = None) -> Any:
        """Resolve service from container."""
        return self._registry.get(key, default)


def get_container() -> ContainerStub:
    """Get global container instance."""
    global _CONTAINER
    if "_CONTAINER" not in globals():
        _CONTAINER = ContainerStub()
    return _CONTAINER
