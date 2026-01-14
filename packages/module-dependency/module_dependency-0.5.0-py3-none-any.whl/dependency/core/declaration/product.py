from typing import Any, Callable, Iterable, TypeVar
from dependency_injector import providers
from dependency.core.declaration.component import Component
from dependency.core.injection.injectable import Injectable

PRODUCT = TypeVar('PRODUCT', bound='Product')

class Product:
    """Product Base Class

    Attributes:
        injectable (Injectable): Injectable instance for the product
    """
    injectable: Injectable

    @classmethod
    def provide(cls, *args: Any, **kwargs: Any) -> Any:
        """Provide an instance of the product"""
        if not cls.injectable.is_resolved:
            raise RuntimeError(f"Product {cls.__name__} injectable was not resolved")
        return cls.injectable.provider(*args, **kwargs)

def product(
    imports: Iterable[type[Component]] = [],
    products: Iterable[type[Product]] = [],
    provider: type[providers.Provider[Any]] = providers.Singleton,
    bootstrap: bool = False,
) -> Callable[[type[PRODUCT]], type[PRODUCT]]:
    """Decorator for Product class

    Args:
        imports (Iterable[type[Component]], optional): List of components to be imported by the product. Defaults to [].
        products (Iterable[type[Product]], optional): List of products to be declared by the product. Defaults to [].
        provider (type[providers.Provider[Any]], optional): Provider class to be used. Defaults to providers.Singleton.

    Raises:
        TypeError: If the wrapped class is not a subclass of Product.

    Returns:
        Callable[[type[Dependent]], type[Dependent]]: Decorator function that wraps the dependent class.
    """
    def wrap(cls: type[PRODUCT]) -> type[PRODUCT]:
        if not issubclass(cls, Product):
            raise TypeError(f"Class {cls} is not a subclass of Product")

        cls.injectable = Injectable(
            component_cls=cls,
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
            bootstrap=cls.provide if bootstrap else None,
        )

        return cls
    return wrap
