import logging
from typing import Iterable
from dependency.core.injection.injectable import Injectable
from dependency.core.resolution.container import Container
from dependency.core.resolution.strategy import ResolutionStrategy
_logger = logging.getLogger("dependency.loader")

# TODO: añadir API meta con acceso al framework
class InjectionResolver:
    """Injection Resolver Class
    """
    def __init__(self,
        container: Container,
        injectables: Iterable[Injectable],
    ) -> None:
        self.container: Container = container
        self._injectables: list[Injectable] = list(injectables)

    def resolve_dependencies(self,
        strategy: ResolutionStrategy = ResolutionStrategy()
    ) -> list[Injectable]:
        """Resolve all dependencies and initialize them.

        Args:
            config (InjectionConfig): Configuration for the injection resolver.

        Returns:
            list[Injectable]: List of resolved injectables."""
        return strategy.resolution(
            container=self.container,
            injectables=self._injectables,
        )
