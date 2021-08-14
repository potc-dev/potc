from queue import Queue
from typing import TypeVar, Collection, Tuple, List

_ElementType = TypeVar('_ElementType')


def topological(n: int, edges: Collection[Tuple[int, int]]) -> List[int]:
    """
    Overview:
        Topological sort with nodes count and edges.

    Arguments:
        - n (:obj:`int`): Count of nodes.
        - edges (:obj:`Collection[Tuple[int, int]]`): Collection of edges, \
            in each tuple (x, y), means x should be earlier appeared than y in the final sequence.

    Returns:
        - sequence (:obj:`List[int]`): Sorted sequence.

    Example:
        >>> topological(3, [])                        # [0, 1, 2]
        >>> topological(3, [(0, 1), (2, 1)])          # [0, 2, 1]
        >>> topological(3, [(0, 1), (2, 1), (1, 0)])  # ArithmeticError
    """
    if n == 0:
        return []

    towards = [0] * n
    goings = [set() for _ in range(n)]
    for from_, to_, in list(set(edges)):
        assert from_ in range(n)
        assert to_ in range(n)
        towards[to_] += 1
        goings[from_].add(to_)

    queue = Queue()
    visited = []
    for i in range(n):
        if towards[i] == 0:
            queue.put(i)
            visited.append(i)

    while not queue.empty():
        head = queue.get()
        for to_ in goings[head]:
            towards[to_] -= 1
            if towards[to_] == 0:
                queue.put(to_)
                visited.append(to_)

    if len(visited) < n:
        missing = tuple(sorted(set(range(n)) - set(visited)))
        raise ArithmeticError(f'Invalid top graph for some node ids not accessible - {repr(missing)}.')

    return visited
