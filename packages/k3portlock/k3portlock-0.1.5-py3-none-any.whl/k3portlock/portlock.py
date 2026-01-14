import errno
import hashlib
import logging
import platform
import socket
import threading
import time

OS = platform.system()

PORT_N = 3
PORT_RANGE = (40000, 60000)

DEFAULT_SLEEP_TIME = 0.01  # sec

logger = logging.getLogger(__name__)


class PortlockError(Exception):
    """
    Super class of all Portlock exceptions.
    """

    pass


class PortlockTimeout(PortlockError):
    """
    Timeout when waiting to acquire the lock.
    """

    pass


class Portlock(object):
    """
    A lock instance.
    Portlock is thread safe.
    It is OK to create just one lock in a process for all threads.
    """

    def __init__(self, key, timeout=1, sleep_time=None):
        """
        `Portlock` supports `with` statement.

        When entering a `with` statement of `Portlock` instance it invokes `acquire()`
        automatically.

        And when leaving `with` block, `release()` will be called to release the lock.
        :param key: is a string as lock key.`key` will be hashed to a certain port
        :param timeout: is the max time in second to wait to acquire the lock.
        it raises an `portlock.PortlockTimeout` exception.
        :param sleep_time: is the time in second between every two attempts to bind a port.
        """
        self.key = key
        self.addr = str_to_addr(key)
        self.timeout = timeout
        self.sleep_time = sleep_time or DEFAULT_SLEEP_TIME
        self.socks = [None] * PORT_N

        self.thread_lock = threading.RLock()

    def try_lock(self):
        self.thread_lock.acquire()

        try:
            self._lock()

            if self.has_locked():
                return True
            else:
                self.socks = [None] * PORT_N
                self.thread_lock.release()
                return False

        except Exception:
            self.thread_lock.release()
            raise

    def has_locked(self):
        """
        It checks if this instances has the lock.
        :return: `True` if it has the lock.
        """
        if OS == "Linux":
            return self.socks[0] is not None

        # other OS

        return len([x for x in self.socks if x is not None]) > len(self.socks) / 2

    def acquire(self):
        """
        It tries to acquire the lock before `timeout`.
        :return: nothing
        """
        t0 = time.time()

        while True:
            if self.try_lock():
                return

            now = time.time()
            left = t0 + self.timeout - now
            if left > 0:
                slp = min([self.sleep_time, left + 0.001])
                time.sleep(slp)
            else:
                raise PortlockTimeout("portlock timeout: " + repr(self.key), self.key)

    def release(self):
        """
        It releases the lock it holds, or does nothing if it does not hold the lock.
        :return: nothing
        """
        if not self.has_locked():
            return

        for sock in self.socks:
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass

        self.socks = [None] * PORT_N

        self.thread_lock.release()

    def _lock(self):
        if OS == "Linux":
            so = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                addr = "\0/portlock/" + self.key
                so.bind(addr)
                self.socks[0] = so
                logger.debug("success to bind: {addr}".format(addr=addr))
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    logger.debug("failure to bind: {addr}".format(addr=addr))
                else:
                    raise

            return

        # other OS

        for i in range(len(self.socks)):
            addr = (self.addr[0], self.addr[1] + i)

            so = self._socket()

            try:
                so.bind(addr)
                self.socks[i] = so
                logger.debug("success to bind: {addr}".format(addr=addr))
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    logger.debug("failure to bind: {addr}".format(addr=addr))
                else:
                    raise

    def _socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, typ, value, traceback):
        self.release()

    def __del__(self):
        self.release()


def str_to_addr(x):
    # builtin hash() gives bad distribution with sequencial values.
    # re-hash it with 32 bit fibonacci hash.
    # And finally embed it into ip and port

    r = hashlib.sha1(str(x).encode("utf8")).hexdigest()
    r = int(r, 16)
    p = r % (PORT_RANGE[1] - PORT_RANGE[0]) + PORT_RANGE[0]

    return ("127.0.0.1", p)
