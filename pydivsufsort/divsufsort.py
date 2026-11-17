"""
Interface to the functions of libdivsufsort
"""

import ctypes
import warnings
from array import array

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
    """Returns pointer to bytes-like input"""
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
                warnings.warn("converting str argument uses more memory", stacklevel=2)
            return ans
        except UnicodeEncodeError:
            raise TypeError("str must only contain ascii chars")
    else:
        warnings.warn(
            "input type not recognized, handled as a buffer of char", stacklevel=2
        )
        return _pointer_frombuffer(inp)


def _cast(inp):
    return _minimize_dtype(_as_unsigned(inp))


def divsufsort(inp, force64=False):
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
    if n <= np.iinfo(np.int32).max and not force64:
        out = (ctypes.c_int32 * n)()
        out_p = ctypes.byref(out)
        retval = libdivsufsort.divsufsort(inp_p, out_p, ctypes.c_int32(n))
    else:
        out = (ctypes.c_int64 * n)()
        out_p = ctypes.byref(out)
        retval = libdivsufsort64.divsufsort64(inp_p, out_p, ctypes.c_int64(n))

    if retval:
        raise Exception("libdivsufsort error", retval)  # pragma: no cover

    return np.ctypeslib.as_array(out)


def _is_wide_array(inp):
    """True if inp is a numpy array that libdivsufsort cannot read directly"""
    if not isinstance(inp, np.ndarray) or inp.dtype == np.uint8:
        return False
    if inp.dtype not in _SUPPORTED_DTYPES:
        raise TypeError(inp.dtype)
    return True


def _bw_transform_wide(inp, sa, force64):
    """bw_transform for integer types other than uint8, in Cython"""
    # stringalg imports this module, thus we cannot import it at the top
    from .stringalg import _bw_transform

    inp = np.ascontiguousarray(inp)
    out = np.empty_like(inp)
    if len(inp) == 0:
        return 0, out
    if sa is None:
        sa = divsufsort(inp, force64=force64)
    idx = _bw_transform(inp, np.ascontiguousarray(sa), out)
    return idx, out


def _inverse_bw_transform_wide(idx, bwt):
    """inverse_bw_transform for integer types other than uint8, in Cython"""
    from .stringalg import _inverse_bw_transform

    bwt = np.ascontiguousarray(bwt)
    out = np.empty_like(bwt)
    order = np.argsort(bwt, kind="stable")
    _inverse_bw_transform(bwt, order, idx, out)
    return out


def bw_transform(inp, sa=None, force64=False):
    """Burrows-Wheeler transform, in the format of libdivsufsort.

    The input has an implicit end marker "$", smaller than all the values.
    The transform is the last column of the sorted rotations of inp + "$",
    without the "$". idx is the row of the "$" in that column.

    Parameters
    ----------
    inp : str (ASCII only), bytes-like object, or numpy array of integers
        All integer dtypes are supported (int8 to uint64).
    sa : numpy array of int32 or int64, optional
        Suffix array of inp. If None, it is calculated.
    force64 : bool
        Use the 64-bit version of libdivsufsort, also for small inputs.

    Returns
    -------
    idx : int
    bwt : numpy array
        Same dtype as inp, or uint8 for str and bytes-like inputs.

    Examples
    --------
    >>> bw_transform(b"banana")
    (4, array([ 97, 110, 110,  98,  97,  97], dtype=uint8))
    >>> bw_transform(np.array([1000, 0, 2000, 0], dtype=np.uint16))
    (3, array([   0, 2000, 1000,    0], dtype=uint16))
    """
    # TODO: inplace computation
    if _is_wide_array(inp):
        return _bw_transform_wide(inp, sa, force64)

    if sa is None:
        sa_p = None
    else:
        sa_p = ctypes.pointer(np.ctypeslib.as_ctypes(sa))

    n = len(inp)
    inp_p = _get_bytes_pointer(inp)

    out = (ctypes.c_uint8 * n)()
    out_p = ctypes.byref(out)
    # the 32-bit version needs a 32-bit suffix array
    if sa is None:
        use32 = n <= np.iinfo(np.int32).max and not force64
    else:
        use32 = sa.dtype == np.int32
    if use32:
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
        raise Exception("libdivsufsort error", retval)  # pragma: no cover

    return idx.value, np.ctypeslib.as_array(out)


def inverse_bw_transform(idx, bwt, force64=False):
    """Inverse of bw_transform.

    Parameters
    ----------
    idx : int
    bwt : str (ASCII only), bytes-like object, or numpy array of integers
        idx and bwt are the output of bw_transform.
        All integer dtypes are supported (int8 to uint64).
    force64 : bool
        Use the 64-bit version of libdivsufsort, also for small inputs.
        Only used for str, bytes-like and uint8 inputs.

    Returns
    -------
    numpy array
        Same dtype as bwt, or uint8 for str and bytes-like inputs.

    Raises
    ------
    ValueError
        If idx is not in [1, len(bwt)] (or 0 when bwt is empty).
        For dtypes other than uint8, also if (idx, bwt) is not the output
        of bw_transform for any input.

    Examples
    --------
    >>> inverse_bw_transform(3, np.array([0, 2000, 1000, 0], dtype=np.uint16))
    array([1000,    0, 2000,    0], dtype=uint16)
    """
    # TODO: inplace computation
    n = len(bwt)
    if not (0 < idx <= n or idx == n == 0):
        raise ValueError(f"idx must be in [1, {n}]")
    if _is_wide_array(bwt):
        return _inverse_bw_transform_wide(idx, bwt)

    bwt_p = _get_bytes_pointer(bwt)

    out = (ctypes.c_uint8 * n)()
    out_p = ctypes.byref(out)

    if n <= np.iinfo(np.int32).max and not force64:
        retval = libdivsufsort.inverse_bw_transform(
            bwt_p, out_p, None, ctypes.c_int32(n), ctypes.c_int32(idx)
        )
    else:
        retval = libdivsufsort64.inverse_bw_transform64(
            bwt_p, out_p, None, ctypes.c_int64(n), ctypes.c_int64(idx)
        )

    if retval:
        raise Exception("libdivsufsort error", retval)  # pragma: no cover

    return np.ctypeslib.as_array(out)


def _pattern_as(pattern, dtype):
    """Converts pattern to a contiguous array of dtype, without changing its values.

    Returns None if a value of pattern does not fit in dtype:
    then pattern cannot occur in an array of dtype.
    """
    if isinstance(pattern, str):
        try:
            pattern = pattern.encode("ascii")
        except UnicodeEncodeError:
            raise TypeError("str must only contain ascii chars")
    if isinstance(pattern, (bytes, bytearray)):
        pattern = np.frombuffer(pattern, dtype=np.uint8)
    pattern = np.asarray(pattern)
    if len(pattern) == 0:
        return np.empty(0, dtype=dtype)
    if pattern.dtype not in _SUPPORTED_DTYPES:
        raise TypeError(pattern.dtype)
    info = np.iinfo(dtype)
    # int() avoids comparisons between int64 and uint64 in numpy
    if int(pattern.min()) < info.min or int(pattern.max()) > info.max:
        return None
    return np.ascontiguousarray(pattern, dtype=dtype)


def sa_search(inp, sa, pattern):
    """Search for a pattern with a suffix array.

    Parameters
    ----------
    inp : str (ASCII only), bytes-like object, or numpy array of integers
        All integer dtypes are supported (int8 to uint64).
    sa : numpy array of int32 or int64
        Suffix array of inp.
    pattern : str (ASCII only), bytes-like object, list or numpy array of integers
        The values of pattern are compared with the values of inp,
        even if the dtypes are different.

    Returns
    -------
    count : int
        Number of occurrences of pattern in inp.
    left : int or None
        The occurrences start at the positions sa[left:left + count].
        None if count is 0.

    Examples
    --------
    >>> s = np.array([1000, 0, 1000, 0], dtype=np.uint16)
    >>> sa_search(s, divsufsort(s), [1000, 0])
    (2, 2)
    """
    if _is_wide_array(inp):
        # stringalg imports this module, thus we cannot import it at the top
        from .stringalg import _sa_search

        pattern = _pattern_as(pattern, inp.dtype)
        if pattern is None:
            return 0, None
        inp = np.ascontiguousarray(inp)
        count, left = _sa_search(inp, np.ascontiguousarray(sa), pattern)
        return count, left if count else None

    n = len(inp)
    m = len(pattern)

    inp_p = _get_bytes_pointer(inp)
    sa_p = ctypes.pointer(np.ctypeslib.as_ctypes(sa))
    if isinstance(pattern, (np.ndarray, list, tuple)):
        pattern = _pattern_as(pattern, np.uint8)
        if pattern is None:
            return 0, None
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
        raise Exception("libdivsufsort error", retval)  # pragma: no cover

    count = retval

    return count, left.value if count else None
