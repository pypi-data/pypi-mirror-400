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
