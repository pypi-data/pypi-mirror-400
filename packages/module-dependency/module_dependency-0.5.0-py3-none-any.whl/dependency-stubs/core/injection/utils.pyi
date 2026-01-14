from dependency_injector import containers as containers, providers as providers
from dependency_injector.wiring import Closing, Modifier as Modifier, Provide, Provider
from typing import Any, Callable, Generic, Iterable, TypeVar

T = TypeVar('T')

class LazyList(Generic[T]):
    """Lazy List Class for deferred list evaluation.
    """
    def __init__(self, iterable: Iterable[T]) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> list[T]: ...

class LazyWiring:
    """Base Lazy Class for deferred provider resolution.
    """
    modifier: Modifier | None
    def __init__(self, provider: Callable[[], providers.Provider[Any] | containers.Container | str], modifier: Modifier | None = None) -> None: ...
    @property
    def provider(self) -> providers.Provider[Any] | containers.Container | str: ...

class LazyProvide(LazyWiring, Provide):
    """Lazy Provide Class for deferred provider resolution.
    """
class LazyProvider(LazyWiring, Provider):
    """Lazy Provider Class for deferred provider resolution.
    """
class LazyClosing(LazyWiring, Closing):
    """Lazy Closing Class for deferred provider resolution.
    """
