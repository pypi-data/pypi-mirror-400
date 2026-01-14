from collections import deque
from typing import Callable, Generic, Iterable, TypeVar

T = TypeVar("T")

class Cycle(Generic[T]):
    """Represents a cycle of elements.
    """
    def __init__(self, elements: Iterable[T]) -> None:
        self.elements: tuple[T, ...] = self.normalize(elements)

    @staticmethod
    def normalize(cycle: Iterable[T]) -> tuple[T, ...]:
        """Normalize the cycle to a canonical form."""
        str_cycle = [str(p) for p in cycle]
        min_idx = str_cycle.index(min(str_cycle))
        d = deque(cycle)
        d.rotate(-min_idx)
        d.append(d[0])
        return tuple(d)

    def __hash__(self) -> int:
        return hash(self.elements)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cycle):
            return False
        return self.elements == other.elements

    def __repr__(self) -> str:
        return ' -> '.join(str(p) for p in self.elements)

def find_cycles(
    function: Callable[[T], Iterable[T]],
    elements: Iterable[T], /
) -> set[Cycle[T]]:
    """Find cycles in a graph defined by the given function.

    Args:
        function (Callable[[T], Iterable[T]]): Function that returns the dependencies of an element.
        elements (Iterable[T]): Elements to check for cycles.

    Returns:
        set[Cycle[T]]: Set of detected cycles.
    """
    cycles: set[Cycle[T]] = set()

    def visit(node: T, path: list[T], visited: set[T]) -> None:
        """Visit nodes recursively to detect cycles.

        Args:
            node (T): Current node being visited.
            path (list[T]): Current path of nodes being explored.
            visited (set[T]): Set of nodes already visited.
        """
        if node in path:
            cycle_start = path.index(node)
            cycle = Cycle(path[cycle_start:])
            cycles.add(cycle)
            return
        if node in visited:
            return

        visited.add(node)
        path.append(node)
        for dep in function(node):
            visit(dep, path, visited)

    for element in elements:
        visit(element, [], set())
    return cycles
