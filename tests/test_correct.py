import array
import random

import numpy as np
import pytest

from pydivsufsort import (
    divsufsort,
    kasai,
    lcp_segtree,
    lcp_query,
    bw_transform,
    inverse_bw_transform,
    sa_search,
    levenshtein,
    most_frequent_substrings,
    common_substrings,
    min_rotation,
)
from pydivsufsort.divsufsort import _SUPPORTED_DTYPES, _minimize_dtype

from reference import (
    suffix_array,
    longest_common_prefix,
    BWT,
    iBWT,
    all_common_substrings,
    min_rotation as min_rotation_ref,
)


def cast_to_array(inp):
    out = array.array("B")
    out.frombytes(inp)
    return out


def cast_to_str(inp):
    return bytes(inp).decode()


def cast_to_np_array(inp):
    """cast back any type to an array"""
    if isinstance(inp, str):
        inp = inp.encode("ascii")
    return np.array(list(inp))


CASTS = [bytes, bytearray, cast_to_array, cast_to_str]


def assert_correct(inp, queries=None):
    sa = suffix_array(inp)
    assert (divsufsort(inp) == sa).all(), inp

    segtree = lcp_segtree(inp)
    if queries is None:
        n = len(inp)
        queries = [[0, 0], [0, n - 2], [0, n - 1], [n - 2, n - 2], [n - 1, n - 1]]
    lcp_opt = lcp_query(segtree, queries)
    lcp_naive = [longest_common_prefix(inp, i, j) for i, j in queries]
    assert (lcp_opt == lcp_naive).all(), (inp, lcp_naive, lcp_opt)

    if not (isinstance(inp, np.ndarray) and inp.dtype != np.uint8):
        bwt_opt = bw_transform(inp)
        bwt_opt2 = bw_transform(inp, sa)
        assert bwt_opt[0] == bwt_opt2[0]
        assert (bwt_opt[1] == bwt_opt2[1]).all()
        bwt_naive = BWT(inp)
        assert bwt_opt[0] == bwt_naive[0]
        assert (bwt_opt[1] == bwt_naive[1]).all()
        tr_opt = inverse_bw_transform(*bwt_opt)
        tr_naive = iBWT(*bwt_naive)
        assert (tr_opt == cast_to_np_array(inp)).all(), inp
        assert (tr_opt == tr_naive).all(), inp

    if len(inp) < 100:
        assert min_rotation(inp) == min_rotation_ref(inp)


def randint_type(size, dtype):
    iinfo = np.iinfo(dtype)
    return np.random.randint(iinfo.min, iinfo.max + 1, size=size, dtype=dtype)


def randint_ascii(size):
    return np.random.randint(0, 128, size=size, dtype="uint8")


def random_cast(inp):
    dtype = random.choice(
        [
            d
            for d in ["uint8", "uint16", "uint32", "uint64"]
            if np.dtype(d).itemsize >= inp.dtype.itemsize
        ]
    )
    return inp.astype(dtype)


def random_test(repetitions, size, dtype):
    for _ in range(repetitions):
        inp = randint_type(size, dtype)
        assert_correct(inp)


def test_containers():
    inp = randint_ascii(10)
    for cast in CASTS:
        assert_correct(cast(inp))


def test_small():
    for dtype in _SUPPORTED_DTYPES:
        random_test(20, 10, dtype)


def test_medium():
    for dtype in _SUPPORTED_DTYPES:
        random_test(5, 1_000, dtype)


def test_minimize_dtype():
    for _ in range(1000):
        dtype = random.choice(["uint8", "uint16", "uint32", "uint64"])
        inp = randint_type(100, dtype)
        inp = random_cast(inp)
        assert _minimize_dtype(inp).dtype.itemsize == np.dtype(dtype).itemsize, inp


def test_kasai():
    inp = np.array(list(b"banana"), dtype="uint8")
    out = np.array([1, 3, 0, 0, 2, 0])
    assert (kasai(inp) == out).all()
    for cast in CASTS:
        assert (kasai(cast(inp)) == out).all()


def test_non_contiguous():
    for dtype in _SUPPORTED_DTYPES:
        inp = randint_type(100, dtype)[::2]
        assert_correct(inp)


def test_queries():
    for n in [100] * 10 + [1000] * 10 + [10_000]:
        q = min(n**2, 1_000)
        inp = np.random.randint(3, size=n)
        queries = np.random.randint(n, size=(q, 2))
        assert_correct(inp, queries)


def test_sa_search():
    for n in [4, 100]:
        for _ in range(10):
            inp = np.random.randint(3, size=n, dtype=np.uint8)
            sa = divsufsort(inp)
            isa = np.argsort(sa)
            for m in list(range(1, 5)) * 10:
                query = np.random.randint(3, size=m, dtype=np.uint8)
                matches = [
                    i for i in range(n - m + 1) if (query == inp[i : i + m]).all()
                ]
                count = len(matches)
                if count:
                    left = isa[matches].min()
                    assert (sorted(isa[matches]) == np.arange(left, left + count)).all()
                else:
                    left = None
                assert (count, left) == sa_search(inp, sa, query)


def test_levenshtein():
    assert levenshtein("kitten", "sitting") == 3


def test_mfs():
    s = "ababababa"
    sa = divsufsort(s)
    lcp = kasai(s, sa)
    pos, cnt = most_frequent_substrings(lcp, 3, limit=2)
    assert (sa[pos] == [6, 5]).all()
    assert (cnt == [4, 3]).all()


def test_common_substrings():
    s1 = "ananas"
    s2 = "banana"
    ans = common_substrings(s1, s2, limit=2)
    assert ans == [(0, 1, 5), (0, 3, 3), (2, 1, 3)]

    size = 5
    for _ in range(100):
        s1 = np.random.randint(0, 4, size=size, dtype="uint8")
        s2 = np.random.randint(0, 4, size=size, dtype="uint8")
        assert common_substrings(s1, s2, limit=1) == all_common_substrings(s1, s2), (
            s1,
            s2,
        )


def test_warnings_errors():
    with pytest.warns(UserWarning):
        divsufsort("a" * 1000)
    import ctypes

    # creates ctypes array

    s = (ctypes.c_char * 6)()
    s[:] = b"banana"
    with pytest.warns(UserWarning):
        assert np.alltrue(divsufsort(s) == np.array([5, 3, 1, 0, 4, 2]))

    with pytest.raises(TypeError):
        divsufsort("é")

    with pytest.raises(TypeError):
        divsufsort(np.array([0.0]))

    with pytest.raises(TypeError):
        bw_transform(np.array([0]))


def test64():
    s = "banana"
    sa = divsufsort(s, force64=True)
    assert sa.dtype == np.int64
    assert (sa == divsufsort(s)).all()

    bwt = bw_transform(s, force64=True)
    tr = inverse_bw_transform(*bwt, force64=True)
    assert (tr == np.array(list(s.encode("ascii")))).all()

    res = sa_search(s, sa, "an")
    assert res == (2, 1)
