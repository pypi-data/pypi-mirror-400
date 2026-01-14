from typing import Any, Generic, Iterable, TypeVar

T = TypeVar('T')

class LazyList(Generic[T]):
    """Lazy List Class for deferred list evaluation.
    """
    def __init__(self, iterable: Iterable[T]) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> list[T]: ...
