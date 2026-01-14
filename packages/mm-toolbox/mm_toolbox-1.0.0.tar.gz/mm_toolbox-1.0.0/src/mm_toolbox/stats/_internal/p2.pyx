# cython: boundscheck=False, wraparound=False, cdivision=True

"""
P² streaming quantiles.

Provides single-quantile P2Quantile and MultiP2Quantiles for maintaining
multiple quantiles in one pass without storing all data.
"""

import numpy as np
from libc.math cimport fabs


cdef inline void _inc_positions(object self, int start_idx):
    if start_idx <= 0:
        self.n0 += 1
    if start_idx <= 1:
        self.n1 += 1
    if start_idx <= 2:
        self.n2 += 1
    if start_idx <= 3:
        self.n3 += 1
    if start_idx <= 4:
        self.n4 += 1


cdef class P2Quantile:
    """P² algorithm for a single target probability p in (0, 1)."""
    def __cinit__(self, double p):
        if not (0.0 < p < 1.0):
            raise ValueError("p must be in (0, 1)")
        self.p = p
        self.initialized = False
        self.dn0 = 0.0
        self.dn1 = p / 2.0
        self.dn2 = p
        self.dn3 = (1.0 + p) / 2.0
        self.dn4 = 1.0
        self.reset()

    cpdef void reset(self):
        """Reset internal markers and bootstrap buffer."""
        self.q0 = 0.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.q4 = 0.0
        self.n0 = 1
        self.n1 = 2
        self.n2 = 3
        self.n3 = 4
        self.n4 = 5
        self.d0 = 1.0
        self.d1 = 1.0 + 2.0 * self.p
        self.d2 = 1.0 + 4.0 * self.p
        self.d3 = 3.0 + 2.0 * self.p
        self.d4 = 5.0
        self.initialized = False
        # buffer via numpy array for first 5 items
        self._buf = []

    cpdef void update(self, double x):
        """Update the quantile estimate with a new observation."""
        cdef double hp, num
        if not self.initialized:
            self._buf.append(x)
            if len(self._buf) == 5:
                self._buf.sort()
                self.q0, self.q1, self.q2, self.q3, self.q4 = self._buf
                self.initialized = True
            return

        # clamp to min/max markers
        if x < self.q0:
            self.q0 = x
            k = 0
        elif x >= self.q4:
            self.q4 = x
            k = 3
        else:
            if x < self.q1:
                k = 0
            elif x < self.q2:
                k = 1
            elif x < self.q3:
                k = 2
            else:
                k = 3

        _inc_positions(self, k + 1)
        self.d0 += self.dn0
        self.d1 += self.dn1
        self.d2 += self.dn2
        self.d3 += self.dn3
        self.d4 += self.dn4

        # adjust internal markers
        cdef long n0 = self.n0
        cdef long n1 = self.n1
        cdef long n2 = self.n2
        cdef long n3 = self.n3
        cdef long n4 = self.n4
        cdef double q0 = self.q0
        cdef double q1 = self.q1
        cdef double q2 = self.q2
        cdef double q3 = self.q3
        cdef double q4 = self.q4
        cdef double d1 = self.d1
        cdef double d2 = self.d2
        cdef double d3 = self.d3

        cdef long i
        for i in (1, 2, 3):
            if i == 1:
                di = d1 - n1
                if ((di >= 1.0 and n2 - n1 > 1) or (di <= -1.0 and n0 - n1 < -1)):
                    s = 1 if di >= 0.0 else -1
                    num = (n1 - n0 + s) * (q2 - q1) / (n2 - n1) + (n2 - n1 - s) * (q1 - q0) / (n1 - n0)
                    hp = q1 + s * num / (n2 - n0)
                    if q0 < hp < q2:
                        q1 = hp
                    else:
                        q1 = q1 + s * (q2 - q1) / (n2 - n1) if s > 0 else q1 + s * (q1 - q0) / (n1 - n0)
                    n1 += s
            elif i == 2:
                di = d2 - n2
                if ((di >= 1.0 and n3 - n2 > 1) or (di <= -1.0 and n1 - n2 < -1)):
                    s = 1 if di >= 0.0 else -1
                    num = (n2 - n1 + s) * (q3 - q2) / (n3 - n2) + (n3 - n2 - s) * (q2 - q1) / (n2 - n1)
                    hp = q2 + s * num / (n3 - n1)
                    if q1 < hp < q3:
                        q2 = hp
                    else:
                        q2 = q2 + s * (q3 - q2) / (n3 - n2) if s > 0 else q2 + s * (q2 - q1) / (n2 - n1)
                    n2 += s
            else:
                di = d3 - n3
                if ((di >= 1.0 and n4 - n3 > 1) or (di <= -1.0 and n2 - n3 < -1)):
                    s = 1 if di >= 0.0 else -1
                    num = (n3 - n2 + s) * (q4 - q3) / (n4 - n3) + (n4 - n3 - s) * (q3 - q2) / (n3 - n2)
                    hp = q3 + s * num / (n4 - n2)
                    if q2 < hp < q4:
                        q3 = hp
                    else:
                        q3 = q3 + s * (q4 - q3) / (n4 - n3) if s > 0 else q3 + s * (q3 - q2) / (n3 - n2)
                    n3 += s

        self.n0 = n0
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        self.q0 = q0
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.q4 = q4

    cpdef double get(self):
        """Return the current quantile estimate."""
        if not self.initialized:
            if not self._buf:
                return 0.0
            b = sorted(self._buf)
            k = <int>(self.p * (len(b) - 1))
            return b[k]
        return self.q2


cdef class MultiP2Quantiles:
    """Maintain several P² quantiles in parallel."""
    def __cinit__(self, probs):
        cdef list ps_list = [float(p) for p in probs]
        if not ps_list:
            raise ValueError("probs must be non-empty")
        if ps_list[0] <= 0.0 or ps_list[-1] >= 1.0:
            ps_list.sort()
            if ps_list[0] <= 0.0 or ps_list[-1] >= 1.0:
                raise ValueError("probs must be in (0, 1)")
        self.ps = np.array(sorted(ps_list), dtype=np.float64)
        self.qs = [P2Quantile(p) for p in self.ps]

    cpdef void reset(self):
        """Reset all managed quantiles."""
        self.qs = [P2Quantile(float(p)) for p in self.ps]

    cpdef void update(self, double x):
        """Update all managed quantiles with x."""
        cdef int i, n = len(self.qs)
        for i in range(n):
            (<P2Quantile> self.qs[i]).update(x)

    cpdef object quantiles(self):
        """Return current estimates for all managed probabilities."""
        return [(<P2Quantile> q).get() for q in self.qs]

    cpdef double get(self, double p):
        """Return estimate for the probability closest to p."""
        cdef int best = 0
        cdef int i, n = self.ps.shape[0]
        cdef double bestd = 1e99
        cdef double d
        for i in range(n):
            d = fabs(self.ps[i] - p)
            if d < bestd:
                bestd = d
                best = i
        return (<P2Quantile> self.qs[best]).get()

