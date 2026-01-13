# `ispunct`

A small Python library for checking whether a character is a punctuation character.

---

## Quick Start

```python
from ispunct import ispunct

assert ispunct("?")
assert not ispunct("a")
assert ispunct("‽")
```

## Using `ispunct` as a Library

This package is published on PyPI.  You can install it with PIP:

```commandline
$ pip add ispunct
```

Or, if using [UV](https://github.com/astral-sh/uv/) for dependency management:

```commandline
$ uv add ispunct
```

## Notes on Internal Functionality

This library also implements (and uses internally) bitwise functions to calculate the number of leading/trailing zeros/ones in the bitwise representation of a Python integer.  We also compute a Python integer that has the same bitpattern as a given character (i.e., simulating Julia's `bitcast`).

## Citation

If your research depends on `ispunct`, please consider giving us a formal citation: [`citation.bib`](./citation.bib).
