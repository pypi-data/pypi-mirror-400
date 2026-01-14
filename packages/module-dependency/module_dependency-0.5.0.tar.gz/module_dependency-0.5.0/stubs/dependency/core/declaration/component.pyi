from dependency.core.agrupation.module import Module as Module
from dependency.core.exceptions import DeclarationError as DeclarationError
from dependency.core.injection.provider import ProviderInjection as ProviderInjection
from dependency_injector import providers as providers
from typing import Any, Callable, TypeVar

COMPONENT = TypeVar('COMPONENT', bound='Component')

class Component:
    """Component Base Class

    Attributes:
        injection (ProviderInjection): Injection handler for the component
        interface_cls (type): Interface class for the component
    """
    injection: ProviderInjection
    interface_cls: type
    @classmethod
    def reference(cls) -> str:
        """Return the reference name of the component."""
    @classmethod
    def provide(cls, *args: Any, **kwargs: Any) -> Any:
        """Provide an instance of the interface class"""

def component(interface: type, module: type[Module] | None = None) -> Callable[[type[COMPONENT]], type[COMPONENT]]:
    """Decorator for Component class

    Args:
        interface (type): Interface class to be used as a base class for the component.
        module (type[Module], optional): Module where the component is registered. Defaults to None.

    Raises:
        TypeError: If the wrapped class is not a subclass of Component.

    Returns:
        Callable[[type[COMPONENT]], COMPONENT]: Decorator function that wraps the component class.
    """
