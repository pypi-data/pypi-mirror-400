import logging
from pydantic import BaseModel
from dependency.core.injection.injectable import Injectable
from dependency.core.resolution.container import Container
from dependency.core.resolution.errors import raise_resolution_error
_logger = logging.getLogger("dependency.loader")

class ResolutionConfig(BaseModel):
    """Configuration for the Resolution Strategy.
    """
    init_container: bool = True
    resolve_products: bool = True

class ResolutionStrategy:
    """Defines the strategy for resolving dependencies.
    """
    config: ResolutionConfig = ResolutionConfig()

    def __init__(self,
        config: ResolutionConfig = ResolutionConfig()
    ) -> None:
        self.config = config

    @classmethod
    def resolution(cls,
        container: Container,
        injectables: list[Injectable],
    ) -> list[Injectable]:
        """Resolve all dependencies and initialize them.

        Args:
            container (Container): The container to wire the injectables with.
            injectables (list[Injectable]): List of injectables to resolve.
            config (ResolutionConfig): Configuration for the resolution strategy.

        Returns:
            list[Injectable]: List of resolved injectables.
        """
        injectables = cls.injection(
            injectables=injectables,
        )
        cls.wiring(
            container=container,
            injectables=injectables,
        )
        cls.bootstrap(
            injectables=injectables
        )
        return injectables

    @classmethod
    def injection(cls,
        injectables: list[Injectable],
    ) -> list[Injectable]:
        """Resolve all injectables in layers.

        Args:
            container (Container): The container to wire the injectables with.
            injectables (list[Injectable]): List of injectables to resolve.

        Returns:
            list[Injectable]: List of resolved injectables.
        """
        _logger.info("Resolving injectables...")
        unresolved: list[Injectable] = injectables.copy()
        resolved: list[Injectable] = []

        while unresolved:
            new_layer = [
                injectable.do_injection()
                for injectable in unresolved
                if injectable.import_resolved
            ]

            if len(new_layer) == 0:
                raise_resolution_error(
                    injectables=injectables,
                    unresolved=unresolved
                )
            resolved.extend(new_layer)
            _logger.debug(f"Layer: {new_layer}")

            if cls.config.resolve_products:
                for injectable in new_layer:
                    unresolved.extend(injectable.products)

            unresolved = [
                injectable
                for injectable in unresolved
                if not injectable.is_resolved
            ]
        return resolved

    @classmethod
    def wiring(cls,
        container: Container,
        injectables: list[Injectable],
    ) -> None:
        """Wire a list of injectables with the given container.

        Args:
            container (Container): The container to wire the injectables with.
            injectables (list[Injectable]): List of injectables to wire.
        """
        _logger.info("Wiring injectables...")
        for injectable in injectables:
            injectable.do_wiring(container=container)
        if cls.config.init_container:
            container.check_dependencies()
            container.init_resources()

    @classmethod
    def bootstrap(cls,
        injectables: list[Injectable],
    ) -> None:
        """Start all implementations by executing their bootstrap functions.

        Args:
            injectables (list[Injectable]): List of injectables to start.
        """
        _logger.info("Starting injectables...")
        for injectable in injectables:
            injectable.do_bootstrap()
