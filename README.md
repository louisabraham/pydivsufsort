[![PyPI
version](https://badge.fury.io/py/pydivsufsort.svg)](https://badge.fury.io/py/pydivsufsort) [![Downloads](https://pepy.tech/badge/pydivsufsort)](https://pepy.tech/project/pydivsufsort) [![Test](https://github.com/louisabraham/pydivsufsort/actions/workflows/test.yml/badge.svg)](https://github.com/louisabraham/pydivsufsort/actions/workflows/test.yml) [![Build and upload](https://github.com/louisabraham/pydivsufsort/actions/workflows/build-and-upload.yml/badge.svg)](https://github.com/louisabraham/pydivsufsort/actions/workflows/build-and-upload.yml) [![codecov](https://codecov.io/gh/louisabraham/pydivsufsort/branch/master/graph/badge.svg?token=A1BM9U1OLV)](https://codecov.io/gh/louisabraham/pydivsufsort) [![DOI](https://zenodo.org/badge/241137939.svg)](https://zenodo.org/badge/latestdoi/241137939)

# `pydivsufsort`: bindings to libdivsufsort

`pydivsufsort` prebuilds `libdivsufsort` as a shared library and
includes it in a Python package with bindings. Wheels are built for Linux, macOS and Windows (32 and 64 bits) using `cibuildwheel` and GitHub Actions. Basically, you should be able to install it with `pip install pydivsufsort` on any system and it should work out of the box. If it doesn't, please create an issue.

**Features**:

- bindings to `divsufsort` that return numpy arrays
- handle string, bytes and almost any integer data type (e.g. `int64`) and not only `char`
- algorithms work even for non char inputs
- additional string algorithms coded in Cython

## Installation

On Linux, macOS and Windows:

```
python -m pip install pydivsufsort
```

We provide precompiled wheels for common systems using `cibuildwheel`, and a source distribution for Unix systems. Manual compilation on Windows might require some tweaking, please create an issue.

## Features

All methods support string, bytes and numpy array inputs, including datatypes greater than `uint8_t` (e.g. `uint64_t`). Below are the signatures of all methods exposed by `pydivsufsort`. To import a method, just do `from pydivsufsort import method_name`. All methods are documented in the docstrings. You can display them with `help(method_name)`.

A nicer interface to reuse computations lazily is provided in WonderString but currently undocumented. Please create an issue if you are interested.

### Methods exposed from libdivsufsort

- `divsufsort(string)`: suffix array
- `bw_transform(string)`: Burrows-Wheeler transform
- `inverse_bw_transform(idx, string)`: inverse Burrows-Wheeler transform
- `sa_search(string, suffix_array, pattern)`: search for a pattern in a suffix array


### Additional string algorithms

- `kasai(string, suffix_array=None)`: LCP array computation (lazily computes the suffix array if not provided)
- `lcp_segtree(string, suffix_array=None, lcp=None)`: build a segment tree for LCP queries (lazily computes the suffix array and LCP array if not provided)
- `lcp_query(segtree, queries)`: query a segment tree for LCP queries. Queries are pairs of indices.
- `levenshtein(string1, string2)`: Levenshtein distance
- `most_frequent_substrings(lcp, length, limit=0, minimum_count=1)`: most frequent substrings. See the docstring for details.
- `common_substrings(string1, string2, limit=25)`: common substrings between two strings.
- `min_rotation(string)`: minimum rotation of a string

### Example usage

```python
from pydivsufsort import divsufsort, kasai

string_inp = "banana$"
string_suffix_array = divsufsort(string_inp)
string_lcp_array = kasai(string_inp, string_suffix_array)
print(string_suffix_array, string_lcp_array)
# [6 5 3 1 0 4 2] [0 1 3 0 0 2 0]

# You can also convert the string input to integers first

import numpy as np

int_inp = np.unique(np.array(list(string_inp)), return_inverse=True)[1]
int_suffix_array = divsufsort(int_inp)
int_lcp_array = kasai(int_inp, int_suffix_array)
print(int_suffix_array, int_lcp_array)
# [6 5 3 1 0 4 2] [0 1 3 0 0 2 0]
```


## Development

You can install locally with

```
pip install -e .
```

A useful command to iterate quickly when changing Cython code is

```
python setup.py build_ext --inplace && pytest -s
```

### Profiling

Profiling can be activated with the environment variable `PROFILE`:

```
PROFILE=1 python setup.py build_ext --inplace && pytest -s
```

Here is an example with line_profiler (requires `pip install "line_profiler<4"`):

```
import line_profiler
from pydivsufsort import common_substrings
from pydivsufsort.stringalg import (
    _common_substrings,
    repeated_substrings,
)

s1 = "banana" * 10000
s2 = "ananas" * 10000

func = common_substrings
profile = line_profiler.LineProfiler(func)
profile.add_function(_common_substrings)
profile.add_function(repeated_substrings)
profile.runcall(func, s1, s2, limit=15)
profile.print_stats()
```

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

## Citing

If you have used this software in a scientific publication, please cite it using the following BibLaTeX code:

```
@software{pydivsufsort,
  author       = {Louis Abraham},
  title        = {pydivsufsort},
  year         = 2023,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.7932458},
  url          = {https://github.com/louisabraham/pydivsufsort}
}
```