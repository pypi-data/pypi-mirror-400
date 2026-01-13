"""Generate PRBS with Random Modules"""

import random
from typing import TypeAlias

from .base import BinarySequence

__all__ = ("random_sequence",)

Seed: TypeAlias = None | int | float | str | bytes | bytearray


def random_sequence(n: int, seed: Seed = None) -> BinarySequence:
    """Generates a random sequence of length n.
    If a seed is provided, the output will be reproducible.

    Args:
        n (int): number of bits to generate
        seed (Seed, optional): random seed. Defaults to None.

    Returns:
        BinarySequence: Random binary sequence.
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")

    rng: random.Random = random.Random(seed)
    random_bits = [rng.randint(0, 1) for _ in range(n)]
    return BinarySequence(random_bits)
