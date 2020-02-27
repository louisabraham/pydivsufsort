from itertools import zip_longest, islice
import numpy as np


def _to_int_keys(l):
    """
    l: iterable of keys
    returns: a list with integer keys
    """
    seen = set()
    ls = []
    for e in l:
        if not e in seen:
            ls.append(e)
            seen.add(e)
    ls.sort()
    index = {v: i for i, v in enumerate(ls)}
    return [index[v] for v in l]


def _inverse_array(l):
    n = len(l)
    ans = [0] * n
    for i in range(n):
        ans[l[i]] = i
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
    if n <= np.iinfo(np.int32).max:
        dtype = np.int32
    else:
        dtype = np.int64
    return np.array(_inverse_array(line), dtype=dtype)
