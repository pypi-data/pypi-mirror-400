from __future__ import annotations

from typing import Optional

from ._internal import WelfordMoments


class OnlineMoments:
    """Online moments up to 4th order via Welford.

    Tracks count, mean, variance, skewness, and kurtosis in one pass.
    """

    __slots__ = ("_w",)

    def __init__(self, sample: bool = True):
        """Initialize.

        Args:
            sample: If True, variance is sample (n-1) based, else population.
        """
        self._w = WelfordMoments(sample=sample)

    def reset(self) -> None:
        """Reset all state."""
        self._w.reset()

    def update(self, x: float) -> None:
        """Update with a new observation."""
        self._w.update(float(x))

    @property
    def count(self) -> int:
        """Number of observations."""
        return self._w.count

    @property
    def mean(self) -> float:
        """Mean."""
        return self._w.mean

    def variance(self) -> float:
        """Variance."""
        return self._w.variance()

    def std(self) -> float:
        """Standard deviation."""
        return self._w.std()

    def skewness(self) -> float:
        """Skewness (unbiased in the limit)."""
        return self._w.skewness()

    def kurtosis(self, *, excess: bool = True) -> float:
        """Kurtosis.

        Args:
            excess: If True, return excess kurtosis (normal=0). If False, normal=3.
        """
        return self._w.kurtosis(excess=excess)


