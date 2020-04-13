import numpy as np
from pydivsufsort import WonderString


def test():
    s = WonderString("abcdabcd")
    assert s.lcp(0, 4) == 4
    assert s.search("bc").count == 2
    assert set(s.search("bc", True)) == {1, 5}
    assert np.array_equal(s.most_frequent_substrings(length=4, limit=1), ([4], [2]))
