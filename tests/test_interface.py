import numpy as np
from pydivsufsort import WonderString
import pytest


def test_base():
    s = WonderString("abcdabcd")
    assert s.lcp(0, 4) == 4
    assert s.lcp([(0, 4)]) == 4
    assert s.search("bc").count == 2
    assert set(s.search("bc", True)) == {1, 5}
    assert s.search("cb", True).size == 0
    assert np.array_equal(s.most_frequent_substrings(length=4, limit=1), ([4], [2]))


def test_exceptions():
    with pytest.raises(TypeError):
        WonderString("abcdabcdé")
    with pytest.raises(NotImplementedError):
        s = WonderString(np.array([0, 256]))
        s.search(np.array([0]))


def test_larger_dtype():
    a = np.array([0, 256, 0, 256], np.uint16)
    s = WonderString(a)
    assert s.lcp(0, 2) == 2
