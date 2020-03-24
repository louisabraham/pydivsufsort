# cython: language_level=3, wraparound=False

cimport numpy as np
import numpy as np
import ctypes

from .divsufsort import divsufsort 

import warnings

ctypedef fused sa_t:
    np.int32_t
    np.int64_t

ctypedef fused string_t:
    np.uint8_t
    np.uint16_t
    np.uint32_t
    np.uint64_t
    np.int8_t
    np.int16_t
    np.int32_t
    np.int64_t


def _kasai(string_t[::1] s not None, sa_t[::1] sa not None):

        
    cdef sa_t i, j, n, k
    cdef np.ndarray[sa_t, ndim=1] lcp = np.empty_like(sa) 
    cdef np.ndarray[sa_t, ndim=1] rank = np.empty_like(sa)
        
    n = len(sa)

    for i in range(n):
        rank[sa[i]] = i

    k = 0
    for i in range(n):
        if rank[i] == n - 1:
            lcp[n-1] = k = 0
            continue
        j = sa[rank[i] + 1]
        while i + k < n and j + k < n and s[i+k] == s[j+k]:
            k += 1
        lcp[rank[i]] = k
        if k:
            k -= 1

    return lcp

def kasai(s, sa=None):
    if isinstance(s, bytes):
        # bad, makes a copy
        # fixing would probably require using ctypes
        # like for divsufsort
        # but it would prevent the use of the buffer interface
        warnings.warn("Passing bytes to kasai() forces memory copy")
        s = bytearray(s)
    if sa is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sa = divsufsort(s)

    return _kasai(s, sa)