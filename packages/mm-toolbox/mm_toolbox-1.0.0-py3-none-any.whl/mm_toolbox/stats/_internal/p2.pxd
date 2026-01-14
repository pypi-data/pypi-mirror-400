cdef class P2Quantile:
    cdef double p
    cdef double q0
    cdef double q1
    cdef double q2
    cdef double q3
    cdef double q4
    cdef long n0
    cdef long n1
    cdef long n2
    cdef long n3
    cdef long n4
    cdef double d0
    cdef double d1
    cdef double d2
    cdef double d3
    cdef double d4
    cdef bint initialized
    cdef double dn0
    cdef double dn1
    cdef double dn2
    cdef double dn3
    cdef double dn4
    cpdef void reset(self)
    cpdef void update(self, double x)
    cpdef double get(self)

cdef class MultiP2Quantiles:
    cdef double[:] ps
    cdef object qs  # list of P2Quantile
    cpdef void reset(self)
    cpdef void update(self, double x)
    cpdef object quantiles(self)
    cpdef double get(self, double p)

