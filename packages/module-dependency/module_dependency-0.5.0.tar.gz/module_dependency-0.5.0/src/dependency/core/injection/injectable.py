import logging
from typing import Any, Callable, Iterable, Optional
from dependency_injector import containers, providers
from dependency.core.exceptions import InitializationError, CancelInitialization
from dependency.core.utils.lazy import LazyList
_logger = logging.getLogger("dependency.loader")

# TODO: Añadir soporte para otros providers (Abstract Factory, Aggregate, Selector)
class Injectable:
    """Injectable Class representing a injectable dependency.
    """
    def __init__(self,
        component_cls: type,
        provided_cls: type,
        provider_cls: type[providers.Provider[Any]] = providers.Singleton,
        imports: Iterable['Injectable'] = (),
        products: Iterable['Injectable'] = (),
        bootstrap: Optional[Callable[[], Any]] = None
    ) -> None:
        self.component_cls: type = component_cls
        self.provided_cls: type = provided_cls
        self.provider_cls: type[providers.Provider[Any]] = provider_cls
        self.modules_cls: set[type] = {component_cls, provided_cls}
        self.bootstrap: Optional[Callable[[], Any]] = bootstrap

        self._imports: LazyList['Injectable'] = LazyList(imports)
        self._products: LazyList['Injectable'] = LazyList(products)
        self._provider: Optional[providers.Provider[Any]] = None
        self.is_resolved: bool = False

    @property
    def imports(self) -> list['Injectable']:
        return self._imports()

    @property
    def products(self) -> list['Injectable']:
        return self._products()

    @property
    # TODO: Necesito extraer esta definición de provider
    def provider(self) -> providers.Provider[Any]:
        """Return an instance from the provider."""
        if self._provider is None:
            self._provider = self.provider_cls(self.provided_cls) # type: ignore
        return self._provider

    @property
    def import_resolved(self) -> bool:
        return all(
            implementation.is_resolved
            for implementation in self.imports
        )

    def do_injection(self) -> "Injectable":
        """Mark the injectable as resolved."""
        self.is_resolved = True
        return self

    def do_wiring(self, container: containers.DynamicContainer) -> None:
        """Wire the provider with the given container.

        Args:
            container (containers.DynamicContainer): Container to wire the provider with.
        """
        container.wire(
            modules=self.modules_cls,
            warn_unresolved=True
        )

    def do_bootstrap(self) -> None:
        """Execute the bootstrap function if it exists."""
        if not self.is_resolved:
            raise InitializationError(f"Component {self.component_cls.__name__} cannot be initialized before being resolved.")
        if self.bootstrap is not None:
            try:
                self.bootstrap()
            except CancelInitialization as e:
                _logger.warning(f"Initialization of Component {self.component_cls.__name__} was cancelled: {e}")
            except Exception as e:
                raise InitializationError(f"Failed to initialize Component {self.component_cls.__name__}") from e

    def __repr__(self) -> str:
        return f"{self.provided_cls.__name__}"
