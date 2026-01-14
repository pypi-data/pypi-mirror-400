
"""
A simple random number generator using xorshift algorithm.
Features:
- random: Return a random float in [0.0, 1.0).
- randint: Return a random integer N such that a <= N <= b.
- seed: Seed the random number generator.
- shuffle: Shuffle the list in place.
- choice: Return a random element from the list.
- choices: Return a list of k random elements from the list (with replacement).
- sample: Return a list of k unique random elements from the list (without replacement).
- get_seed: Return the current seed value.
- randombytes: Get n random bytes.
"""

from time import time
from typing import Any, List
import os

__all__ = ["Random", "random", "randint", "shuffle", "choice", "choices", "sample", "randombytes"]

class Random:
    """
    A simple random number generator using xorshift algorithm.
    1. random() -> float: Return a random float in [0.0, 1.0).
    2. randint(a: int, b: int) -> int: Return a random integer N such that a <= N <= b.
    3. shuffle(lst: list) -> None: Shuffle the list in place.
    4. choice(lst: list) -> any: Return a random element from the list.
    5. choices(lst: list, k: int) -> list: Return a list of k random elements from the list (with replacement).
    6. sample(lst: list, k: int) -> list: Return a list of k unique random elements from the list (without replacement).
    7. randombytes(n: int) -> bytes: Get n random bytes.
    8. get_seed() -> list[int]: Return the current seed value.
    9. seed(seed: list[int]) -> None: Seed the random number generator.
    """

    M: int = 0xFFFFFFFF_FFFFFFFF

    def __init__(self, seed: list[int] | None = None) -> None:
        """
        Initialize the random number generator with a seed.
        :param seed: The initial seed value.
        """

        if seed is None:
            self._state: list[int] = [_get_seed() for _ in range(16)]
        else:
            self.seed(seed)
        self._p = 0

    def __next__(self) -> int:
        p = self._p
        s0 = self._state[p]
        p = (p + 1) & 15
        s1 = self._state[p]
        s1 ^= s1 << 31  # a
        s1 ^= s1 >> 11  # b
        s0 ^= s0 >> 30  # c
        self._state[p] = s0 ^ s1
        self._p = p
        return (self._state[p] + s1) & self.M

    def _call(self) -> int:
        """
        Call the next random number generator.
        :return: The next random number.
        """

        return self.__next__()

    def seed(self, seed: list[int]) -> None:
        assert len(seed) == 16 and all(map(lambda x: isinstance(x, int), seed)), f"Seed is bad: {seed}"
        self._state = seed

    def random(self) -> float:
        """
        Return a random float in [0.0, 1.0).
        :return: A random float in [0.0, 1.0).
        """

        return self._call() / 0x100000000_00000000

    def randint(self, a: int, b: int) -> int:
        """Return random integer in [a, b] (inclusive)."""
        assert b >= a, "b must be >= a"
        range_len = b - a + 1
        if range_len == 1:
            return a
        mask = 1
        while mask < range_len:
            mask <<= 1
        while True:
            r = self() & (mask - 1)
            if r < range_len:
                return a + r

    def shuffle(self, lst: List[Any]) -> None:
        """
        Shuffle the list in place.
        :param lst: The list to shuffle.
        """

        n: int = len(lst)
        for i in range(n):
            j: int = self.randint(i, n - 1)
            lst[i], lst[j] = lst[j], lst[i]

    def choice(self, lst: List[Any]) -> Any:
        """
        Return a random element from the list.
        :param lst: The list to choose from.
        """

        n: int = len(lst)
        assert n > 0, "Cannot choose from an empty list."
        idx: int = self.randint(0, n - 1)
        return lst[idx]

    def choices(self, lst: List[Any], k: int) -> List[Any]:
        """
        Return a list of k random elements from the list (with replacement).
        :param lst: The list to choose from.
        :param k: The number of elements to choose.
        """

        result: List[Any] = []
        for _ in range(k):
            result.append(self.choice(lst))
        return result

    def sample(self, lst: List[Any], k: int) -> List[Any]:
        """
        Return a list of k unique random elements from the list (without replacement).
        :param lst: The list to sample from.
        :param k: The number of elements to sample.
        :return: A list of k unique random elements.
        """
        n = len(lst)
        assert k <= n, "Sample larger than population."
        if k == 0:
            return []

        '''if k <= n // 2:
            selected_indices = []
            while len(selected_indices) < k:
                idx = self.randint(0, n - 1)
                if idx not in selected_indices:
                    selected_indices.append(idx)
            return [lst[i] for i in selected_indices]
        else:'''
        lst_copy = lst[:]
        for i in range(k):
            j = self.randint(i, n - 1)
            lst_copy[i], lst_copy[j] = lst_copy[j], lst_copy[i]
        return lst_copy[:k]

    def randombytes(self, n: int, secure: bool = False) -> bytes:
        """
        Get n random bytes.
        :param n: The number of random bytes to get.
        :param secure: If True, use os.urandom for cryptographically secure random bytes.
                    If False, generate bytes from the internal state (reproducible).
        :return: n random bytes.
        """

        if secure:
            try:
                return os.urandom(n)
            except OSError as e:
                raise RuntimeError(f"Failed to get secure random bytes: {e}") from e
        else:
            bytes_needed = (n + 7) // 8  # Each 64-bit integer provides 8 bytes
            random_ints = [self() for _ in range(bytes_needed)]
            # Convert each integer to 8 bytes (little-endian) and concatenate
            return b''.join(i.to_bytes(8, 'little') for i in random_ints)[:n]
    
    def get_seed(self) -> list[int]:
        return self._state.copy()

    def __call__(self) -> int:
        """
        Call the next random number generator.
        :return: The next random number.
        """

        return self.__next__()

def _get_seed() -> int:
    """
    Get a seed based on the current time.
    :return: A seed based on the current time.
    """

    time_now: int = int(time() * 0xFFFFFFFF) & 0xFFFFFFFF_FFFFFFFF
    time_seed: int = (time_now >> 33) ^ (time_now & 0xFFFFFFFF)

    urandom_bytes: bytes = os.urandom(8)
    urandom_int: int = int.from_bytes(urandom_bytes, 'little') & 0xFFFFFFFF_FFFFFFFF
    time_seed ^= (urandom_int >> 32) ^ (urandom_int & 0xFFFFFFFF_FFFFFFFF) ^ id(os) ^ hash(str(time_now))

    return abs(time_seed) & 0xFFFFFFFF_FFFFFFFF

"""Initialize the default random number generator with a seed based on the current time."""

_rng: Random = Random()

seed = _rng.seed
random = _rng.random
randint = _rng.randint
shuffle = _rng.shuffle
choice = _rng.choice
choices = _rng.choices
sample = _rng.sample
randombytes = _rng.randombytes
get_seed = _rng.get_seed
next_r = _rng.__next__

next_r()

if __name__ == "__main__":
    for i in range(100):
        print(randint(0, 100))

