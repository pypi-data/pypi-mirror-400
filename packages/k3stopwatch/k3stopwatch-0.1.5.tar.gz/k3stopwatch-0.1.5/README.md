# k3stopwatch

[![Action-CI](https://github.com/pykit3/k3stopwatch/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3stopwatch/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3stopwatch/badge/?version=stable)](https://k3stopwatch.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3stopwatch)](https://pypi.org/project/k3stopwatch)

StopWatch - library for adding timers and tags in your code for performance monitoring

k3stopwatch is a component of [pykit3] project: a python3 toolkit set.


StopWatch operates on a notion of "spans" which represent scopes of code for which we
want to measure timing. Spans can be nested and placed inside loops for aggregation.

StopWatch requires a root scope which upon completion signifies the end of the round
of measurements. On a server, you might use a single request as your root scope.

StopWatch produces two kinds of reports.
1) Aggregated (see _reported_values).
2) Non-aggregated or "tracing" (see _reported_traces).



# Install

```
pip install k3stopwatch
```

# Synopsis

```python

import k3stopwatch
sw  = k3stopwatch.StopWatch()

with sw.timer('rwoot'):
    for i in range(50):
         with sw.timer('inner_task'):
             print("do_inner_task(i)")

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3