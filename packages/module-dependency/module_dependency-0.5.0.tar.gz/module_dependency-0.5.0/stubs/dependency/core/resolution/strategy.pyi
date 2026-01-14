from dependency.core.injection.injectable import Injectable as Injectable
from dependency.core.resolution.container import Container as Container
from dependency.core.resolution.errors import raise_resolution_error as raise_resolution_error
from pydantic import BaseModel

class ResolutionConfig(BaseModel):
    """Configuration for the Resolution Strategy.
    """
    init_container: bool
    resolve_products: bool

class ResolutionStrategy:
    """Defines the strategy for resolving dependencies.
    """
    config: ResolutionConfig
    def __init__(self, config: ResolutionConfig = ...) -> None: ...
    @classmethod
    def resolution(cls, container: Container, injectables: list[Injectable]) -> list[Injectable]:
        """Resolve all dependencies and initialize them.

        Args:
            container (Container): The container to wire the injectables with.
            injectables (list[Injectable]): List of injectables to resolve.
            config (ResolutionConfig): Configuration for the resolution strategy.

        Returns:
            list[Injectable]: List of resolved injectables.
        """
    @classmethod
    def injection(cls, injectables: list[Injectable]) -> list[Injectable]:
        """Resolve all injectables in layers.

        Args:
            container (Container): The container to wire the injectables with.
            injectables (list[Injectable]): List of injectables to resolve.

        Returns:
            list[Injectable]: List of resolved injectables.
        """
    @classmethod
    def wiring(cls, container: Container, injectables: list[Injectable]) -> None:
        """Wire a list of injectables with the given container.

        Args:
            container (Container): The container to wire the injectables with.
            injectables (list[Injectable]): List of injectables to wire.
        """
    @classmethod
    def bootstrap(cls, injectables: list[Injectable]) -> None:
        """Start all implementations by executing their bootstrap functions.

        Args:
            injectables (list[Injectable]): List of injectables to start.
        """
