# k3txutil

[![Action-CI](https://github.com/pykit3/k3txutil/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3txutil/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3txutil/badge/?version=stable)](https://k3txutil.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3txutil)](https://pypi.org/project/k3txutil)

A collection of helper functions to implement transactional operations.

k3txutil is a component of [pykit3] project: a python3 toolkit set.


#   Name

txutil

#   Status

This library is considered production ready.

#   Description

A collection of helper functions to implement transactional operations.

#   Exceptions

##  CASConflict

**syntax**:
`CASConflict()`

User should raise this exception when a CAS conflict detect in a user defined
`set` function.




# Install

```
pip install k3txutil
```

# Synopsis

```python

import k3txutil
import threading


class Foo(object):

    def __init__(self):
        self.lock = threading.RLock()
        self.val = 0
        self.ver = 0

    def _get(self, db, key, **kwargs):
        # db, key == 'dbname', 'mykey'
        with self.lock:
            return self.val, self.ver

    def _set(self, db, key, val, prev_stat, **kwargs):

        # db, key == 'dbname', 'mykey'
        with self.lock:
            if prev_stat != self.ver:
                raise k3txutil.CASConflict(prev_stat, self.ver)

            self.val = val
            self.ver += 1

    def test_cas(self):
        for curr in k3txutil.cas_loop(self._get, self._set, args=('dbname', 'mykey', )):
            curr.v += 2

        print((self.val, self.ver)) # (2, 1)

while True:
    curr_val, stat = getter(key="mykey")
    new_val = curr_val + ':foo'
    try:
        setter(new_val, stat, key="mykey")
    except CASConflict:
        continue
    else:
        break

#`cas_loop` simplifies the above workflow to:
for curr in k3txutil.cas_loop(getter, setter, args=("mykey", )):
    curr.v += ':foo'


```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3