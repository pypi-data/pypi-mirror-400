from __future__ import annotations

from typing import Sequence

import numpy as np


class RecursiveLeastSquares:
    """Recursive least squares with forgetting."""

    __slots__ = ("_d", "_lambda", "_theta", "_P")

    def __init__(self, n_features: int, *, forgetting: float = 1.0, delta: float = 1e3):
        """Initialize RLS.

        Args:
            n_features: Number of features.
            forgetting: Forgetting factor λ in (0, 1], 1.0 means no forgetting.
            delta: Initial covariance scale, P0 = delta * I.
        """
        if n_features <= 0:
            raise ValueError("n_features must be > 0")
        if not (0.0 < forgetting <= 1.0):
            raise ValueError("forgetting must be in (0, 1]")
        if delta <= 0.0:
            raise ValueError("delta must be > 0")
        self._d = int(n_features)
        self._lambda = float(forgetting)
        self._theta = np.zeros(self._d, dtype=np.float64)
        self._P = np.eye(self._d, dtype=np.float64) * float(delta)

    def reset(self) -> None:
        """Reset coefficients and covariance."""
        self._theta.fill(0.0)
        self._P[:] = np.eye(self._d, dtype=np.float64) * self._P.trace() / self._d

    def predict(self, x: Sequence[float] | np.ndarray) -> float:
        """Predict y for feature vector x."""
        phi = np.asarray(x, dtype=np.float64)
        if phi.ndim != 1 or phi.shape[0] != self._d:
            raise ValueError("x must be 1D and match n_features")
        return float(self._theta @ phi)

    def update(self, x: Sequence[float] | np.ndarray, y: float) -> float:
        """Update with (x, y) and return prediction after update."""
        phi = np.asarray(x, dtype=np.float64)
        if phi.ndim != 1 or phi.shape[0] != self._d:
            raise ValueError("x must be 1D and match n_features")
        lam = self._lambda
        P_phi = self._P @ phi
        denom = lam + float(phi @ P_phi)
        K = P_phi / denom
        err = float(y) - float(phi @ self._theta)
        self._theta = self._theta + K * err
        self._P = (self._P - np.outer(K, phi) @ self._P) / lam
        return float(self._theta @ phi)

    @property
    def coef(self) -> np.ndarray:
        """Current coefficients."""
        return self._theta

    def covariance(self) -> np.ndarray:
        """Coefficient covariance matrix."""
        return self._P


