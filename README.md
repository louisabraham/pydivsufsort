[![PyPI
version](https://badge.fury.io/py/pydivsufsort.svg)](https://badge.fury.io/py/pydivsufsort) [![Build
Status](https://travis-ci.org/louisabraham/pydivsufsort.svg?branch=master)](https://travis-ci.org/louisabraham/pydivsufsort)

# `pydivsufsort`: bindings to libdivsufsort

`pydivsufsort` prebuilds `libdivsufsort` as a shared library and
includes it in a Python package with bindings.

## Installation

On Linux and macOS:
```
python -m pip install pydivsufsort
```

Untested on Windows.

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
- [Sean Law](https://github.com/seanlaw) for initiating this project and contributing