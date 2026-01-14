# cython: boundscheck=False, wraparound=False, cdivision=True

"""
Exponentially weighted statistics.

Fast updates for:
- EWM1D: scalar mean/variance
- EWMPair1D: pairwise means, variances and covariance
- EWMVectorND: vector mean and covariance matrix
"""

from libc.math cimport exp, log, sqrt
cimport numpy as cnp
import numpy as np


cdef inline double _alpha_from_halflife(double halflife):
    if halflife <= 0.0:
        raise ValueError("halflife must be > 0")
    return 1.0 - exp(-log(2.0) / halflife)


cdef inline double _alpha_from_span(double span):
    if span <= 0.0:
        raise ValueError("span must be > 0")
    return 2.0 / (span + 1.0)


cdef inline double _ew_var(double prev_var, double prev_mean, double new_mean, double x, double alpha):
    cdef double delta = x - prev_mean
    return (1.0 - alpha) * (prev_var + alpha * delta * delta)


cdef inline double _ew_cov(
    double prev_cov,
    double prev_mean_x,
    double prev_mean_y,
    double new_mean_x,
    double new_mean_y,
    double x,
    double y,
    double alpha,
):
    cdef double dx = x - prev_mean_x
    cdef double dy = y - prev_mean_y
    return (1.0 - alpha) * (prev_cov + alpha * dx * dy)


cdef class EWM1D:
    """Exponentially weighted mean and variance for a single stream."""
    def __cinit__(self, double alpha):
        if not (0.0 < alpha <= 1.0):
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self.mean = 0.0
        self.var = 0.0
        self.count = 0

    cpdef void reset(self):
        """Reset state."""
        self.mean = 0.0
        self.var = 0.0
        self.count = 0

    cpdef void update(self, double x):
        """Update the EWM statistics with a new observation."""
        cdef double prev_mean, new_mean, v
        if self.count == 0:
            self.mean = x
            self.var = 0.0
            self.count = 1
            return
        prev_mean = self.mean
        new_mean = (1.0 - self.alpha) * prev_mean + self.alpha * x
        v = _ew_var(self.var, prev_mean, new_mean, x, self.alpha)
        if v > -1e-18 and v < 1e-18:
            v = 0.0
        self.var = v
        self.mean = new_mean
        self.count += 1

    cpdef double std(self):
        """Return exponentially weighted standard deviation."""
        return sqrt(self.var)

    cpdef double zscore(self, double x):
        """Compute z-score using current EWM mean/std."""
        cdef double sd = self.std()
        if sd == 0.0:
            return 0.0
        return (x - self.mean) / sd


cdef class EWMPair1D:
    """Exponentially weighted stats for a pair (x, y)."""
    def __cinit__(self, double alpha):
        if not (0.0 < alpha <= 1.0):
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self.mx = 0.0
        self.my = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.cxy = 0.0
        self.count = 0

    cpdef void reset(self):
        """Reset state."""
        self.mx = 0.0
        self.my = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.cxy = 0.0
        self.count = 0

    cpdef void update(self, double x, double y):
        """Update with a new (x, y) pair."""
        cdef double pmx, pmy, nmx, nmy
        if self.count == 0:
            self.mx = x
            self.my = y
            self.vx = 0.0
            self.vy = 0.0
            self.cxy = 0.0
            self.count = 1
            return
        pmx = self.mx
        pmy = self.my
        nmx = (1.0 - self.alpha) * pmx + self.alpha * x
        nmy = (1.0 - self.alpha) * pmy + self.alpha * y
        self.vx = _ew_var(self.vx, pmx, nmx, x, self.alpha)
        self.vy = _ew_var(self.vy, pmy, nmy, y, self.alpha)
        self.cxy = _ew_cov(self.cxy, pmx, pmy, nmx, nmy, x, y, self.alpha)
        self.mx = nmx
        self.my = nmy
        self.count += 1

    cpdef double correlation(self):
        """Return current EWM correlation coefficient."""
        cdef double denom = sqrt(self.vx * self.vy)
        if denom == 0.0:
            return 0.0
        return self.cxy / denom


cdef class EWMVectorND:
    """Exponentially weighted mean and covariance for vectors of length d."""
    def __cinit__(self, int d, double alpha):
        if d <= 0:
            raise ValueError("d must be > 0")
        if not (0.0 < alpha <= 1.0):
            raise ValueError("alpha must be in (0, 1]")
        self.d = d
        self.alpha = alpha
        self.mean_arr = np.zeros((d,), dtype=np.float64)
        self.cov_arr = np.zeros((d, d), dtype=np.float64)
        self.count = 0

    cpdef void reset(self):
        """Reset vector mean and covariance."""
        cdef double[:] mean = self.mean_arr
        cdef double[:, :] cov = self.cov_arr
        cdef int i, j, d = self.d
        for i in range(d):
            mean[i] = 0.0
        for i in range(d):
            for j in range(d):
                cov[i, j] = 0.0
        self.count = 0

    cpdef void update(self, object x):
        """Update vector EWM statistics with a new observation."""
        cdef cnp.ndarray arr = np.asarray(x, dtype=np.float64)
        cdef double[:] xmv = arr
        cdef double[:] mean = self.mean_arr
        cdef double[:, :] cov = self.cov_arr
        cdef int d = self.d
        if arr.ndim != 1 or arr.shape[0] != d:
            raise ValueError("x must be 1D and match dimensionality")
        cdef int i, j
        cdef double a = self.alpha
        if self.count == 0:
            for i in range(d):
                mean[i] = xmv[i]
            for i in range(d):
                for j in range(d):
                    cov[i, j] = 0.0
            self.count = 1
            return
        # prev_mean copy
        cdef double[:] prev_mean = np.copy(self.mean_arr)
        # new mean
        for i in range(d):
            mean[i] = (1.0 - a) * prev_mean[i] + a * xmv[i]
        # outer update
        cdef double dx_i, dx2_j
        for i in range(d):
            dx_i = xmv[i] - prev_mean[i]
            for j in range(d):
                dx2_j = xmv[j] - mean[j]
                cov[i, j] = (1.0 - a) * (cov[i, j] + a * dx_i * dx2_j)
        self.count += 1

    cpdef object correlation(self):
        """Compute correlation matrix from the current covariance."""
        cdef double[:, :] cov = self.cov_arr
        cdef int d = self.d
        cdef cnp.ndarray corr = np.empty((d, d), dtype=np.float64)
        cdef double[:, :] cmv = corr
        cdef double[:] std = np.empty((d,), dtype=np.float64)
        cdef int i, j
        for i in range(d):
            std[i] = sqrt(cov[i, i]) if cov[i, i] > 0.0 else 0.0
        cdef double denom
        for i in range(d):
            for j in range(d):
                denom = std[i] * std[j]
                cmv[i, j] = 0.0 if denom == 0.0 else cov[i, j] / denom
        return corr


def alpha_from_halflife(halflife: float) -> float:
    """Convert half-life to alpha in (0, 1]."""
    return _alpha_from_halflife(halflife)


def alpha_from_span(span: float) -> float:
    """Convert span to alpha: alpha = 2 / (span + 1)."""
    return _alpha_from_span(span)


def ew_var(prev_var: float, prev_mean: float, new_mean: float, x: float, alpha: float) -> float:
    """EWM variance update given previous and new means."""
    return _ew_var(prev_var, prev_mean, new_mean, x, alpha)


def ew_cov(
    prev_cov: float,
    prev_mean_x: float,
    prev_mean_y: float,
    new_mean_x: float,
    new_mean_y: float,
    x: float,
    y: float,
    alpha: float,
) -> float:
    """EWM covariance update for a pair (x, y)."""
    return _ew_cov(prev_cov, prev_mean_x, prev_mean_y, new_mean_x, new_mean_y, x, y, alpha)


def ew_update_matrix(mean_vec, cov, x, alpha: float):
    """Compute next EWM mean and covariance for a vector.

    Args:
        mean_vec: Previous mean vector.
        cov: Previous covariance matrix.
        x: New observation vector.
        alpha: Decay factor in (0, 1].

    Returns:
        (new_mean, new_cov) as numpy arrays.
    """
    cdef cnp.ndarray mean = np.asarray(mean_vec, dtype=np.float64)
    cdef cnp.ndarray covar = np.asarray(cov, dtype=np.float64)
    cdef cnp.ndarray arr = np.asarray(x, dtype=np.float64)
    cdef int d = mean.shape[0]
    if arr.ndim != 1 or arr.shape[0] != d:
        raise ValueError("x must be 1D and match mean dimensionality")
    if covar.ndim != 2 or covar.shape[0] != covar.shape[1] or covar.shape[0] != d:
        raise ValueError("cov must be square and match mean dimensionality")
    cdef EWMVectorND e = EWMVectorND(d, alpha)
    e.mean_arr = mean.copy()
    e.cov_arr = covar.copy()
    e.count = 1
    e.update(arr)
    return (np.asarray(e.mean_arr), np.asarray(e.cov_arr))

