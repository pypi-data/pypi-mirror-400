"""Internal utilities for streaming statistics.

This package exposes high-performance implementations of core
streaming statistics used across the toolbox. Import from here rather
than submodules to keep a stable public surface.
"""

from .ew import (  # type: ignore
    alpha_from_halflife,
    alpha_from_span,
    ew_cov,
    ew_var,
    ew_update_matrix,
    EWM1D,
    EWMPair1D,
    EWMVectorND,
)
from .matrix import correlation_from_covariance  # type: ignore
from .p2 import P2Quantile, MultiP2Quantiles  # type: ignore
from .robust import approx_cdf_from_quantiles, iqr_to_sigma  # type: ignore
from .welford import WelfordMoments  # type: ignore
from .typing import Array1D  # noqa: F401


