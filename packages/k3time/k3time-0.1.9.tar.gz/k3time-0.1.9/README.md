# k3time

[![Action-CI](https://github.com/pykit3/k3time/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3time/actions/workflows/python-package.yml)
[![Build Status](https://travis-ci.com/pykit3/k3time.svg?branch=master)](https://travis-ci.com/pykit3/k3time)
[![Documentation Status](https://readthedocs.org/projects/k3time/badge/?version=stable)](https://k3time.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3time)](https://pypi.org/project/k3time)

Time convertion utils

k3time is a component of [pykit3] project: a python3 toolkit set.


Time convertion utils.

    >>> parse('2017-01-24T07:51:59.000Z', 'iso')
    datetime.datetime(2017, 1, 24, 7, 51, 59)
    >>> format_ts(1485216000, 'iso')
    '2017-01-24T00:00:00.000Z'
    >>> format_ts(1485216000, '%Y-%m-%d')
    '2017-01-24'




# Install

```
pip install k3time
```

# Synopsis

```python
>>> parse('2017-01-24T07:51:59.000Z', 'iso')
datetime.datetime(2017, 1, 24, 7, 51, 59)
>>> format_ts(1485216000, 'iso')
'2017-01-24T00:00:00.000Z'
>>> format_ts(1485216000, '%Y-%m-%d')
'2017-01-24'
```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3