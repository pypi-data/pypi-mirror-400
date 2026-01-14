
"""
Note: This module is old. You can use unstdlibpy.randoms
      Maybe delete it on new version.
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
- setstate: Set the state of the random number generator.
"""

from time import time
from typing import Any, List
import os

__all__ = ["Random", "random", "randint", "seed", "shuffle", "choice", "choices", "sample", "get_seed", "randombytes", "setstate"]

class Random:
    """
    A simple random number generator using xorshift algorithm.
    1. random() -> float: Return a random float in [0.0, 1.0).
    2. randint(a: int, b: int) -> int: Return a random integer N such that a <= N <= b.
    3. seed(seed: Union[int, str, float]) -> None: Seed the random number generator.
    4. shuffle(lst: list) -> None: Shuffle the list in place.
    5. choice(lst: list) -> any: Return a random element from the list.
    6. choices(lst: list, k: int) -> list: Return a list of k random elements from the list (with replacement).
    7. sample(lst: list, k: int) -> list: Return a list of k unique random elements from the list (without replacement).
    8. get_seed() -> int: Return the current seed value.
    9. randombytes(n: int) -> bytes: Get n random bytes.
    10. setstate(state: int) -> None: Set the state of the random number generator.
    """

    M: int = 0xFFFFFFFF
    def __init__(self, seed: int) -> None:
        """
        Initialize the random number generator with a seed.
        :param seed: The initial seed value.
        """

        assert isinstance(seed, int), "Seed should is a int."
        self._seed: int = seed
    
    def __next__(self) -> int:
        """
        Generate the next random number using xorshift algorithm.
        :return: The next random number.
        """
        
        s = self._seed & Random.M
        s ^= (s << 13) & Random.M
        s ^= (s >> 17) & Random.M
        s ^= (s << 5) & Random.M
        self._seed = s
        return s
    
    def _call(self) -> int:
        """
        Call the next random number generator.
        :return: The next random number.
        """

        return self.__next__()

    def random(self) -> float:
        """
        Return a random float in [0.0, 1.0).
        :return: A random float in [0.0, 1.0).
        """

        return self._call() / self.M

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

    def seed(self, seed: object) -> None:
        """
        Seed the random number generator.
        :param seed: The seed value (int, str, or float).
        """

        if isinstance(seed, str):
            # Stable conversion from string to int seed
            seed_int: int = abs(hash(seed)) & Random.M
            seed = seed_int
        elif isinstance(seed, float):
            seed = int(seed * (Random.M + 1)) & Random.M
        elif not isinstance(seed, int):
            raise TypeError("Seed should be int, str or float.")

        self._seed = seed & Random.M

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
        """

        n: int = len(lst)
        assert k <= n, "Sample larger than population."
        lst_copy: List[Any] = lst[:]
        self.shuffle(lst_copy)
        return lst_copy[:k]

    def get_seed(self) -> int:
        """
        Get the current seed value.
        :return: The current seed value.
        """

        return self._seed

    def setstate(self, state: int) -> None:
        """
        Set the state of the random number generator.
        :param state: The state to set.
        """

        assert isinstance(state, int), "State should be an integer."
        self._seed = state

    def randombytes(self, n: int) -> bytes:
        """
        Get n random bytes.
        :param n: The number of random bytes to get.
        :return: n random bytes.
        """

        return os.urandom(n)

    def __eq__(self, other: object) -> bool:
        """
        equality comparison of two Random objects.
        :param other: The other Random object to compare with.
        :return: True if the two Random objects are equal, False otherwise.
        """

        if not isinstance(other, Random):
            return False
        
        return self._seed == other._seed

    def __hash__(self) -> int:
        """
        hash of the Random object.
        :return: The hash of the Random object.
        """
        return hash((self._seed, id(self)))

    def __repr__(self) -> str:
        """
        string representation of the Random object.
        :return: A string representation of the Random object.
        """

        return f"<unstd.random.Random seed={self._seed}>"
    
    def __str__(self) -> str:
        """
        string representation of the Random object.
        :return: A string representation of the Random object.
        """

        return self.__repr__()

    def __call__(self) -> int:
        """
        Call the next random number generator.
        :return: The next random number.
        """

        return self._call()

def _get_seed() -> int:
    """
    Get a seed based on the current time.
    :return: A seed based on the current time.
    """

    time_now: int = int(time() * 1000) & 0xFFFFFFFF
    time_seed: int = (time_now >> 16) ^ (time_now & 0xFFFF)

    urandom_bytes: bytes = os.urandom(4)
    urandom_int: int = int.from_bytes(urandom_bytes, 'little') & 0xFFFFFFFF
    time_seed ^= (urandom_int >> 16) ^ (urandom_int & 0xFFFF) ^ id(os) ^ hash(str(time_now))

    return abs(time_seed) & 0xFFFFFFFF

"""Initialize the default random number generator with a seed based on the current time."""

_rng: Random = Random(_get_seed())

random = _rng.random
randint = _rng.randint
seed = _rng.seed
shuffle = _rng.shuffle
choice = _rng.choice
choices = _rng.choices
sample = _rng.sample
get_seed = _rng.get_seed
randombytes = _rng.randombytes
setstate = _rng.setstate
next_r = _rng.__next__

next_r()

if __name__ == "__main__":
    for i in range(100):
        print(random())

