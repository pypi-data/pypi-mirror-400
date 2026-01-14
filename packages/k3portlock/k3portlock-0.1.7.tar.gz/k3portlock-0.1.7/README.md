# k3portlock

[![Action-CI](https://github.com/pykit3/k3portlock/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3portlock/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3portlock/badge/?version=stable)](https://k3portlock.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3portlock)](https://pypi.org/project/k3portlock)

k3protlock is a cross-process lock that is implemented with `tcp` port binding.

k3portlock is a component of [pykit3] project: a python3 toolkit set.


k3portlock is a cross-process lock that is implemented with `tcp` port binding.
Since no two processes could bind on a same TCP port.

k3portlock tries to bind **3** ports on loopback ip `127.0.0.1`.
If a Portlock instance succeeds on binding **2** ports out of 3,
it is considered this instance has acquired the lock.




# Install

```
pip install k3portlock
```

# Synopsis

```python

#!/usr/bin/env python

import time
import k3portlock

if __name__ == "__main__":

    # Basic lock acquisition and release
    lock = k3portlock.Portlock("mylock")

    # Try to acquire lock (non-blocking)
    if lock.try_lock():
        print("Lock acquired")
        # Do some work
        lock.release()
        print("Lock released")
    else:
        print("Failed to acquire lock")

    # Blocking lock acquisition with timeout
    lock2 = k3portlock.Portlock("mylock2", timeout=5)
    try:
        lock2.acquire()  # Will wait up to 5 seconds
        print("Lock acquired")
        time.sleep(1)
        lock2.release()
        print("Lock released")
    except k3portlock.PortlockTimeout:
        print("Timeout while waiting for lock")

    # Context manager usage (recommended)
    with k3portlock.Portlock("mylock3", timeout=3) as lock:
        print("Lock acquired via context manager")
        # Do some work
        time.sleep(0.5)
    print("Lock automatically released")

    # Check if lock is held (without acquiring)
    lock4 = k3portlock.Portlock("testlock")
    print(lock4.has_locked())  # False

    lock4.acquire()
    another_lock = k3portlock.Portlock("testlock")
    print(another_lock.has_locked())  # False (different instance)
    lock4.release()

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3