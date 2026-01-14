from typing import Callable, Generic, Iterable, TypeVar

T = TypeVar('T')

class Cycle(Generic[T]):
    """Represents a cycle of elements.
    """
    elements: tuple[T, ...]
    def __init__(self, elements: Iterable[T]) -> None: ...
    @staticmethod
    def normalize(cycle: Iterable[T]) -> tuple[T, ...]:
        """Normalize the cycle to a canonical form."""
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...

def find_cycles(function: Callable[[T], Iterable[T]], elements: Iterable[T], /) -> set[Cycle[T]]:
    """Find cycles in a graph defined by the given function.

    Args:
        function (Callable[[T], Iterable[T]]): Function that returns the dependencies of an element.
        elements (Iterable[T]): Elements to check for cycles.

    Returns:
        set[Cycle[T]]: Set of detected cycles.
    """
