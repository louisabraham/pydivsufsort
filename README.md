[![PyPI
version](https://badge.fury.io/py/pydivsufsort.svg)](https://badge.fury.io/py/pydivsufsort) [![Build
Status](https://travis-ci.com/louisabraham/pydivsufsort.svg?branch=master)](https://travis-ci.org/louisabraham/pydivsufsort)

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

We provide precompiled wheels for common systems, and a source distribution for Unix systems. Manual compilation on Windows might require some tweaking, please create an issue.

## Usage

```python
from pydivsufsort import divsufsort, kasai

print(divsufsort(b"abcd"))

inp = np.array([1, 4, 2, 4, 5, 2, 2])
sa = divsufsort(inp)
print(kasai(inp, sa))
```

## Testing

```
pytest
```

## Technical details (for performance tweaks)

`libdivsufsort` is compiled in both 32 and 64 bits, as [the 32 bits version is faster](https://github.com/y-256/libdivsufsort/issues/21). `pydivsufsort` automatically chooses to use the 32 bits version when possible (aka when the input size is less than `2**31-1`).

The precompiled libraries use OpenMP. You can disable it by setting the env variable `OMP_NUM_THREADS=1`, and it will yield the same performance as the version compiled without OpenMP

The original `libdivsufsort` only supports char as the base type. `pydivsufsort` can handle arrays of any integer type (even signed), by encoding each element as multiple chars, which makes the computation slower. If your values use an integer type that is bigger than required, but they span over a small contiguous range, `pydivsufsort` will automatically change their type (see [#6](https://github.com/louisabraham/pydivsufsort/issues/6)).

## Acknowledgements

- [Yuta Mori](https://github.com/y-256) for writing [libdivsufsort](https://github.com/y-256/libdivsufsort)
- [Sean Law](http://seanlaw.github.io/) for initiating this project and contributing
