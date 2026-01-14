# k3rangeset

[![Action-CI](https://github.com/pykit3/k3rangeset/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3rangeset/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3rangeset/badge/?version=stable)](https://k3rangeset.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3rangeset)](https://pypi.org/project/k3rangeset)

segmented range which is represented in a list of sorted interleaving range.

k3rangeset is a component of [pykit3] project: a python3 toolkit set.


Segmented range which is represented in a list of sorted interleaving range.

A range set can be thought as: `[[1, 2], [5, 7]]`.




# Install

```
pip install k3rangeset
```

# Synopsis

```python

import k3rangeset

a = k3rangeset.RangeSet([[1, 5], [10, 20]])
a.has(1)  # True
a.has(8)  # False
a.add([5, 7])  # [[1, 7], [10, 20]]

inp = [
    [0, 1, [['a', 'b', 'ab'],
            ['b', 'd', 'bd'],
            ]],
    [1, 2, [['a', 'c', 'ac'],
            ['c', 'd', 'cd'],
            ]],
]

r = k3rangeset.RangeDict(inp, dimension=2)
print(r.get(0.5, 'a'))  # 'ab'
print(r.get(1.5, 'a'))  # 'ac'

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3