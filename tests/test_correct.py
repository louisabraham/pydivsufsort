import array
from functools import partial


from pydivsufsort import divsufsort
from pydivsufsort.divsufsort import _SUPPORTED_DTYPES
from reference import suffix_array
import numpy as np


def cast_to_array(inp):
    out = array.array("B")
    out.frombytes(inp)
    return out


CASTS = [bytes, bytearray, cast_to_array]


def assert_correct(inp):
    assert (divsufsort(inp) == suffix_array(inp)).all(), inp


def random_type(size, dtype):
    iinfo = np.iinfo(dtype)
    return np.random.randint(iinfo.min, iinfo.max, size=size, dtype=dtype)


def random_test(repetitions, size, dtype):
    for _ in range(repetitions):
        inp = random_type(size, dtype)
        assert_correct(inp)


def test_containers():
    inp = random_type(10, np.uint8)
    for cast in CASTS:
        assert_correct(cast(inp))


def test_small():
    for dtype in _SUPPORTED_DTYPES:
        random_test(100, 10, dtype)


def test_medium():
    for dtype in _SUPPORTED_DTYPES:
        random_test(5, 1_000, dtype)
