# cython: boundscheck=False, wraparound=False, cdivision=True

"""
Robust helpers.

Includes robust sigma from IQR and a fast piecewise-linear CDF approximation
from a set of quantiles and probabilities.
"""

from libc.math cimport fabs


cdef inline double _iqr_to_sigma(double iqr):
    if iqr <= 0.0:
        return 0.0
    return iqr / 1.349


cpdef double iqr_to_sigma(double iqr):
    """Approximate normal sigma from IQR (sigma ≈ IQR / 1.349)."""
    return _iqr_to_sigma(iqr)


cpdef double approx_cdf_from_quantiles(object quantiles, object probs, double x):
    """Approximate CDF using linear interpolation between quantiles.

    Args:
        quantiles: Sorted quantile values.
        probs: Corresponding sorted probabilities in (0, 1).
        x: Value to evaluate.

    Returns:
        Approximate CDF in [0, 1].
    """
    cdef Py_ssize_t n = len(quantiles)
    if n == 0 or n != len(probs):
        raise ValueError("quantiles and probs must be non-empty and same length")
    cdef double q0 = <double> quantiles[0]
    cdef double qN = <double> quantiles[n - 1]
    if x <= q0:
        return 0.0
    if x >= qN:
        return 1.0
    cdef Py_ssize_t lo = 0
    cdef Py_ssize_t hi = n - 1
    cdef Py_ssize_t mid
    cdef double ql, qh, pl, ph, w
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if x < <double> quantiles[mid]:
            hi = mid
        else:
            lo = mid
    ql = <double> quantiles[lo]
    qh = <double> quantiles[hi]
    pl = <double> probs[lo]
    ph = <double> probs[hi]
    if qh == ql:
        return (pl + ph) * 0.5
    w = (x - ql) / (qh - ql)
    return pl + w * (ph - pl)

