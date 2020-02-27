import array
from functools import partial
import random

from pydivsufsort import divsufsort
from pydivsufsort.divsufsort import _SUPPORTED_DTYPES, _minimize_dtype
from reference import suffix_array
import numpy as np


def cast_to_array(inp):
    out = array.array("B")
    out.frombytes(inp)
    return out


CASTS = [bytes, bytearray, cast_to_array]


def assert_correct(inp):
    assert (divsufsort(inp) == suffix_array(inp)).all(), inp


def randint_type(size, dtype):
    iinfo = np.iinfo(dtype)
    return np.random.randint(iinfo.min, iinfo.max, size=size, dtype=dtype)


def random_cast(inp):
    dtype = random.choice(
        [
            d
            for d in ["uint8", "uint16", "uint32", "uint64"]
            if np.dtype(d).itemsize >= inp.dtype.itemsize
        ]
    )
    return inp.astype(dtype)


def random_shift(inp):
    return inp + randint_type(1, inp.dtype)


def random_test(repetitions, size, dtype):
    for _ in range(repetitions):
        inp = randint_type(size, dtype)
        assert_correct(inp)


def test_containers():
    inp = randint_type(10, np.uint8)
    for cast in CASTS:
        assert_correct(cast(inp))


def test_small():
    for dtype in _SUPPORTED_DTYPES:
        random_test(100, 10, dtype)


def test_medium():
    for dtype in _SUPPORTED_DTYPES:
        random_test(5, 1_000, dtype)


def test_casts():
    for _ in range(1000):
        dtype = random.choice(["uint8", "uint16", "uint32", "uint64"])
        inp = randint_type(10, dtype)
        inp = random_shift(inp)
        inp = random_cast(inp)
        assert _minimize_dtype(inp).dtype.itemsize == np.dtype(dtype).itemsize, inp
