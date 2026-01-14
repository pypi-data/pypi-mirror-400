from dependency.core.declaration.component import Component as Component
from dependency.core.injection.injectable import Injectable as Injectable
from dependency_injector import providers
from typing import Any, Callable, Iterable, TypeVar

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

def product(imports: Iterable[type[Component]] = [], products: Iterable[type[Product]] = [], provider: type[providers.Provider[Any]] = ..., bootstrap: bool = False) -> Callable[[type[PRODUCT]], type[PRODUCT]]:
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
