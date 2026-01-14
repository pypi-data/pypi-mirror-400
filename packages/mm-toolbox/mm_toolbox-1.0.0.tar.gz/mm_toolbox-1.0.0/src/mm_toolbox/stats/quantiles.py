from __future__ import annotations

from typing import List, Sequence

from ._internal import MultiP2Quantiles, P2Quantile


class StreamingQuantile:
    """Single streaming quantile via P²."""

    __slots__ = ("_q",)

    def __init__(self, p: float):
        """Initialize for probability p in (0, 1)."""
        self._q = P2Quantile(float(p))

    def reset(self) -> None:
        """Reset state."""
        p = self._q.p
        self._q = P2Quantile(p)

    def update(self, x: float) -> float:
        """Update and return current estimate."""
        self._q.update(float(x))
        return self._q.get()

    def get(self) -> float:
        """Return current estimate."""
        return self._q.get()

    @property
    def p(self) -> float:
        """Target probability."""
        return self._q.p


class StreamingQuantiles:
    """Multiple streaming quantiles via P²."""

    __slots__ = ("_qs", "_ps")

    def __init__(self, probs: Sequence[float]):
        """Initialize for given probabilities in (0, 1)."""
        self._qs = MultiP2Quantiles(probs)
        self._ps = list(self._qs.probs)

    def reset(self) -> None:
        """Reset state."""
        self._qs = MultiP2Quantiles(self._ps)

    def update(self, x: float) -> List[float]:
        """Update with x and return current quantile estimates (aligned with probs)."""
        self._qs.update(float(x))
        return self._qs.quantiles()

    def quantiles(self) -> List[float]:
        """Return current estimates aligned with probs."""
        return self._qs.quantiles()

    @property
    def probs(self) -> List[float]:
        """Maintained probabilities."""
        return list(self._ps)


