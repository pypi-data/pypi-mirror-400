# k3pattern

[![Action-CI](https://github.com/pykit3/k3pattern/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3pattern/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3pattern/badge/?version=stable)](https://k3pattern.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3pattern)](https://pypi.org/project/k3pattern)

Find common prefix of several `string`s, tuples of string, or other nested structure, recursively by default.

k3pattern is a component of [pykit3] project: a python3 toolkit set.


Find common prefix of several string, tuples of string, or other nested structure, recursively by default.
It returns the shortest prefix: empty string or empty tuple is removed.



# Install

```
pip install k3pattern
```

# Synopsis

```python

import k3pattern

k3pattern.common_prefix('abc', 'abd')                   # 'ab'
k3pattern.common_prefix((1, 2, 'abc'), (1, 2, 'abd'))   # (1, 2, 'ab')
k3pattern.common_prefix((1, 2, 'abc'), (1, 2, 'xyz'))   # (1, 2); empty prefix of 'abc' and 'xyz' is removed
k3pattern.common_prefix((1, 2, (5, 6)), (1, 2, (5, 7))) # (1, 2, (5,) )
k3pattern.common_prefix('abc', 'abd', 'abe')            # 'ab'; common prefix of more than two
```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3