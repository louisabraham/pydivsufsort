import array
from functools import partial


from pydivsufsort import divsufsort
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


test_small = partial(random_test, 1000, 10, np.uint8)


def test_containers():
    inp = random_type(10, np.uint8)
    for cast in CASTS:
        assert_correct(cast(inp))


test_medium = partial(random_test, 10, 10_000, np.uint8)


def test_small_bigint():
    for dtype in [np.uint16, np.uint32, np.uint64]:
        random_test(1000, 10, np.uint8)


def test_big_bigint():
    for dtype in [np.uint16, np.uint32, np.uint64]:
        random_test(10, 10_000, np.uint8)
