[![PyPI
version](https://badge.fury.io/py/pydivsufsort.svg)](https://badge.fury.io/py/pydivsufsort) [![Test](https://github.com/louisabraham/pydivsufsort/actions/workflows/test.yml/badge.svg)](https://github.com/louisabraham/pydivsufsort/actions/workflows/test.yml) [![Build and upload](https://github.com/louisabraham/pydivsufsort/actions/workflows/build-and-upload.yml/badge.svg)](https://github.com/louisabraham/pydivsufsort/actions/workflows/build-and-upload.yml) [![codecov](https://codecov.io/gh/louisabraham/pydivsufsort/branch/master/graph/badge.svg?token=A1BM9U1OLV)](https://codecov.io/gh/louisabraham/pydivsufsort)

# `pydivsufsort`: bindings to libdivsufsort

`pydivsufsort` prebuilds `libdivsufsort` as a shared library and
includes it in a Python package with bindings.

**Features**:

- bindings to `divsufsort` that return numpy arrays
- handle almost any integer data type (e.g. `int64`) and not only `char`
- additional string algorithms

## Installation

On Linux, macOS and Windows:

```
python -m pip install pydivsufsort
```

We provide precompiled wheels for common systems using `cibuildwheel`, and a source distribution for Unix systems. Manual compilation on Windows might require some tweaking, please create an issue.

## Usage

### Using String Inputs

```python
import numpy as np
from pydivsufsort import divsufsort, kasai

string_inp = "banana$"
string_suffix_array = divsufsort(string_inp)
string_lcp_array = kasai(string_inp, string_suffix_array)
print(string_suffix_array, string_lcp_array)
# [6 5 3 1 0 4 2] [0 1 3 0 0 2 0]
```

### Using Integer Inputs

```python
import numpy as np
from pydivsufsort import divsufsort, kasai

string_inp = "banana$"

# Convert the string input to integers first
int_inp = np.unique(np.array(list(string_inp)), return_inverse=True)[1]
int_suffix_array = divsufsort(int_inp)
int_lcp_array = kasai(int_inp, int_suffix_array)
print(int_suffix_array, int_lcp_array)
# [6 5 3 1 0 4 2] [0 1 3 0 0 2 0]
```

### Using Multiple Sentinel Characters Witin A String

```python
import numpy as np
from pydivsufsort import divsufsort, kasai

sentinel_inp = "a$banana#and@a*bandana+"
sentinel_suffix_array = divsufsort(sentinel_inp)
sentinel_lcp_array = kasai(sentinel_inp, sentinel_suffix_array)
print(sentinel_suffix_array, sentinel_lcp_array)
# [ 8  1 14 22 12  7  0 13 21  5 19  3  9 16  2 15 11 18  6 20  4 10 17] [0 0 0 0 0 1 1 1 1 3 3 2 3 0 3 0 1 0 2 2 1 2 0]
```


## Development

You can install locally with

```
pip install -e .
```

Note: on my M1 machine that uses a x86 version of Python, I have to launch `arch -x86_64 ./build.sh` to build `libdivsufsort` for the correct architecture.


## Testing

```
pytest
```

## Technical details (for performance tweaks)

`libdivsufsort` is compiled in both 32 and 64 bits, as [the 32 bits version is faster](https://github.com/y-256/libdivsufsort/issues/21). `pydivsufsort` automatically chooses to use the 32 bits version when possible (aka when the input size is less than `2**31-1`).

For best performance, use contiguous arrays. If you have a sliced array, pydivsufsort converts it automatically with [`numpy.ascontiguousarray`](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ascontiguousarray.html).

The precompiled libraries use OpenMP. You can disable it by setting the env variable `OMP_NUM_THREADS=1`, and it will yield the same performance as the version compiled without OpenMP

The original `libdivsufsort` only supports char as the base type. `pydivsufsort` can handle arrays of any integer type (even signed), by encoding each element as multiple chars, which makes the computation slower. If your values use an integer type that is bigger than required, but they span over a small contiguous range, `pydivsufsort` will automatically change their type (see [#6](https://github.com/louisabraham/pydivsufsort/issues/6)).

## Acknowledgements

- [Yuta Mori](https://github.com/y-256) for writing [libdivsufsort](https://github.com/y-256/libdivsufsort)
- [Sean Law](http://seanlaw.github.io/) for initiating this project and contributing
