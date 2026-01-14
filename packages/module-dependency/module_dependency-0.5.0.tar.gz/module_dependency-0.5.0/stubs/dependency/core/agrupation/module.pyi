from dependency.core.injection.base import ContainerInjection as ContainerInjection
from dependency.core.injection.injectable import Injectable as Injectable
from dependency.core.resolution.container import Container as Container
from typing import Callable, Generator, TypeVar

MODULE = TypeVar('MODULE', bound='Module')

class Module:
    """Module Base Class

    Attributes:
        injection (ContainerInjection): Injection handler for the module
    """
    injection: ContainerInjection
    @classmethod
    def inject_container(cls, container: Container) -> None:
        """Inject the module into the application container.

        Args:
            container (Container): The application container.
        """
    @classmethod
    def resolve_providers(cls) -> Generator[Injectable, None, None]:
        """Resolve provider injections for the plugin.

        Returns:
            Generator[Injectable, None, None]: A generator of injectable providers.
        """

def module(module: type[Module] | None = None) -> Callable[[type[MODULE]], type[MODULE]]:
    """Decorator for Module class

    Args:
        module (type[Module], optional): Parent module class which this module belongs to. Defaults to None.

    Raises:
        TypeError: If the wrapped class is not a subclass of Module.

    Returns:
        Callable[[type[MODULE]], MODULE]: Decorator function that wraps the module class.
    """
