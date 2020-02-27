import ctypes
from array import array
import warnings

import numpy as np

from .dll import libdivsufsort, libdivsufsort64


def _pointer_frombuffer(inp):
    inp = (ctypes.c_uint8 * len(inp)).from_buffer(inp)
    return ctypes.byref(inp)


_SIGNED_TO_UNSIGNED = {
    np.dtype(f"int{bits}"): np.dtype(f"uint{bits}") for bits in [8, 16, 32, 64]
}


def _as_unsigned(inp: np.ndarray):
    """Casts to the corresponding unsigned dtype
    and preserves the order of the elements
    """
    dtype = inp.dtype
    if dtype not in _SIGNED_TO_UNSIGNED:
        return inp
    lastbit = np.iinfo(inp.dtype).max + 1
    return inp.astype(_SIGNED_TO_UNSIGNED[dtype]) ^ lastbit


def _minimize_dtype(inp: np.ndarray):
    """
    Returns an array with a smaller dtype and big endian
    inp is supposed unsigned
    """
    if inp.dtype == np.dtype("uint8"):
        return inp
    inp_min = inp.min()
    n_bits = int(inp.max() - inp_min).bit_length()
    n_bytes = (n_bits + 7) // 8
    # power of 2
    n_bytes = 1 << (n_bytes - 1).bit_length()
    return (inp - inp_min).astype(f">u{n_bytes}")


_SUPPORTED_DTYPES = {
    np.dtype(f"{signed}int{bits}") for signed in ["", "u"] for bits in [8, 16, 32, 64]
}


def divsufsort(inp):
    if isinstance(inp, np.ndarray):
        if inp.dtype == np.uint8:
            if not inp.flags["C_CONTIGUOUS"]:
                # Make a contiguous copy of the numpy array.
                inp = np.ascontiguousarray(inp)
            inp_p = ctypes.pointer(np.ctypeslib.as_ctypes(inp))
        elif inp.dtype in _SUPPORTED_DTYPES:
            inp = _minimize_dtype(_as_unsigned(inp))
            dtype = inp.dtype
            out = divsufsort(inp.view("uint8"))
            return out[out % dtype.itemsize == 0] // dtype.itemsize
        else:
            raise TypeError(inp.dtype)
    elif isinstance(inp, array):
        assert inp.typecode == "B"
        inp_p = _pointer_frombuffer(inp)
    elif isinstance(inp, bytearray):
        inp_p = _pointer_frombuffer(inp)
    elif isinstance(inp, bytes):
        inp_p = inp
    else:
        warnings.warn("input type not recognized, handled as a buffer of char")
        inp_p = _pointer_frombuffer(inp)

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
