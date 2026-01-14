from dependency_injector import containers as containers, providers as providers
from dependency_injector.wiring import Closing, Modifier as Modifier, Provide, Provider
from typing import Any, Callable

class LazyWiring:
    """Base Lazy Class for deferred provider resolution.
    """
    modifier: Modifier | None
    def __init__(self, provider: Callable[[], providers.Provider[Any] | containers.Container | str], modifier: Modifier | None = None) -> None: ...
    @property
    def provider(self) -> providers.Provider[Any] | containers.Container | str:
        """Return the provider instance."""

class LazyProvide(LazyWiring, Provide):
    """Lazy Provide Class for deferred provider resolution.
    """
class LazyProvider(LazyWiring, Provider):
    """Lazy Provider Class for deferred provider resolution.
    """
class LazyClosing(LazyWiring, Closing):
    """Lazy Closing Class for deferred provider resolution.
    """
