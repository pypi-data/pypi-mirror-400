# cython: boundscheck=False, wraparound=False, cdivision=True

"""
Welford online moments.

Maintains mean, variance, skewness, and kurtosis in one pass with numeric
stability, optionally returning sample or population variance.
"""

from libc.math cimport sqrt


cdef class WelfordMoments:
    """Online central moments up to 4th order via Welford."""
    def __cinit__(self, bint sample=True):
        self.sample = sample
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.m3 = 0.0
        self.m4 = 0.0

    cpdef void reset(self):
        """Reset all internal counters and accumulators."""
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.m3 = 0.0
        self.m4 = 0.0

    cpdef void update(self, double x):
        """Update moments with a new observation."""
        cdef long n0 = self.count
        cdef long n = n0 + 1
        cdef double delta = x - self.mean
        cdef double delta_n = delta / n
        cdef double delta_n2 = delta_n * delta_n
        cdef double term1 = delta * delta_n * n0
        self.m4 = self.m4 + term1 * delta_n2 * (n * (n - 3) + 3) + 6.0 * delta_n2 * self.m2 - 4.0 * delta_n * self.m3
        self.m3 = self.m3 + term1 * delta_n * (n - 2.0) - 3.0 * delta_n * self.m2
        self.m2 = self.m2 + term1
        self.mean = self.mean + delta_n
        self.count = n

    cpdef double variance(self):
        """Return variance (sample if configured, else population)."""
        cdef long n = self.count
        if n == 0:
            return 0.0
        if self.sample:
            if n < 2:
                return 0.0
            return self.m2 / (n - 1)
        return self.m2 / n

    cpdef double std(self):
        """Return standard deviation."""
        return sqrt(self.variance())

    cpdef double skewness(self):
        """Return skewness (0 when insufficient data)."""
        cdef long n = self.count
        cdef double m2, m3
        if n < 3 or self.m2 == 0.0:
            return 0.0
        m2 = self.m2 / n
        m3 = self.m3 / n
        if m2 <= 0.0:
            return 0.0
        return m3 / (m2 ** 1.5)

    cpdef double kurtosis(self, bint excess=True):
        """Return kurtosis; excess=True returns excess kurtosis (normal=0)."""
        cdef long n = self.count
        cdef double m2, m4, g2
        if n < 4 or self.m2 == 0.0:
            return 0.0 if excess else 3.0
        m2 = self.m2 / n
        m4 = self.m4 / n
        if m2 <= 0.0:
            g2 = 0.0
        else:
            g2 = m4 / (m2 * m2)
        return g2 - 3.0 if excess else g2

