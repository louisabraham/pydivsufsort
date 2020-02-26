import ctypes
from array import array

import numpy as np

from .dll import libdivsufsort, libdivsufsort64


def divsufsort(inp):
    if isinstance(inp, np.ndarray):
        assert inp.dtype == np.uint8
        if not inp.flags["C_CONTIGUOUS"]:
            # Make a contiguous copy of the numpy array.
            inp = np.ascontiguousarray(inp)            
        inp_p = ctypes.pointer(np.ctypeslib.as_ctypes(inp))
    elif isinstance(inp, array):
        assert inp.typecode == 'B'
        addr, _ = inp.buffer_info()
        inp_p = addr
    else:
        inp_p = inp
   
    n = len(inp)
    if n <= np.iinfo(np.int32).max:
        out = (ctypes.c_int32 * n)()
        out_p = ctypes.byref(out)
        retval = libdivsufsort.divsufsort(inp_p, out_p, ctypes.c_int32(n))
    else:
        out = (ctypes.c_int64 * n)()
        out_p = ctypes.byref(out)
        retval = libdivsufsort64.divsufsort64(inp_p, out_p, ctypes.c_int64(n))
        
    if retval:
        raise Exception("Couldn't create suffix array", retval)
        
    return np.ctypeslib.as_array(out)

