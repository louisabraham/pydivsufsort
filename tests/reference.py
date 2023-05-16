from collections import defaultdict
from itertools import zip_longest, islice
import numpy as np


def _to_int_keys(it):
    """
    it: iterable of keys
    returns: a list with integer keys
    """
    seen = set()
    ls = []
    for e in it:
        if e not in seen:
            ls.append(e)
            seen.add(e)
    ls.sort()
    index = {v: i for i, v in enumerate(ls)}
    return [index[v] for v in it]


def _inverse_array(arr):
    n = len(arr)
    ans = [0] * n
    for i in range(n):
        ans[arr[i]] = i
    return ans


def suffix_array(s):
    """
    suffix array of s
    O(n * log(n)^2)
    """
    n = len(s)
    k = 1
    line = _to_int_keys(s)
    while max(line) < n - 1:
        line = _to_int_keys(
            [
                a * (n + 1) + b + 1
                for (a, b) in zip_longest(line, islice(line, k, None), fillvalue=-1)
            ]
        )
        k <<= 1

    dtype = np.int32 if n <= np.iinfo(np.int32).max else np.int64
    return np.array(_inverse_array(line), dtype=dtype)


def longest_common_prefix(s, i, j):
    """naive longest prefix of positions i and j"""
    n = len(s)
    k = 0
    while max(i, j) + k < n and s[i + k] == s[j + k]:
        k += 1
    return k


def BWT(s, sa=None):
    if isinstance(s, str):
        s = s.encode("ascii")
    if sa is None:
        sa = suffix_array(s)
    pos = _inverse_array(sa)
    sa, pos = pos, sa
    ans = [s[-1]]
    for i in range(len(s)):
        if pos[i] > 0:
            ans.append(s[pos[i] - 1])
        else:
            idx = i + 1
    return idx, ans


def iBWT(idx, b):
    n = len(b)
    last = list(zip(b, range(n)))
    ilast = {}
    for i, e in enumerate(last):
        ilast[e] = i + (i >= idx)
    first = sorted(last)
    ans = []
    c = first[idx - 1]
    while len(ans) < n:
        ans.append(c[0])
        c = first[ilast[c] - 1]
    return ans


def all_common_substrings(s1, s2):
    ans = defaultdict(int)
    for i in range(len(s1)):
        for j in range(len(s2)):
            k = 0
            while i + k < len(s1) and j + k < len(s2) and s1[i + k] == s2[j + k]:
                k += 1
            if k:
                ans[i + k, j + k] = max(ans[i + k, j + k], k)

    return sorted((i - k, j - k, k) for (i, j), k in ans.items())


def min_rotation(s):
    s = list(s)
    return min(range(len(s)), key=lambda i: s[i:] + s[:i])
