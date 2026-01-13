# simde-py

[![PyPI version](https://badge.fury.io/py/simde-py.svg)](https://badge.fury.io/py/simde-py)
[![Python Versions](https://img.shields.io/pypi/pyversions/simde-py.svg)](https://pypi.org/project/simde-py/)

Python package providing [SIMD Everywhere (SIMDe)](https://github.com/simd-everywhere/simde) header files for building Python C extensions with portable SIMD intrinsics.

SIMDe is a header-only C library that provides fast, portable implementations of SIMD intrinsics. It allows you to use SSE functions on ARM, or NEON functions on x86, with zero overhead when native implementation is available.

## Installation

As a build dependency in `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools", "simde-py"]
```

## Usage

```python
import simde_py

# Get include directory for your extension
include_dir = simde_py.get_include()
```

In your C code:

```c
#include "simde/x86/sse2.h"
#include "simde/arm/neon.h"
// SIMD code works everywhere
```

## API

### `simde_py.get_include()`

Returns the path to the SIMDe header files directory.

## License

MIT License. SIMDe is also MIT licensed.
