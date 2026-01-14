from dependency.core.injection.injectable import Injectable as Injectable
from dependency.core.resolution.container import Container as Container
from dependency.core.resolution.strategy import ResolutionStrategy as ResolutionStrategy
from typing import Iterable

class InjectionResolver:
    """Injection Resolver Class
    """
    container: Container
    def __init__(self, container: Container, injectables: Iterable[Injectable]) -> None: ...
    def resolve_dependencies(self, strategy: ResolutionStrategy = ...) -> list[Injectable]:
        """Resolve all dependencies and initialize them.

        Args:
            config (InjectionConfig): Configuration for the injection resolver.

        Returns:
            list[Injectable]: List of resolved injectables."""
