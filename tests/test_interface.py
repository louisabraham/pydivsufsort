import numpy as np
import pytest
from reference import longest_common_prefix, suffix_array

from pydivsufsort import WonderString
from pydivsufsort.divsufsort import _SUPPORTED_DTYPES


def test_base():
    s = WonderString("abcdabcd")
    assert s.lcp(0, 4) == 4
    assert s.lcp([(0, 4)]) == 4
    assert s.search("bc").count == 2
    assert set(s.search("bc", True)) == {1, 5}
    assert s.search("cb", True).size == 0
    assert np.array_equal(s.most_frequent_substrings(length=4, limit=1), ([4], [2]))


def test_cache():
    s = WonderString("abcdabcd")
    assert s.suffix_array is s.suffix_array
    assert s.lcp_array is s.lcp_array
    assert s._lcp_segtree is s._lcp_segtree


def test_exceptions():
    with pytest.raises(TypeError):
        WonderString("abcdabcdé")
    with pytest.raises(TypeError):
        WonderString(np.array([0, 256])).search(np.array([0.0]))


def test_larger_dtype():
    a = np.array([0, 256, 0, 256], np.uint16)
    s = WonderString(a)
    assert s.lcp(0, 2) == 2
    pat = np.array([0, 256], np.uint16)
    ans = s.search(pat, return_positions=True)
    assert sorted(ans) == [0, 2]
    a = np.array([257, 257], np.uint16)
    s = WonderString(a)
    pat = np.array([257], np.uint16)
    ans = s.search(pat, return_positions=True)
    assert sorted(ans) == [0, 1]


def test_all_dtypes():
    """Same results as with uint8, for all integer dtypes"""
    rng = np.random.default_rng(0)
    for _ in range(20):
        x = rng.integers(0, 3, 30, dtype=np.uint8)
        ref = WonderString(x)
        queries = rng.integers(0, len(x), (10, 2))
        patterns = [rng.integers(0, 3, m, dtype=np.uint8) for m in range(4)]
        for dtype in _SUPPORTED_DTYPES:
            s = WonderString(x.astype(dtype))
            assert (s.suffix_array == ref.suffix_array).all()
            assert (s.lcp_array == ref.lcp_array).all()
            assert (s.lcp(queries) == ref.lcp(queries)).all()
            mfs = s.most_frequent_substrings(2)
            assert np.array_equal(mfs, ref.most_frequent_substrings(2))
            for pattern in patterns:
                assert s.search(pattern.astype(dtype)) == ref.search(pattern)
                assert s.search(pattern) == ref.search(pattern)


def test_wide_values():
    """Values that do not fit in one byte, compared with naive results"""
    rng = np.random.default_rng(0)
    for dtype in _SUPPORTED_DTYPES:
        info = np.iinfo(dtype)
        alphabet = {int(info.min), int(info.min) + 1, 0, 1, 255, int(info.max)}
        alphabet = np.array(sorted(v for v in alphabet if v <= info.max), dtype)
        x = alphabet[rng.integers(0, len(alphabet), 40)]
        s = WonderString(x)
        sa = suffix_array(x)
        assert (s.suffix_array == sa).all()
        lcp = [longest_common_prefix(x, i, j) for i, j in zip(sa, sa[1:])] + [0]
        assert (s.lcp_array == lcp).all()
        for _ in range(20):
            i = rng.integers(len(x))
            pattern = x[i : i + rng.integers(1, 4)]
            m = len(pattern)
            positions = [
                j for j in range(len(x) - m + 1) if (x[j : j + m] == pattern).all()
            ]
            assert s.search(pattern).count == len(positions)
            assert sorted(s.search(pattern, return_positions=True)) == positions

        if info.bits < 64:
            # a value that does not fit in dtype must not wrap around
            pattern = np.array([int(x[0]) + 2**info.bits], dtype=np.int64)
            assert s.search(pattern) == (0, None)
