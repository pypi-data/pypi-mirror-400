from typing import Any, Generic, Iterable, Optional, TypeVar

T = TypeVar('T')

class LazyList(Generic[T]):
    """Lazy List Class for deferred list evaluation.
    """
    def __init__(self, iterable: Iterable[T]) -> None:
        self._iterable = iterable
        self._list: Optional[list[T]] = None

    def __call__(self, *args: Any, **kwargs: Any) -> list[T]:
        if self._list is None:
            self._list = list(self._iterable)
        return self._list
