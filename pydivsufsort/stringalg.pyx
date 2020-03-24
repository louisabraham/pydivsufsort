# cython: language_level=3, wraparound=False

cimport numpy as np
import numpy as np

from .divsufsort import divsufsort 


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


def kasai(string_t[::1] s not None, sa_t[::1] sa = None):

    if sa is None:
        return _kasai(s, divsufsort(s))
        
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
