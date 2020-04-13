"""
Interface to the functions of libdivsufsort
"""

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
    """_casts to the corresponding unsigned dtype
    and preserves the order of the elements
    """
    dtype = inp.dtype
    if dtype not in _SIGNED_TO_UNSIGNED:
        return inp
    lastbit = np.iinfo(dtype).max + 1
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


def _get_bytes_pointer(inp):
    """Returns pointer to bytes-like input
    """
    if isinstance(inp, np.ndarray):
        assert inp.dtype == np.uint8
        # https://stackoverflow.com/q/60848009/5133167
        if not inp.flags["C_CONTIGUOUS"]:
            # Make a contiguous copy of the numpy array.
            inp = np.ascontiguousarray(inp)
        return ctypes.pointer(np.ctypeslib.as_ctypes(inp))
    elif isinstance(inp, array):
        assert inp.typecode == "B"
        return _pointer_frombuffer(inp)
    elif isinstance(inp, bytearray):
        return _pointer_frombuffer(inp)
    elif isinstance(inp, bytes):
        return inp
    elif isinstance(inp, str):
        try:
            ans = inp.encode("ascii")
            if len(inp) > 999:
                warnings.warn("converting str argument uses more memory")
            return ans
        except UnicodeEncodeError:
            raise TypeError("str must only contain ascii chars")
    else:
        warnings.warn("input type not recognized, handled as a buffer of char")
        return _pointer_frombuffer(inp)


def _cast(inp):
    return _minimize_dtype(_as_unsigned(inp))


def divsufsort(inp):
    if isinstance(inp, np.ndarray):
        if inp.dtype == np.uint8:
            pass
        elif inp.dtype in _SUPPORTED_DTYPES:
            inp = _cast(inp)
            dtype = inp.dtype
            out = divsufsort(inp.view("uint8"))
            return out[out % dtype.itemsize == 0] // dtype.itemsize
        else:
            raise TypeError(inp.dtype)

    n = len(inp)
    inp_p = _get_bytes_pointer(inp)
    if n <= np.iinfo(np.int32).max:
        out = (ctypes.c_int32 * n)()
        out_p = ctypes.byref(out)
        retval = libdivsufsort.divsufsort(inp_p, out_p, ctypes.c_int32(n))
    else:
        out = (ctypes.c_int64 * n)()
        out_p = ctypes.byref(out)
        retval = libdivsufsort64.divsufsort64(inp_p, out_p, ctypes.c_int64(n))

    if retval:
        raise Exception("libdivsufsort error", retval)

    return np.ctypeslib.as_array(out)


DTYPE_NOT_SUPPORTED_MSG = (
    "This function only supports inputs that can be converted to uint8.\n"
    "Please raise an issue on <https://github.com/louisabraham/pydivsufsort/issues>"
)


def bw_transform(inp, sa=None):
    # TODO: inplace computation
    if isinstance(inp, np.ndarray):
        if inp.dtype == np.uint8:
            pass
        if inp.dtype in _SUPPORTED_DTYPES:
            inp = _cast(inp)
            dtype = inp.dtype
            if dtype != np.uint8:
                raise TypeError(DTYPE_NOT_SUPPORTED_MSG)

    if sa is None:
        sa_p = None
    else:
        sa_p = ctypes.pointer(np.ctypeslib.as_ctypes(sa))

    n = len(inp)
    inp_p = _get_bytes_pointer(inp)

    out = (ctypes.c_uint8 * n)()
    out_p = ctypes.byref(out)
    if sa is not None and sa.dtype == np.int32 or n <= np.iinfo(np.int32).max:
        idx = ctypes.c_int32()
        idx_p = ctypes.byref(idx)
        retval = libdivsufsort.bw_transform(
            inp_p, out_p, sa_p, ctypes.c_int32(n), idx_p
        )
    else:
        idx = ctypes.c_int64()
        idx_p = ctypes.byref(idx)
        retval = libdivsufsort64.bw_transform64(
            inp_p, out_p, sa_p, ctypes.c_int64(n), idx_p
        )

    if retval:
        raise Exception("libdivsufsort error", retval)

    return idx.value, np.ctypeslib.as_array(out)


def inverse_bw_transform(idx, bwt):
    # TODO: inplace computation
    n = len(bwt)
    bwt_p = _get_bytes_pointer(bwt)

    out = (ctypes.c_uint8 * n)()
    out_p = ctypes.byref(out)

    if n <= np.iinfo(np.int32).max:
        retval = libdivsufsort.inverse_bw_transform(
            bwt_p, out_p, None, ctypes.c_int32(n), ctypes.c_int32(idx)
        )
    else:
        retval = libdivsufsort64.inverse_bw_transform64(
            bwt_p, out_p, None, ctypes.c_int64(n), ctypes.c_int64(idx)
        )

    if retval:
        raise Exception("libdivsufsort error", retval)

    return np.ctypeslib.as_array(out)


def sa_search(inp, sa, pattern):
    n = len(inp)
    m = len(pattern)

    inp_p = _get_bytes_pointer(inp)
    sa_p = ctypes.pointer(np.ctypeslib.as_ctypes(sa))
    if isinstance(pattern, np.ndarray):
        pattern = _cast(pattern)
    pat_p = _get_bytes_pointer(pattern)

    if sa.dtype == np.int32:
        n = ctypes.c_int32(n)
        m = ctypes.c_int32(m)
        left = ctypes.c_int32()
        left_p = ctypes.byref(left)
        retval = libdivsufsort.sa_search(inp_p, n, pat_p, m, sa_p, n, left_p)
    else:
        n = ctypes.c_int64(n)
        m = ctypes.c_int64(m)
        left = ctypes.c_int64()
        left_p = ctypes.byref(left)
        retval = libdivsufsort64.sa_search64(inp_p, n, pat_p, m, sa_p, n, left_p)

    if retval < 0:
        raise Exception("libdivsufsort error", retval)

    count = retval

    return count, left.value if count else None
