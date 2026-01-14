# k3color

[![Action-CI](https://github.com/pykit3/k3color/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3color/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3color/badge/?version=stable)](https://k3color.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3color)](https://pypi.org/project/k3color)

create colored text on terminal

k3color is a component of [pykit3] project: a python3 toolkit set.


# Install

```
pip install k3color
```

# Synopsis

```python
# output text in blue:
>>> blue('I am blue')
 '\x01\x1b[38;5;67m\x02I am blue\x01\x1b[0m\x02'

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3