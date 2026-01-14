# cython: boundscheck=False, wraparound=False, cdivision=True

"""
Matrix utilities.

Efficient conversion from covariance to correlation matrices.
"""

cimport numpy as cnp
import numpy as np
from libc.math cimport sqrt


cpdef object correlation_from_covariance(object cov):
    """Compute correlation matrix from a covariance matrix.

    Args:
        cov: Square covariance matrix (array-like).

    Returns:
        New numpy.ndarray correlation matrix of the same shape.
    """
    cdef cnp.ndarray covar = np.asarray(cov, dtype=np.float64)
    if covar.ndim != 2 or covar.shape[0] != covar.shape[1]:
        raise ValueError("cov must be a square matrix")
    cdef int d = covar.shape[0]
    cdef cnp.float64_t[:, :] cm = covar
    cdef cnp.ndarray corr = np.empty((d, d), dtype=np.float64)
    cdef cnp.float64_t[:, :] rm = corr
    cdef cnp.float64_t[:] std = np.empty((d,), dtype=np.float64)
    cdef int i, j
    for i in range(d):
        std[i] = sqrt(cm[i, i]) if cm[i, i] > 0.0 else 0.0
    cdef double denom
    for i in range(d):
        for j in range(d):
            denom = std[i] * std[j]
            rm[i, j] = 0.0 if denom == 0.0 else cm[i, j] / denom
    return corr

