# k3utfjson

[![Action-CI](https://github.com/pykit3/k3utfjson/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3utfjson/actions/workflows/python-package.yml)
[![Build Status](https://travis-ci.com/pykit3/k3utfjson.svg?branch=master)](https://travis-ci.com/pykit3/k3utfjson)
[![Documentation Status](https://readthedocs.org/projects/k3utfjson/badge/?version=stable)](https://k3utfjson.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3utfjson)](https://pypi.org/project/k3utfjson)

force `json.dump` and `json.load` in `utf-8` encoding.

k3utfjson is a component of [pykit3] project: a python3 toolkit set.


# Name

utfjson: force `json.dump` and `json.load` in `utf-8` encoding.

# Status

This library is considered production ready.


# Install

```
pip install k3utfjson
```

# Synopsis

```python

import k3utfjson

k3utfjson.load('"hello"')
k3utfjson.dump({})

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3