cimport cdivsufsort64 as c
import numpy as np
cimport numpy as np


def divsufsort(np.ndarray[np.uint8_t, ndim=1, mode='c'] inp not None):
    if not inp.flags['C_CONTIGUOUS']:
        # Make a contiguous copy of the numpy array.
        inp = np.ascontiguousarray(inp)

    cdef np.ndarray[np.int64_t, ndim=1] out = np.empty(inp.shape[0], dtype=np.int64)
    
    error = c.divsufsort64(&inp[0], &out[0], inp.shape[0])
    assert error == 0
    
    return out
    

