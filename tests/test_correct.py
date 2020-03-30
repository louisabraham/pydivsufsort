import array
from functools import partial
import random

import numpy as np

from pydivsufsort import divsufsort
from pydivsufsort.divsufsort import _SUPPORTED_DTYPES, _minimize_dtype
from pydivsufsort import kasai

from reference import suffix_array


def cast_to_array(inp):
    out = array.array("B")
    out.frombytes(inp)
    return out


def cast_to_str(inp):
    return bytes(inp).decode()


CASTS = [bytes, bytearray, cast_to_array, cast_to_str]


def assert_correct(inp):
    sa = suffix_array(inp)
    assert (divsufsort(inp) == sa).all(), inp
    kasai(inp)
    kasai(inp, sa)


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
        random_test(100, 10, dtype)


def test_medium():
    for dtype in _SUPPORTED_DTYPES:
        random_test(5, 1_000, dtype)


def test_minimize_dtype():
    for _ in range(10000):
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
