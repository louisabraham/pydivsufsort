cimport cdivsufsort64 as c
import numpy as np
cimport numpy as np


def divsufsort(object[np.uint8_t, ndim=1] inp not None):
    if isinstance(inp, np.ndarray) and not inp.flags['C_CONTIGUOUS']:
        # Make a contiguous copy of the numpy array.
        inp = np.ascontiguousarray(inp)

    cdef np.ndarray[np.int64_t, ndim=1] out = np.empty(len(inp), dtype=np.int64)
    
    error = c.divsufsort64(&inp[0], &out[0], len(inp))
    assert error == 0
    
    return out
    

