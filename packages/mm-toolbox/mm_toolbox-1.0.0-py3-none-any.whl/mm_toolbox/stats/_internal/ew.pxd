cdef double _alpha_from_halflife(double halflife)
cdef double _alpha_from_span(double span)
cdef double _ew_var(double prev_var, double prev_mean, double new_mean, double x, double alpha)
cdef double _ew_cov(double prev_cov, double prev_mean_x, double prev_mean_y, double new_mean_x, double new_mean_y, double x, double y, double alpha)

cdef class EWM1D:
    cdef double alpha
    cdef double mean
    cdef double var
    cdef long count
    cpdef void reset(self)
    cpdef void update(self, double x)
    cpdef double std(self)
    cpdef double zscore(self, double x)

cdef class EWMPair1D:
    cdef double alpha
    cdef double mx
    cdef double my
    cdef double vx
    cdef double vy
    cdef double cxy
    cdef long count
    cpdef void reset(self)
    cpdef void update(self, double x, double y)
    cpdef double correlation(self)

cdef class EWMVectorND:
    cdef int d
    cdef double alpha
    cdef object mean_arr  # numpy.ndarray
    cdef object cov_arr   # numpy.ndarray
    cdef long count
    cpdef void reset(self)
    cpdef void update(self, object x)
    cpdef object correlation(self)

