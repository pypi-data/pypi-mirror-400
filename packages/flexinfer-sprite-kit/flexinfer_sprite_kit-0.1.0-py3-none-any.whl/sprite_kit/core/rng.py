"""Seeded random number generator for deterministic sprite generation."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


class SeededRNG:
    """Deterministic random number generator for reproducible sprites.

    Uses a simple xorshift algorithm for fast, reproducible random numbers.

    Example:
        >>> rng = SeededRNG(42)
        >>> rng.random()
        0.37454012...
        >>> rng.randint(1, 10)
        7
    """

    def __init__(self, seed: int = 42) -> None:
        """Initialize with seed.

        Args:
            seed: Random seed for reproducibility
        """
        self._seed = seed
        self._state = seed if seed != 0 else 1

    @property
    def seed(self) -> int:
        """Get the initial seed."""
        return self._seed

    def reset(self) -> None:
        """Reset to initial seed."""
        self._state = self._seed if self._seed != 0 else 1

    def _next(self) -> int:
        """Generate next random integer (xorshift32)."""
        x = self._state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        self._state = x & 0xFFFFFFFF
        return self._state

    def random(self) -> float:
        """Get random float in [0.0, 1.0).

        Returns:
            Random float
        """
        return self._next() / 0xFFFFFFFF

    def randint(self, min_val: int, max_val: int) -> int:
        """Get random integer in [min, max].

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)

        Returns:
            Random integer
        """
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        return min_val + (self._next() % (max_val - min_val + 1))

    def uniform(self, min_val: float, max_val: float) -> float:
        """Get random float in [min, max].

        Args:
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Random float
        """
        return min_val + self.random() * (max_val - min_val)

    def choice(self, seq: Sequence[T]) -> T:
        """Random choice from sequence.

        Args:
            seq: Sequence to choose from

        Returns:
            Random element

        Raises:
            IndexError: If sequence is empty
        """
        if not seq:
            raise IndexError("Cannot choose from empty sequence")
        return seq[self.randint(0, len(seq) - 1)]

    def choices(self, seq: Sequence[T], k: int) -> list[T]:
        """Random choices from sequence (with replacement).

        Args:
            seq: Sequence to choose from
            k: Number of choices

        Returns:
            List of random elements
        """
        return [self.choice(seq) for _ in range(k)]

    def shuffle(self, seq: list[T]) -> list[T]:
        """Return shuffled copy of list.

        Args:
            seq: List to shuffle

        Returns:
            Shuffled copy
        """
        result = list(seq)
        for i in range(len(result) - 1, 0, -1):
            j = self.randint(0, i)
            result[i], result[j] = result[j], result[i]
        return result

    def gaussian(self, mean: float = 0.0, std: float = 1.0) -> float:
        """Generate value from Gaussian/normal distribution.

        Uses Box-Muller transform.

        Args:
            mean: Mean of distribution
            std: Standard deviation

        Returns:
            Random value from normal distribution
        """
        u1 = self.random()
        u2 = self.random()

        # Avoid log(0)
        while u1 == 0:
            u1 = self.random()

        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mean + z * std

    def noise1d(self, x: float) -> float:
        """1D value noise (not true Perlin, but deterministic).

        Args:
            x: Input value

        Returns:
            Noise value in [0.0, 1.0]
        """
        # Simple hash-based noise
        xi = int(x)
        xf = x - xi

        # Smooth interpolation
        t = xf * xf * (3 - 2 * xf)

        # Hash the integer parts
        def hash_int(n: int) -> float:
            n = ((n << 13) ^ n) & 0xFFFFFFFF
            n = (n * (n * n * 15731 + 789221) + 1376312589) & 0x7FFFFFFF
            return n / 0x7FFFFFFF

        return hash_int(xi) * (1 - t) + hash_int(xi + 1) * t

    def noise2d(self, x: float, y: float) -> float:
        """2D value noise.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Noise value in [0.0, 1.0]
        """
        xi = int(x)
        yi = int(y)
        xf = x - xi
        yf = y - yi

        # Smooth interpolation
        tx = xf * xf * (3 - 2 * xf)
        ty = yf * yf * (3 - 2 * yf)

        def hash_2d(x: int, y: int) -> float:
            n = x + y * 57
            n = ((n << 13) ^ n) & 0xFFFFFFFF
            n = (n * (n * n * 15731 + 789221) + 1376312589) & 0x7FFFFFFF
            return n / 0x7FFFFFFF

        # Bilinear interpolation
        v00 = hash_2d(xi, yi)
        v10 = hash_2d(xi + 1, yi)
        v01 = hash_2d(xi, yi + 1)
        v11 = hash_2d(xi + 1, yi + 1)

        v0 = v00 * (1 - tx) + v10 * tx
        v1 = v01 * (1 - tx) + v11 * tx

        return v0 * (1 - ty) + v1 * ty

    def fork(self, offset: int = 1) -> SeededRNG:
        """Create child RNG with derived seed.

        Useful for generating independent random streams.

        Args:
            offset: Offset to add to derived seed

        Returns:
            New SeededRNG with derived seed
        """
        derived_seed = (self._seed * 1103515245 + offset) & 0xFFFFFFFF
        return SeededRNG(derived_seed)
