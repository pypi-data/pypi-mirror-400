# cython: language_level=3
import numpy as np
cimport numpy as np
from libc.stddef cimport size_t

cdef extern from "itrigamma.h":
    void itrigamma_vec(const double *y, double *out, size_t n)

def itrigamma(y):
    cdef np.ndarray[np.float64_t, ndim=1, mode="c"] y1
    cdef np.ndarray[np.float64_t, ndim=1, mode="c"] out1
    cdef size_t n
    cdef tuple shape

    arr = np.asarray(y, dtype=np.float64)
    shape = arr.shape
    y1 = np.ascontiguousarray(arr.ravel(), dtype=np.float64)
    out1 = np.empty_like(y1)

    n = <size_t> y1.size
    itrigamma_vec(<const double*> y1.data, <double*> out1.data, n)

    out = out1.reshape(shape)
    # for scalars
    if shape == ():
        return float(out[()])
    return out
