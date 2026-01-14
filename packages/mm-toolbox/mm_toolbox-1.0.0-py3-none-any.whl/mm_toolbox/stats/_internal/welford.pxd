cdef class WelfordMoments:
    cdef bint sample
    cdef long count
    cdef double mean
    cdef double m2
    cdef double m3
    cdef double m4
    cpdef void reset(self)
    cpdef void update(self, double x)
    cpdef double variance(self)
    cpdef double std(self)
    cpdef double skewness(self)
    cpdef double kurtosis(self, bint excess=*)

