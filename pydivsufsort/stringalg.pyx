cimport numpy as np

ctypedef fused size_t:
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

cdef kasai(string_t[:] s, size_t[:] sa ):
    if not s.flags['C_CONTIGUOUS']:
        s = np.ascontiguousarray(s)
    if not sa.flags['C_CONTIGUOUS']:
        sa = np.ascontiguousarray(sa)

    cdef size_t i, j, n, k
    cdef lcp = np.empty_like(sa) 
    cdef rank = np.empty_like(sa)

    n = len(sa)

    for i in range(n):
        rank[sa[i]] = i

    k = 0
    for i in range(n):
        if sa[i] == n - 1:
            k = 0
            continue
        j = rank[sa[i] + 1]
        while i + k < n and j + k < n and s[i+k] == s[j+k]:
            k += 1
        lcp[sa[i]] = k
        if k:
            k -= 1

    return lcp