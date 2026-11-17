import array
import random

import numpy as np
import pytest
from reference import BWT, all_common_substrings, iBWT, longest_common_prefix
from reference import min_rotation as min_rotation_ref
from reference import suffix_array

from pydivsufsort import (
    bw_transform,
    common_substrings,
    divsufsort,
    inverse_bw_transform,
    kasai,
    kmp_censor_stream,
    lcp_query,
    lcp_segtree,
    lempel_ziv_complexity,
    lempel_ziv_factorization,
    levenshtein,
    longest_previous_factor,
    min_rotation,
    most_frequent_substrings,
    sa_search,
)
from pydivsufsort.divsufsort import _SUPPORTED_DTYPES, _minimize_dtype


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

    bwt_opt = bw_transform(inp)
    bwt_opt2 = bw_transform(inp, sa)
    assert bwt_opt[0] == bwt_opt2[0]
    assert (bwt_opt[1] == bwt_opt2[1]).all()
    bwt_naive = BWT(inp, sa)
    assert bwt_opt[0] == bwt_naive[0]
    assert (bwt_opt[1] == bwt_naive[1]).all()
    tr_opt = inverse_bw_transform(*bwt_opt)
    tr_naive = iBWT(*bwt_naive)
    assert (tr_opt == cast_to_np_array(inp)).all(), inp
    assert (tr_opt == tr_naive).all(), inp
    if isinstance(inp, np.ndarray):
        assert bwt_opt[1].dtype == inp.dtype
        assert tr_opt.dtype == inp.dtype

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


def test_sa_search_dtypes():
    for n in [0, 1, 50]:
        inp = np.random.randint(3, size=n).astype(np.uint8)
        for dtype in _SUPPORTED_DTYPES:
            s = inp.astype(dtype)
            sa = divsufsort(inp)
            for m in list(range(4)) * 5:
                query = np.random.randint(3, size=m).astype(np.uint8)
                matches = [
                    i for i in range(n - m + 1) if (query == inp[i : i + m]).all()
                ]
                expected = sa_search(inp, sa, query)
                if m == 0:
                    # every suffix begins with the empty pattern
                    assert expected == (n, 0 if n else None)
                else:
                    assert expected[0] == len(matches)
                assert sa_search(s, sa, query) == expected
                assert sa_search(s, sa, query.astype(dtype)) == expected
                assert sa_search(s, sa, query.astype(np.int64)) == expected
                assert sa_search(s, sa, list(query)) == expected

    # the values of the pattern are compared, not its bytes
    s = b"banana"
    sa = divsufsort(s)
    assert sa_search(s, sa, np.array([97, 110])) == (2, 1)
    assert sa_search(s, sa, np.array([97, 1000])) == (0, None)
    assert sa_search(s, sa, np.array([-159, 110])) == (0, None)
    s = np.array([1000, 0, 1000, 0], dtype=np.uint16)
    assert sa_search(s, divsufsort(s), "a") == (0, None)
    assert sa_search(s, divsufsort(s), [1000, 0]) == (2, 2)
    assert sa_search(s, divsufsort(s).astype(np.int64), [1000, 0]) == (2, 2)

    with pytest.raises(ValueError):
        sa_search(s, np.array([0, 1, 2, 4], dtype=np.int32), [1000])
    for s in [b"banana", np.array([1000, 0, 1000, 0], dtype=np.uint16)]:
        sa = divsufsort(s)
        with pytest.raises(ValueError):
            sa_search(s, np.concatenate([sa, sa]), s[:1])
        with pytest.raises(TypeError):
            sa_search(s, sa.astype(np.uint32), s[:1])


def test_sa_search_sparse():
    """Sorted subsets of the suffix array (sparse suffix arrays)"""
    n = 60
    inp = np.random.randint(3, size=n).astype(np.uint8)
    sa = divsufsort(inp)
    subsets = [sa[sa % 2 == 0], sa[sa % 7 == 3], sa[:5], sa[-3:], sa[:0]]
    for dtype in _SUPPORTED_DTYPES:
        s = inp.astype(dtype)
        for sparse in subsets:
            for sa_dtype in [np.int32, np.int64]:
                sparse = sparse.astype(sa_dtype)
                for m in [1, 2, 3] * 5:
                    query = np.random.randint(3, size=m).astype(np.uint8)
                    matches = {
                        i for i in sparse if np.array_equal(inp[i : i + m], query)
                    }
                    count, left = sa_search(s, sparse, query)
                    assert count == len(matches)
                    if count:
                        assert set(sparse[left : left + count]) == matches
                    else:
                        assert left is None


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
        assert np.all(divsufsort(s) == np.array([5, 3, 1, 0, 4, 2]))

    with pytest.raises(TypeError):
        divsufsort("é")

    with pytest.raises(TypeError):
        divsufsort(np.array([0.0]))

    with pytest.raises(TypeError):
        bw_transform(np.array([0.0]))

    with pytest.raises(TypeError):
        inverse_bw_transform(1, np.array([0.0]))


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

    # 64-bit suffix array with the 32-bit version of libdivsufsort
    assert bw_transform(s, sa)[0] == bw_transform(s)[0]
    assert (bw_transform(s, sa)[1] == bw_transform(s)[1]).all()

    inp = np.array([1000, 0, 2000, 0], dtype=np.uint16)
    bwt = bw_transform(inp, force64=True)
    assert (bwt[1] == bw_transform(inp)[1]).all()
    assert (bwt[1] == bw_transform(inp, divsufsort(inp).astype(np.int64))[1]).all()
    assert (inverse_bw_transform(*bwt, force64=True) == inp).all()


def test_lpf():
    s = "abbaabbbaaabab"
    lpf = longest_previous_factor(s)
    assert (lpf == np.array([0, 0, 1, 1, 3, 2, 4, 3, 2, 3, 2, 2, 2, 1])).all()


def test_lz():
    s = "abbaabbbaaabab"
    lz = lempel_ziv_factorization(longest_previous_factor(s))
    # a b b a abb baa ab ab
    assert lz == [0, 1, 2, 3, 4, 7, 10, 12, 14]

    s = "1001111011000010"
    lz = lempel_ziv_factorization(longest_previous_factor(s))
    # 1 0 0 1 111 011 00 001 0
    assert lz == [0, 1, 2, 3, 4, 7, 10, 12, 15, 16]
    # 1 0 01 1110 1100 0010
    assert lempel_ziv_complexity("1001111011000010") == 6

    assert lempel_ziv_complexity("") == 0
    assert lempel_ziv_complexity("0001") == 2
    assert lempel_ziv_complexity("010") == 3


def test_kmp_censor_stream():
    assert list(kmp_censor_stream("an", "banana")) == ["b", "a"]
    assert list(kmp_censor_stream("an", ["ba", "na", "na"])) == ["b", "a"]
    assert list(kmp_censor_stream("nan", "banana")) == ["b", "a", "a"]
    assert list(kmp_censor_stream("nan", "bananana")) == ["b", "a", "a"]

    out = list(kmp_censor_stream("a", ["ba", "naba", "na"]))
    assert len(out) == 3
    assert "".join(out) == "bnbn"

    out = list(kmp_censor_stream("a", "bonne journée"))


def test_bwt_wide_dtypes():
    # same result as the uint8 version of libdivsufsort
    for _ in range(20):
        inp = randint_ascii(50) % 4
        idx, bwt = bw_transform(inp)
        for dtype in _SUPPORTED_DTYPES:
            idx2, bwt2 = bw_transform(inp.astype(dtype))
            assert idx2 == idx
            assert (bwt2 == bwt).all()
            assert (inverse_bw_transform(idx2, bwt2) == inp).all()

    # values that do not fit in one byte
    inp = np.array([-(2**63), 2**63 - 1, -1, 0, 2**63 - 1, -(2**63)], dtype=np.int64)
    assert (inverse_bw_transform(*bw_transform(inp)) == inp).all()
    inp = np.array([2**64 - 1, 0, 2**64 - 1, 2**32], dtype=np.uint64)
    assert (inverse_bw_transform(*bw_transform(inp)) == inp).all()


def test_bwt_edge_cases():
    for dtype in _SUPPORTED_DTYPES:
        for n in range(4):
            for inp in [np.zeros(n, dtype=dtype), np.arange(n, dtype=dtype)]:
                idx, bwt = bw_transform(inp)
                assert idx == (n and BWT(inp)[0])
                assert bwt.dtype == inp.dtype
                tr = inverse_bw_transform(idx, bwt)
                assert tr.dtype == inp.dtype
                assert (tr == inp).all()


def test_bwt_invalid():
    for bwt in [b"ab", np.array([1, 2], dtype=np.uint16)]:
        for idx in [-1, 0, 3]:
            with pytest.raises(ValueError):
                inverse_bw_transform(idx, bwt)
    for bwt in [b"", np.array([], dtype=np.uint16)]:
        with pytest.raises(ValueError):
            inverse_bw_transform(1, bwt)

    # rows 0 -> 2 -> 0 and 1 -> 1 form two cycles: not a valid transform
    with pytest.raises(ValueError):
        inverse_bw_transform(2, np.array([1, 0], dtype=np.uint16))

    inp = np.array([1, 2, 3], dtype=np.uint16)
    for sa in [
        np.array([1, 2], dtype=np.int32),
        np.array([1, 2, 3], dtype=np.int32),
        np.array([0, 4, 1], dtype=np.int64),
        np.array([0, -1, 1], dtype=np.int64),
    ]:
        with pytest.raises(ValueError):
            bw_transform(inp, sa)
