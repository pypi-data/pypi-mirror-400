from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

from ._internal import (
    alpha_from_halflife,
    alpha_from_span,
    EWM1D,
    P2Quantile,
    MultiP2Quantiles,
    iqr_to_sigma,
)


class EWMMoments:
    """Exponentially weighted mean and variance."""

    __slots__ = ("_alpha", "_ew")

    def __init__(self, *, alpha: float | None = None, halflife: float | None = None, span: float | None = None):
        """Initialize EWM moments.

        Exactly one of alpha, halflife, or span must be provided.
        """
        params = [alpha is not None, halflife is not None, span is not None]
        if sum(params) != 1:
            raise ValueError("Provide exactly one of alpha, halflife, or span")
        if alpha is None:
            if halflife is not None:
                alpha = alpha_from_halflife(float(halflife))
            else:
                alpha = alpha_from_span(float(span))  # type: ignore[arg-type]
        if not (0.0 < alpha <= 1.0):
            raise ValueError("alpha must be in (0, 1]")
        self._alpha = float(alpha)
        self._ew = EWM1D(self._alpha)

    def reset(self) -> None:
        """Reset."""
        self._ew.reset()

    def update(self, x: float) -> None:
        """Update with a new observation."""
        self._ew.update(float(x))

    @property
    def count(self) -> int:
        """Number of observations (effective updates)."""
        return self._ew.count

    @property
    def alpha(self) -> float:
        """Alpha parameter."""
        return self._alpha

    @property
    def mean(self) -> float:
        """EWM mean."""
        return self._ew.mean

    def variance(self) -> float:
        """EWM variance."""
        return self._ew.var

    def std(self) -> float:
        """EWM standard deviation."""
        return self._ew.std()

    def zscore_of(self, x: float) -> float:
        """Z-score of x under current EWM stats."""
        return self._ew.zscore(float(x))


class EWMZScore:
    """Streaming z-scores with EWM mean/variance."""

    __slots__ = ("_moments",)

    def __init__(self, *, alpha: float | None = None, halflife: float | None = None, span: float | None = None):
        self._moments = EWMMoments(alpha=alpha, halflife=halflife, span=span)

    def reset(self) -> None:
        """Reset."""
        self._moments.reset()

    def update(self, x: float) -> float:
        """Update and return z-score of x."""
        self._moments.update(x)
        return self._moments.zscore_of(x)

    @property
    def mean(self) -> float:
        """Current EWM mean."""
        return self._moments.mean

    def std(self) -> float:
        """Current EWM std."""
        return self._moments.std()


class RobustZScore:
    """Robust z-scores using streaming median and IQR (via P² approximations).

    z = (x - median) / sigma, with sigma ≈ IQR / 1.349
    """

    __slots__ = ("_median", "_q1", "_q3")

    def __init__(self):
        self._median = P2Quantile(0.5)
        self._q1 = P2Quantile(0.25)
        self._q3 = P2Quantile(0.75)

    def reset(self) -> None:
        """Reset."""
        self._median = P2Quantile(0.5)
        self._q1 = P2Quantile(0.25)
        self._q3 = P2Quantile(0.75)

    def update(self, x: float) -> float:
        """Update and return robust z-score."""
        self._median.update(x)
        self._q1.update(x)
        self._q3.update(x)
        med = self._median.get()
        iqr = max(0.0, self._q3.get() - self._q1.get())
        sigma = iqr_to_sigma(iqr)
        if sigma == 0.0:
            return 0.0
        return (float(x) - med) / sigma

    def parameters(self) -> Tuple[float, float, float]:
        """Return (median, q1, q3)."""
        return (self._median.get(), self._q1.get(), self._q3.get())


