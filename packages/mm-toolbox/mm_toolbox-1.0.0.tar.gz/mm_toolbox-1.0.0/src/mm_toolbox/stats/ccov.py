from __future__ import annotations

from typing import Sequence

import numpy as np

from ._internal import alpha_from_halflife, alpha_from_span, EWMVectorND, correlation_from_covariance


class OnlineCovariance:
    """Online mean and covariance via Welford/Chan update."""

    __slots__ = ("_d", "_n", "_mean", "_S", "_sample")

    def __init__(self, d: int, *, sample: bool = True):
        """Initialize.

        Args:
            d: Dimensionality.
            sample: If True, covariance uses n-1 denominator; else n.
        """
        if d <= 0:
            raise ValueError("d must be > 0")
        self._d = int(d)
        self._n = 0
        self._mean = np.zeros(self._d, dtype=np.float64)
        self._S = np.zeros((self._d, self._d), dtype=np.float64)
        self._sample = bool(sample)

    def reset(self) -> None:
        """Reset state."""
        self._n = 0
        self._mean.fill(0.0)
        self._S.fill(0.0)

    def update(self, x: Sequence[float] | np.ndarray) -> None:
        """Update with a new observation."""
        arr = np.asarray(x, dtype=np.float64)
        if arr.ndim != 1 or arr.shape[0] != self._d:
            raise ValueError("x must be 1D and match dimensionality")
        self._n += 1
        delta = arr - self._mean
        self._mean += delta / float(self._n)
        self._S += np.outer(delta, arr - self._mean)

    @property
    def count(self) -> int:
        """Number of observations."""
        return self._n

    @property
    def mean(self) -> np.ndarray:
        """Current mean vector."""
        return self._mean

    def covariance(self) -> np.ndarray:
        """Covariance matrix."""
        if self._n == 0:
            return np.zeros_like(self._S)
        denom = float(self._n - 1 if self._sample else self._n)
        if denom <= 0.0:
            return np.zeros_like(self._S)
        return self._S / denom

    def correlation(self) -> np.ndarray:
        """Correlation matrix."""
        return correlation_from_covariance(self.covariance())


class EWMCovariance:
    """Exponentially weighted mean/covariance."""

    __slots__ = ("_d", "_alpha", "_ewv")

    def __init__(
        self,
        d: int,
        *,
        alpha: float | None = None,
        halflife: float | None = None,
        span: float | None = None,
    ):
        """Initialize EWM covariance.

        Exactly one of alpha, halflife, or span must be provided.
        """
        if d <= 0:
            raise ValueError("d must be > 0")
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
        self._d = int(d)
        self._alpha = float(alpha)
        self._ewv = EWMVectorND(self._d, self._alpha)

    def reset(self) -> None:
        """Reset state."""
        self._ewv.reset()

    def update(self, x: Sequence[float] | np.ndarray) -> None:
        """Update with a new observation."""
        self._ewv.update(x)

    @property
    def count(self) -> int:
        """Number of observations (effective updates)."""
        return self._ewv.count

    @property
    def alpha(self) -> float:
        """Alpha parameter."""
        return self._alpha

    @property
    def mean(self) -> np.ndarray:
        """EWM mean vector."""
        return self._ewv.mean

    def covariance(self) -> np.ndarray:
        """EWM covariance."""
        return self._ewv.cov

    def correlation(self) -> np.ndarray:
        """EWM correlation matrix."""
        return self._ewv.correlation()


