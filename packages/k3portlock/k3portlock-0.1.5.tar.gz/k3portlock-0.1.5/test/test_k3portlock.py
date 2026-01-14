import threading
import time
import unittest
import resource
import hashlib

import k3portlock
import k3ut

dd = k3ut.dd


class TestPortlock(unittest.TestCase):
    def test_mem_test(self):
        a = k3portlock.Portlock("k1")
        b = k3portlock.Portlock("k1")

        dd("lock-a: ", a.addr)
        dd("lock-b: ", b.addr)

        r = b.has_locked()
        self.assertFalse(r, "not locked")

        r = b.has_locked()
        self.assertFalse(r, "still not locked")

        a.acquire()

        r = b.has_locked()
        self.assertFalse(r, "not locked by me.")

        r = b.try_lock()
        self.assertFalse(r, "can not lock while another one hold it")

        b.release()
        r = b.try_lock()
        self.assertFalse(r, "b can not release lock belongs to a")

        a.release()

        r = b.try_lock()
        self.assertTrue(r, "I can hold it now")
        dd("try-locked:", r)

        try:
            a.acquire()
            self.fail("lock-a should not be able to get lock")
        except k3portlock.PortlockError:
            pass

    def test_1_lock_per_thread(self):
        sess = {"n": 0}

        def worker(lock, ident):
            for ii in range(1000):
                lock.acquire()
                dd("{0}-{1} start".format(ident, ii))

                self.assertEqual(0, sess["n"], "n is 0 just after lock is acquired, 1-lock-for-1")

                sess["n"] += 1
                time.sleep(0.001)
                self.assertEqual(1, sess["n"], "no more than 2 thread holding lock")
                sess["n"] -= 1
                dd("{0}-{1} end".format(ident, ii))
                lock.release()

        ts = [threading.Thread(target=worker, args=(k3portlock.Portlock("x", timeout=100), x)) for x in range(10)]

        for t in ts:
            t.start()

        for t in ts:
            t.join()

    def test_1_lock_for_all_thread(self):
        sess = {"n": 0}

        def worker(lck):
            for ii in range(1000):
                lck.acquire()

                self.assertEqual(0, sess["n"], "n is 0 just after lock is acquired, 1-lock-for-all")

                sess["n"] += 1
                time.sleep(0.001)
                self.assertEqual(1, sess["n"], "no more than 2 thread holding lock")
                sess["n"] -= 1
                lck.release()

        lock = k3portlock.Portlock("x", timeout=100)
        ts = [threading.Thread(target=worker, args=(lock,)) for x in range(3)]

        for t in ts:
            t.daemon = True
            t.start()

        for t in ts:
            t.join()

    def test_sleep_time(self):
        lock0 = k3portlock.Portlock("x")
        lock = k3portlock.Portlock("x", timeout=1, sleep_time=2)

        with lock0:
            t0 = time.time()
            try:
                lock.acquire()
            except k3portlock.PortlockTimeout:
                pass

            t1 = time.time()

            self.assertTrue(
                0.9 < t1 - t0 < 1.1,
                "sleep_time should not affect timeout(1 sec), but it spends {0} seconds".format(t1 - t0),
            )

    def test_collision(self):
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (102400, 102400))
        except ValueError:
            self.skipTest("Cannot set resource limits (requires elevated privileges)")

        dd = {}
        ls = []
        collision_num = 0
        for i in range(1 << 15):
            key = str(hashlib.sha1(str(i).encode("utf8")).hexdigest())
            lck = key
            lock = k3portlock.Portlock(lck, timeout=8)
            r = lock.try_lock()
            if r:
                dd[lock.addr] = i
                ls.append(lock)
            else:
                collision_num += 1
        self.assertTrue(
            (collision_num / (1 << 15)) < 0.01, "The lock collision rate should be less than the threshold of 1%"
        )
