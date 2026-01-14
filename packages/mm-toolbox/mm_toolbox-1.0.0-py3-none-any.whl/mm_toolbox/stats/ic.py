from __future__ import annotations

from typing import Sequence

from ._internal import alpha_from_halflife, alpha_from_span, EWMPair1D, approx_cdf_from_quantiles, MultiP2Quantiles


class OnlinePearson:
    """Streaming Pearson correlation for pairs (x, y)."""

    __slots__ = ("_mode", "_n", "_mx", "_my", "_Cxx", "_Cyy", "_Cxy", "_alpha", "_vx", "_vy", "_cxy", "_ema_x", "_ema_y", "_ew_pair")

    def __init__(self, *, alpha: float | None = None, halflife: float | None = None, span: float | None = None):
        """Initialize.

        If any of alpha/halflife/span is provided, uses EWM updates; else Welford.
        """
        params = [alpha is not None, halflife is not None, span is not None]
        if sum(params) not in (0, 1):
            raise ValueError("Provide none or exactly one of alpha, halflife, or span")
        if alpha is None and (halflife is not None or span is not None):
            alpha = alpha_from_halflife(float(halflife)) if halflife is not None else alpha_from_span(float(span))  # type: ignore[arg-type]
        self._alpha = float(alpha) if alpha is not None else None
        self._mode = "ewm" if self._alpha is not None else "welford"
        self._n = 0
        self._mx = 0.0
        self._my = 0.0
        if self._mode == "welford":
            self._Cxx = 0.0
            self._Cyy = 0.0
            self._Cxy = 0.0
            self._vx = 0.0
            self._vy = 0.0
            self._cxy = 0.0
        else:
            self._ew_pair = EWMPair1D(float(self._alpha))  # type: ignore[arg-type]

    def reset(self) -> None:
        """Reset."""
        self.__init__(alpha=self._alpha)  # type: ignore[arg-type]

    def update(self, x: float, y: float) -> float:
        """Update with (x, y) and return current correlation."""
        if self._mode == "welford":
            self._n += 1
            dx = x - self._mx
            dy = y - self._my
            self._mx += dx / float(self._n)
            self._my += dy / float(self._n)
            self._Cxx += dx * (x - self._mx)
            self._Cyy += dy * (y - self._my)
            self._Cxy += dx * (y - self._my)
            vx = self._Cxx / float(self._n - 1) if self._n > 1 else 0.0
            vy = self._Cyy / float(self._n - 1) if self._n > 1 else 0.0
            cxy = self._Cxy / float(self._n - 1) if self._n > 1 else 0.0
        else:
            self._ew_pair.update(float(x), float(y))
            vx, vy, cxy = self._ew_pair.vx, self._ew_pair.vy, self._ew_pair.cxy
        denom = (vx * vy) ** 0.5
        if denom == 0.0:
            return 0.0
        return cxy / denom

    def correlation(self) -> float:
        """Return current correlation."""
        if self._mode == "welford":
            if self._n <= 1:
                return 0.0
            vx = self._Cxx / float(self._n - 1)
            vy = self._Cyy / float(self._n - 1)
            cxy = self._Cxy / float(self._n - 1)
        else:
            vx, vy, cxy = self._ew_pair.vx, self._ew_pair.vy, self._ew_pair.cxy  # type: ignore[union-attr]
        denom = (vx * vy) ** 0.5
        if denom == 0.0:
            return 0.0
        return cxy / denom


class ApproxSpearmanIC:
    """Approximate Spearman rank IC via streaming quantile transforms."""

    __slots__ = ("_ps", "_qx", "_qy", "_pearson")

    def __init__(
        self,
        probs: Sequence[float] | None = None,
        *,
        alpha: float | None = None,
        halflife: float | None = None,
        span: float | None = None,
    ):
        """Initialize.

        Args:
            probs: Probabilities to maintain for CDF approximation.
            alpha/halflife/span: If provided, use EWM Pearson on ranks; else Welford.
        """
        if probs is None:
            probs = tuple(p / 20.0 for p in range(1, 20))  # 0.05..0.95
        ps = sorted(float(p) for p in probs)
        if not ps:
            raise ValueError("probs must be non-empty")
        if ps[0] <= 0.0 or ps[-1] >= 1.0:
            raise ValueError("probs must be in (0, 1)")
        self._ps = ps
        self._qx = MultiP2Quantiles(self._ps)
        self._qy = MultiP2Quantiles(self._ps)
        self._pearson = OnlinePearson(alpha=alpha, halflife=halflife, span=span)

    def reset(self) -> None:
        """Reset."""
        self.__init__(self._ps)  # type: ignore[arg-type]

    def update(self, x: float, y: float) -> float:
        """Update with (x, y) and return approximate Spearman IC."""
        self._qx.update(x)
        self._qy.update(y)
        qx = self._qx.quantiles()
        qy = self._qy.quantiles()
        u = approx_cdf_from_quantiles(qx, self._ps, x)
        v = approx_cdf_from_quantiles(qy, self._ps, y)
        return self._pearson.update(u, v)

    def correlation(self) -> float:
        """Current approximate Spearman IC."""
        return self._pearson.correlation()


