# k3portlock

[![Action-CI](https://github.com/pykit3/k3portlock/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3portlock/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3portlock/badge/?version=stable)](https://k3portlock.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3portlock)](https://pypi.org/project/k3portlock)

k3portlock is a cross-process lock that is implemented with `tcp` port binding.

k3portlock is a component of [pykit3] project: a python3 toolkit set.


k3portlock is a cross-process lock that is implemented with `tcp` port binding.
Since no two processes could bind on a same TCP port.

k3portlock tries to bind **3** ports on loopback ip `127.0.0.1`.
If a k3portlock instance succeeds on binding **2** ports out of 3,
it is considered this instance has acquired the lock.




# Install

```
pip install k3portlock
```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3