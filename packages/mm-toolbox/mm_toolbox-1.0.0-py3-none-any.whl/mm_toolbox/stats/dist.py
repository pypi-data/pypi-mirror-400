from __future__ import annotations

import math
from typing import Tuple

from .ewm import EWMMoments
from .online import OnlineMoments
from .quantiles import StreamingQuantiles


class NormalEWM:
    """EWM normal fit (mu, sigma)."""

    __slots__ = ("_mom",)

    def __init__(self, *, alpha: float | None = None, halflife: float | None = None, span: float | None = None):
        self._mom = EWMMoments(alpha=alpha, halflife=halflife, span=span)

    def reset(self) -> None:
        """Reset."""
        self._mom.reset()

    def update(self, x: float) -> Tuple[float, float]:
        """Update and return (mu, sigma)."""
        self._mom.update(x)
        return (self._mom.mean, self._mom.std())

    def parameters(self) -> Tuple[float, float]:
        """Return (mu, sigma)."""
        return (self._mom.mean, self._mom.std())


class LaplaceFit:
    """Laplace fit via quantiles: mu=median, b=IQR/(2 ln 2)."""

    __slots__ = ("_qs", "_ps")

    def __init__(self):
        self._ps = (0.25, 0.5, 0.75)
        self._qs = StreamingQuantiles(self._ps)

    def reset(self) -> None:
        """Reset."""
        self._qs = StreamingQuantiles(self._ps)

    def update(self, x: float) -> Tuple[float, float]:
        """Update and return (mu, b)."""
        self._qs.update(x)
        q25, q50, q75 = self._qs.quantiles()
        iqr = max(0.0, q75 - q25)
        b = iqr / (2.0 * math.log(2.0)) if iqr > 0.0 else 0.0
        return (q50, b)

    def parameters(self) -> Tuple[float, float]:
        """Return (mu, b)."""
        q25, q50, q75 = self._qs.quantiles()
        iqr = max(0.0, q75 - q25)
        b = iqr / (2.0 * math.log(2.0)) if iqr > 0.0 else 0.0
        return (q50, b)


class StudentTMomentsFit:
    """Student-t fit via moments (mu, nu, s).

    Uses excess kurtosis g2 to solve nu = 4 + 6/g2 when g2 > 0,
    else falls back to a large nu (approx normal).
    Scale s is from variance: var = s^2 * nu / (nu - 2), nu > 2.
    """

    __slots__ = ("_mom", "_large_nu")

    def __init__(self, *, large_nu: float = 1e6):
        self._mom = OnlineMoments(sample=True)
        self._large_nu = float(large_nu)

    def reset(self) -> None:
        """Reset."""
        self._mom.reset()

    def update(self, x: float) -> Tuple[float, float, float]:
        """Update and return (mu, nu, s)."""
        self._mom.update(x)
        return self.parameters()

    def parameters(self) -> Tuple[float, float, float]:
        """Return (mu, nu, s)."""
        mu = self._mom.mean
        var = self._mom.variance()
        g2 = self._mom.kurtosis(excess=True)
        if g2 > 0.0:
            nu = max(4.001, 4.0 + 6.0 / g2)
        else:
            nu = self._large_nu
        if nu <= 2.0 or var == 0.0:
            s = 0.0
        else:
            s = math.sqrt(max(0.0, var * (nu - 2.0) / nu))
        return (mu, nu, s)


