# cython: language_level=3, wraparound=False, boundscheck=False

cimport numpy as np
import numpy as np

import warnings
from .divsufsort import divsufsort 

ctypedef np.uint64_t ull

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

def handle_input(s):
    if isinstance(s, np.ndarray):
        # in my tests, converting to contiguous and using [::1]
        # gives *slightly* better performance than using [:]
        if not s.flags["C_CONTIGUOUS"]:
            # Make a contiguous copy of the numpy array.
            s = np.ascontiguousarray(s)
    if isinstance(s, str):
        try:
            s = s.encode("ascii")
            if len(s) > 999:
                warnings.warn("converting str argument uses more memory")
        except UnicodeEncodeError:
            raise TypeError("str must only contain ascii chars")
    return s


"""
TODO: reuse rank array for kasai and lcp_segtree
"""

def _kasai(string_t[::1] s not None, sa_t[::1] sa not None):

    cdef ull i, j, n, k
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

def _kasai_bytes(const unsigned char[::1] s not None, sa_t[::1] sa not None):
    """Same as _kasai but with a const first argument.
    
    TODO: Cython does not support const fused types arguments YET
    but it will be fixed in the 0.30 release
    <https://github.com/pandas-dev/pandas/issues/31710>
    """
        
    cdef ull i, j, n, k
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
    s = handle_input(s)
    if sa is None:
        sa = divsufsort(s)
    if isinstance(s, bytes):
        return _kasai_bytes(s, sa)
    return _kasai(s, sa)

def _lcp_segtree(
        string_t[::1] s not None,
        np.ndarray[sa_t, ndim=1] sa not None,
        np.ndarray[sa_t, ndim=1] lcp not None
    ):

    cdef ull i, j, n, k
    
    cdef np.ndarray[sa_t, ndim=1] segtree = np.concatenate([np.empty_like(lcp), lcp])
    cdef np.ndarray rank = np.empty_like(sa)
        
    n = len(sa)
    for i in range(n-1, 0, -1):
        segtree[i] = min(segtree[i << 1], segtree[i << 1 | 1])
    
    for i in range(n):
        rank[sa[i]] = i

    return rank, segtree


def lcp_segtree(s, sa=None, lcp=None):
    s = handle_input(s)
    if sa is None:
        sa = divsufsort(s)
    if lcp is None:
        lcp = kasai(s, sa)
    if isinstance(s, bytes):
        # tofix
        s = bytearray(s)
    return _lcp_segtree(s, sa, lcp)


def _lcp_query(
        np.ndarray[sa_t, ndim=1] rank not None,
        np.ndarray[sa_t, ndim=1] segtree not None,
        queries
    ):
    cdef sa_t n, q, i

    # note: l and r could hold 2*n-1
    # fortunately, n is at most int64
    cdef ull l, r

    n = len(rank)
    q = len(queries)

    cdef np.ndarray[sa_t, ndim=1] ans = np.empty(q, dtype=segtree.dtype)

    # TODO: parallelize
    # prange throws a lot of errors
    for i in range(q):
        l, r = queries[i]
        res = n - max(l, r)
        l, r = rank[l], rank[r]
        if r < l:
            l, r = r, l
        l += n
        r += n
        while l < r:
            if l&1:
                if segtree[l] < res:
                    res = segtree[l]
                l += 1
            if r&1:
                r -= 1
                if segtree[r] < res:
                    res = segtree[r]
            l >>= 1 
            r >>= 1 
        ans[i] = res
    return ans

def lcp_query(segtree, queries):
    return _lcp_query(*segtree, queries)

def _levenshtein(string_t[::1] a not None, string_t[::1] b not None):
    cdef ull n, m, i, j, d
    n = len(a)
    m = len(b)
    cdef np.ndarray[np.uint64_t, ndim=2] temp = np.empty((n+1, m+1), dtype=np.uint64)
    for i in range(n):
        temp[i][0] = i
    for j in range(m):
        temp[0][j] = j
    for i in range(n):
        for j in range(m):
            temp[i+1][j+1] = min(temp[i][j+1] + 1, temp[i+1][j] + 1, temp[i][j] + (a[i] != b[j]))
    return temp[n][m]


def levenshtein(a, b):
    a = handle_input(a)
    b = handle_input(b)
    if isinstance(a, bytes):
        # tofix
        a = bytearray(a)
    if isinstance(b, bytes):
        # tofix
        b = bytearray(b)
    return _levenshtein(a, b)

from libcpp.pair cimport pair
from libcpp.vector cimport vector
from libcpp.map cimport map as cpp_map
from libcpp.algorithm cimport sort

# TODO: in Cython 0.30 reverse can be imported from libcpp.algorithm
cdef extern from "<algorithm>" namespace "std" nogil:
    void reverse[Iter](Iter first, Iter last) except +


def most_frequent_substrings(
    np.ndarray[sa_t, ndim=1] lcp not None,
    sa_t length,
    sa_t limit = 0,
    sa_t minimum_count = 1
    ):
    """
    Find the most frequent substrings of a given length in a string.
    If `limit` is not 0, only the `limit` most frequent substrings are returned.
    If `minimum_count` is not 1, only the substrings that occur at least `minimum_count` times are returned.

    Parameters
    ----------

    lcp : np.ndarray
        LCP array
    length : int
        length of the substrings to compare
    limit : int (default 0)
        number of substrings to extract, 0 for all of them
    minimum_count : int (default 1)
        ignore the substrings that occur less than `minimum_count` times
    

    Returns
    -------
    positions : np.ndarray
        position in the suffix array
    counts : np.ndarray
        number of occurrences, decreasing
    """
    # TODO: test
    # TODO: clean <https://stackoverflow.com/q/61176636/5133167>

    cdef ull n, i, cur, cur_count, last    
    cdef vector[pair[sa_t, sa_t]] count
    
    if minimum_count < 1:
        minimum_count = 1

    n = len(lcp)
    cur = 0
    cur_count = 1
    for i in range(n-1):
        if lcp[i] >= length:
            cur_count += 1
        else:
            if cur_count >= minimum_count:
                count.push_back((cur_count, cur))
            cur = i + 1
            cur_count = 1
    if cur_count >= minimum_count:
        count.push_back((cur_count, cur))

    sort(count.begin(), count.end())
    reverse(count.begin(), count.end())
    if limit and limit < count.size():
        count.resize(limit)
    
    n = count.size()
    cdef np.ndarray[sa_t, ndim=1] pos = np.empty(n, dtype=lcp.dtype) 
    cdef np.ndarray[sa_t, ndim=1] cnt = np.empty(n, dtype=lcp.dtype) 

    for i in range(n):
        pos[i] = count[i].second
        cnt[i] = count[i].first

    return pos, cnt


cpdef repeated_substrings(ull[::1] suffix_array, ull[::1] lcp):
    """
    See https://github.com/louisabraham/pydivsufsort/issues/42 for more details
    
    Parameters
    ----------
    suffix_array : np.ndarray
        suffix array
    lcp : np.ndarray
        LCP array
    
    Returns
    -------
    ranges : list
        list of (start, end, length) tuples
        All positions in suffix_array[start:end] correspond to
        the same repeated substring with that length.
    """
    cdef vector[pair[ull, ull]] stack
    cdef pair[ull, ull] key
    cdef ull n, idx, end_pos, len_range, start, length
    cdef list ans = []
    n = len(lcp)
    for idx in range(n):
        if stack.empty() or lcp[idx] > stack.back().first:
            if lcp[idx] > 0:
                stack.push_back((lcp[idx], idx))
        else:
            while not stack.empty() and lcp[idx] < stack.back().first:
                length, start = stack.back()
                stack.pop_back()
                ans.append((start, idx + 1, length))

            if stack.empty() and lcp[idx] > 0 or lcp[idx] > stack.back().first:
                stack.push_back((lcp[idx], start))
    # stack is empty because lcp[n-1] == 0
    # note: lcp[n-2] is also 0 because of sep

    return ans


def _common_substrings(np.ndarray[ull, ndim=1] suffix_array, ull[::1] lcp, ull len1, ull limit):
    n = len(suffix_array)
    ranges = repeated_substrings(suffix_array, lcp)
    # origin_cumsum can be use to check faster that
    # a range contains only suffixes from s1 or s2
    cdef char [::1] origin = suffix_array < len1
    cdef np.ndarray[ull, ndim=1] origin_cumsum = np.empty(n + 1, dtype=np.uint64)
    origin_cumsum[0] = 0
    origin_cumsum[1:] = np.cumsum(origin)

    cdef cpp_map[pair[ull, ull], ull] ans
    cdef vector[np.uint64_t] start1, start2
    ranges.sort(key=lambda x: x[2]) # sort to avoid membership test
    cdef ull start, end, length, diff, i, j, l
    for start, end, length in ranges:
        if length < limit:
            continue
        diff = origin_cumsum[end] - origin_cumsum[start]
        if diff == 0 or diff == end - start:
            continue
        start1.clear()
        start2.clear()
        for i in range(start, end):
            pos = suffix_array[i]
            if origin[i]: # might be faster than pos < len1 thanks to cache lookup
                start1.push_back(pos)
            else:
                start2.push_back(pos - len1 - 1)
        sort(start1.begin(), start1.end())
        sort(start2.begin(), start2.end())
        for i in start1:
            for j in start2:
                # deduplicate start positions
                # needed first to remove smaller matches
                ans[i, j] = length
    
    # deduplicate end positions
    cdef cpp_map[pair[ull, ull], ull] ans1
    for (i, j), l in ans:
        i += l
        j += l
        if ans1[i, j] < l:
            ans1[i, j] = l
    
    ans2 = [(i - l, j - l, l) for (i, j), l in ans1]
    ans2.sort()
    return ans2


cdef inline ull _clip(ull x, ull n):
    if x < n:
        return x
    return x - n


def _min_rotation(string_t[::1] s):
    cdef ull a = 0
    cdef ull n = len(s)
    cdef ull b = 0, i
    while b < n:
        for i in range(n):
            if a + i == b or s[_clip(a + i, n)] < s[_clip(b + i, n)]:
                if i > 1:
                    b += i - 1
                break
            if s[_clip(a + i, n)] > s[_clip(b + i, n)]:
                a = b
                break
        b += 1
    return a


def _min_rotation_bytes(const unsigned char[::1] s):
    cdef ull a = 0
    cdef ull n = len(s)
    cdef ull b = 0, i
    while b < n:
        for i in range(n):
            if a + i == b or s[_clip(a + i, n)] < s[_clip(b + i, n)]:
                if i > 1:
                    b += i - 1
                break
            if s[_clip(a + i, n)] > s[_clip(b + i, n)]:
                a = b
                break
        b += 1
    return a



def min_rotation(s):
    s = handle_input(s)
    if isinstance(s, bytes):
        return _min_rotation_bytes(s)
    return _min_rotation(s)