
"""
This module re-exports selected functions and classes from the standard
libraries `bisect`, `heapq`, and `collections`, along with some custom
algorithmic utilities.
It provides a unified interface for common algorithmic operations.
Functions included:
- binary_search: Perform binary search on a sorted array.
- top_k_elements: Get the top k largest elements from an iterable.
- sliding_window: Generate a sliding window of a specified size over an iterable.
"""

from bisect import bisect_left
from heapq import nlargest
from collections import deque
from typing import List, Tuple, Any, Iterable, Deque, Callable

def binary_search(arr: List[Any], target: Any) -> int:
    """
    Perform binary search on a sorted array.
    :param arr: A sorted list of elements.
    :param target: The element to search for.
    :return: The index of the target element if found, otherwise -1.
    """

    index = bisect_left(arr, target)
    if index != len(arr) and arr[index] == target:
        return index
    return -1

def top_k_elements(iterable: Iterable[Any], k: int) -> List[Any]:
    """
    Get the top k largest elements from an iterable.
    :param iterable: An iterable of elements.
    :param k: The number of top elements to retrieve.
    :return: A list of the top k largest elements.
    """

    return nlargest(k, iterable)

def sliding_window(iterable: Iterable[Any], window_size: int) -> Iterable[Tuple[Any, ...]]:
    """
    Generate a sliding window of a specified size over an iterable.
    :param iterable: An iterable of elements.
    :param window_size: The size of the sliding window.
    :return: An iterable of tuples representing the sliding windows.
    """

    if window_size <= 0:
        raise ValueError("window_size must be > 0")

    it = iter(iterable)
    window: Deque[Any] = deque(maxlen=window_size)

    try:
        for _ in range(window_size):
            window.append(next(it))
    except StopIteration:
        # Not enough elements for a full window: yield nothing
        return

    yield tuple(window)

    for elem in it:
        window.append(elem)
        yield tuple(window)

def sort(num: Iterable[Any]) -> Iterable[Any]:
    """
    Sort for a Iterable
    :param num: A function of sorting.
    :type num: Iterable[Any]
    :return: An Iterable of sorting.
    :rtype: Iterable[Any]
    """
    return sorted(num)

def exec(func: Callable, *arg, **kwarg) -> None: {
    # I'll update it in the future ( boring {} =) ).
    func(*arg, **kwarg)
} # type: ignore
