from typing import Any, Callable, Iterable, TypeVar
from dependency_injector import providers
from dependency.core.declaration.component import Component
from dependency.core.declaration.product import Product
from dependency.core.injection.injectable import Injectable

T = TypeVar('T')

def instance(
    component: type[Component],
    imports: Iterable[type[Component]] = [],
    products: Iterable[type[Product]] = [],
    provider: type[providers.Provider[Any]] = providers.Singleton,
    bootstrap: bool = False,
) -> Callable[[type[T]], type[T]]:
    """Decorator for instance class

    Args:
        component (type[Component]): Component class to be used as a base class for the provider.
        imports (Iterable[type[Component]], optional): List of components to be imported by the provider. Defaults to ().
        products (Iterable[type[Product]], optional): List of products to be declared by the provider. Defaults to ().
        provider (type[providers.Provider[Any]], optional): Provider class to be used. Defaults to providers.Singleton.
        bootstrap (bool, optional): Whether the provider should be bootstrapped. Defaults to False.

    Raises:
        TypeError: If the wrapped class is not a subclass of Component declared base class.

    Returns:
        Callable[[type], Instance]: Decorator function that wraps the instance class and returns an Instance object.
    """
    def wrap(cls: type[T]) -> type[T]:
        if not issubclass(cls, component.interface_cls):
            raise TypeError(f"Class {cls} is not a subclass of {component.interface_cls}")

        component.injection.set_instance(
            injectable = Injectable(
                component_cls=component,
                provided_cls=cls,
                provider_cls=provider,
                imports=(
                    component.injection.injectable
                    for component in imports
                ),
                products=(
                    product.injectable
                    for product in products
                ),
                bootstrap=component.provide if bootstrap else None,
            )
        )

        return cls # type: ignore
    return wrap
