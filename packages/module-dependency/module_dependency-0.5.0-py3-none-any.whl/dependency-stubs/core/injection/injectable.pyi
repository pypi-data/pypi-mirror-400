from dependency.core.exceptions import CancelInitialization as CancelInitialization, InitializationError as InitializationError
from dependency.core.utils.lazy import LazyList as LazyList
from dependency_injector import containers as containers, providers
from typing import Any, Callable, Iterable

class Injectable:
    """Injectable Class representing a injectable dependency.
    """
    component_cls: type
    provided_cls: type
    provider_cls: type[providers.Provider[Any]]
    modules_cls: set[type]
    bootstrap: Callable[[], Any] | None
    is_resolved: bool
    def __init__(self, component_cls: type, provided_cls: type, provider_cls: type[providers.Provider[Any]] = ..., imports: Iterable['Injectable'] = (), products: Iterable['Injectable'] = (), bootstrap: Callable[[], Any] | None = None) -> None: ...
    @property
    def imports(self) -> list['Injectable']: ...
    @property
    def products(self) -> list['Injectable']: ...
    @property
    def provider(self) -> providers.Provider[Any]:
        """Return an instance from the provider."""
    @property
    def import_resolved(self) -> bool: ...
    def do_injection(self) -> Injectable:
        """Mark the injectable as resolved."""
    def do_wiring(self, container: containers.DynamicContainer) -> None:
        """Wire the provider with the given container.

        Args:
            container (containers.DynamicContainer): Container to wire the provider with.
        """
    def do_bootstrap(self) -> None:
        """Execute the bootstrap function if it exists."""
