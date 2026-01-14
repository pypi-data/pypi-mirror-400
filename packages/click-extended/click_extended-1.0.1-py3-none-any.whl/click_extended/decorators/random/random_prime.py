"""Parent node for generating a random prime number."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import math
import random
from typing import Any

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RandomPrime(ParentNode):
    """Parent node for generating a random prime number."""

    _SMALL_PRIMES = [
        2,
        3,
        5,
        7,
        11,
        13,
        17,
        19,
        23,
        29,
        31,
        37,
        41,
        43,
        47,
        53,
        59,
        61,
        67,
        71,
        73,
        79,
        83,
        89,
        97,
        101,
        103,
        107,
        109,
        113,
        127,
        131,
        137,
        139,
        149,
        151,
        157,
        163,
        167,
        173,
        179,
        181,
        191,
        193,
        197,
        199,
        211,
        223,
        227,
        229,
        233,
        239,
        241,
        251,
        257,
        263,
        269,
        271,
        277,
        281,
        283,
        293,
        307,
        311,
        313,
        317,
        331,
        337,
        347,
        349,
        353,
        359,
        367,
        373,
        379,
        383,
        389,
        397,
        401,
        409,
        419,
        421,
        431,
        433,
        439,
        443,
        449,
        457,
        461,
        463,
        467,
        479,
        487,
        491,
        499,
        503,
        509,
        521,
        523,
        541,
    ]

    def _calculate_prime(self, k: int) -> int:
        """Calculate the k:th prime number (1-indexed)."""
        if k <= 0:
            raise ValueError("k must be positive")

        if k <= len(self._SMALL_PRIMES):
            return self._SMALL_PRIMES[k - 1]

        # For larger k, use sieve with better upper bound estimation
        # Using Rosser's theorem: p_n < n(ln(n) + ln(ln(n))) for n >= 6
        if k < 6:
            n = 30
        else:
            log_k = math.log(k)
            log_log_k = math.log(log_k)
            n = int(k * (log_k + log_log_k) * 1.3)  # 30% buffer

        sieve = [True] * (n + 1)
        sieve[0] = sieve[1] = False

        for p in range(2, int(math.sqrt(n)) + 1):
            if sieve[p]:
                start = p * p
                step = p if p == 2 else p * 2
                for i in range(start, n + 1, step):
                    sieve[i] = False

        primes: list[int] = []
        for i in range(2, n + 1):
            if sieve[i]:
                primes.append(i)
                if len(primes) == k:
                    return primes[k - 1]

        raise ValueError(
            f"Unable to calculate {k}th prime with buffer size {n}"
        )

    def load(self, context: Context, *args: Any, **kwargs: Any) -> int:
        if kwargs.get("seed") is not None:
            random.seed(kwargs["seed"])

        k = random.randint(1, kwargs["k"])
        return self._calculate_prime(k)


def random_prime(
    name: str,
    k: int = 100,
    seed: int | None = None,
) -> Decorator:
    """
    Generate a random prime number.

    Type: `ParentNode`

    Args:
        name (str):
            The name of the parent node.
        k (int):
            A random prime from the first `k` primes.
            It's important to remember that calculating large prime
            numbers is a slow process, so try to keep the `k` value
            small to avoid slowing down your program.
        seed (int | None):
            Optional seed for reproducible randomness.

    Returns:
        Decorator:
            The decorator function.
    """
    return RandomPrime.as_decorator(
        name=name,
        k=k,
        seed=seed,
    )
