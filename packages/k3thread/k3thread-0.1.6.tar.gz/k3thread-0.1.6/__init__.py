"""
k3thread is utility to create and operate thread.

Start a daemon thread after 0.2 seconds::

    >>> th = daemon(lambda :1, after=0.2)

Stop a thread by sending a exception::

    import time

    def busy():
        while True:
            time.sleep(0.1)

    t = daemon(busy)
    send_exception(t, SystemExit)

"""

from importlib.metadata import version

__version__ = version("k3thread")

from .thd import InvalidThreadIdError
from .thd import SendRaiseError
from .thd import daemon
from .thd import send_exception
from .thd import start

__all__ = [
    "InvalidThreadIdError",
    "SendRaiseError",
    "daemon",
    "send_exception",
    "start",
]
