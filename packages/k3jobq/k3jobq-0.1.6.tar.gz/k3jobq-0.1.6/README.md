# k3jobq

[![Build Status](https://github.com/pykit3/k3jobq/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3jobq/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3jobq/badge/?version=stable)](https://k3jobq.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3jobq)](https://pypi.org/project/k3jobq)

k3jobq processes a series of inputs with functions concurrently

k3jobq is a component of [pykit3] project: a python3 toolkit set.


k3jobq is a manager to create cuncurrent tasks.
It processes a series of inputs with functions concurrently and
return once all threads are done::

    def add1(args):
        return args + 1

    def printarg(args):
        print(args)

    k3jobq.run([0, 1, 2], [add1, printarg])
    # > 1
    # > 2
    # > 3



# Install

```
pip install k3jobq
```

# Synopsis

```python

#!/usr/bin/env python

import k3jobq

if __name__ == "__main__":

    def add1(args):
        return args + 1

    def multi2(args):
        return args * 2

    def printarg(args):
        print(args)

    k3jobq.run([0, 1, 2], [add1, printarg])
    # > 1
    # > 2
    # > 3

    k3jobq.run((0, 1, 2), [add1, multi2, printarg])
    # > 2
    # > 4
    # > 6

    # Specify number of threads for each job:

    # Job 'multi2' uses 1 thread.
    # This is the same as the above example.
    k3jobq.run(list(range(3)), [add1, (multi2, 1), printarg])
    # > 2
    # > 4
    # > 6

    # Create 2 threads for job 'multi2':

    # As there are 2 thread dealing with multi2, output order will not be kept.
    k3jobq.run(list(range(3)), [add1, (multi2, 2), printarg])
    # Output could be:
    # > 4
    # > 2
    # > 6

    # Multiple threads with order kept:

    # keep_order=True to force to keep order even with concurrently running.
    k3jobq.run(list(range(3)), [add1, (multi2, 2), printarg],
               keep_order=True)
    # > 2
    # > 4
    # > 6

    # timeout=0.5 specifies that it runs at most 0.5 second.
    k3jobq.run(list(range(3)), [add1, (multi2, 2), printarg],
               timeout=0.5)

    # Returning *k3jobq.EmptyRst* stops delivering result to next job:

    def drop_even_number(i):
        if i % 2 == 0:
            return k3jobq.EmptyRst
        else:
            return i

    k3jobq.run(list(range(10)), [drop_even_number, printarg])
    # > 1
    # > 3
    # > 5
    # > 7
    # > 9

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3