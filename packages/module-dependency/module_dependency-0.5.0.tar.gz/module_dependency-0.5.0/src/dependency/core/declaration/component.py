import logging
from typing import Any, Callable, Optional, TypeVar
from dependency_injector import providers
from dependency.core.agrupation.module import Module
from dependency.core.injection.provider import ProviderInjection
from dependency.core.exceptions import DeclarationError
_logger = logging.getLogger("dependency.loader")

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
        return cls.injection.reference

    @classmethod
    def provide(cls, *args: Any, **kwargs: Any) -> Any:
        """Provide an instance of the interface class"""
        if not cls.injection.injectable.is_resolved:
            raise DeclarationError(f"Component {cls.__name__} injectable was not resolved")
        return cls.injection.injectable.provider(*args, **kwargs)

def component(
    interface: type,
    module: Optional[type[Module]] = None,
) -> Callable[[type[COMPONENT]], type[COMPONENT]]:
    """Decorator for Component class

    Args:
        interface (type): Interface class to be used as a base class for the component.
        module (type[Module], optional): Module where the component is registered. Defaults to None.

    Raises:
        TypeError: If the wrapped class is not a subclass of Component.

    Returns:
        Callable[[type[COMPONENT]], COMPONENT]: Decorator function that wraps the component class.
    """
    def wrap(cls: type[COMPONENT]) -> type[COMPONENT]:
        if not issubclass(cls, Component):
            raise TypeError(f"Class {cls} is not a subclass of Component")

        if module is None:
            _logger.warning(f"Component {cls.__name__} is not registered to any module")

        cls.injection = ProviderInjection(
            name=cls.__name__,
            parent=module.injection if module else None,
        )
        cls.interface_cls = interface

        return cls
    return wrap
