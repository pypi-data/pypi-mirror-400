#!/usr/bin/env python
# coding: utf-8

import ctypes
import inspect
import threading
import time


class SendRaiseError(Exception):
    """
    Super class of exceptions raied when calling send_raise().
    """


class InvalidThreadIdError(SendRaiseError):
    """
    Raised if a invalid thread id is used.
    """


def start(target, name=None, args=None, kwargs=None, daemon=False, after=None):
    """
    Create and start a thread with the given args.

    Args:
        target(callable):
            The callable object to run.

        name:
            The thread name. By default, a unique name is constructed of the form "Thread-N" where N is a small decimal number.

        args:
            The argument tuple for the target invocation. Defaults to `()`.

        kwargs(dict):
            A dictionary of keyword arguments for the target invocation. Defaults to `{}`.

        daemon(bool):
            Whether to create a **daemon** thread.

            A daemon thread will quit when the main thread in a process quits.
            A non-daemon thread keeps running after main thread quits.
            A process does not quit if there are any non-daemon threads running.

        after(bool):
            If `after` is not `None`, it sleeps for `after` seconds before calling
            `target`.

            By default it is `None`.

    Returns:
        threading.Thread: the thread started.

    """
    args = args or ()
    kwargs = kwargs or {}

    if after is None:
        _target = target
    else:

        def _target(*args, **kwargs):
            time.sleep(after)
            target(*args, **kwargs)

    t = threading.Thread(target=_target, name=name, args=args, kwargs=kwargs)
    t.daemon = daemon
    t.start()

    return t


def daemon(target, name=None, args=None, kwargs=None, after=None):
    """
    Create and start a daemon thread.
    It is same as `start()` except that it sets argument `daemon=True`.
    """

    return start(target, name=name, args=args, kwargs=kwargs, daemon=True, after=after)


def send_exception(thread, exctype):
    """
    Asynchronously raises an exception in the context of the given thread,
    which should cause the thread to exit silently (unless caught).

    **Caveat**: this function does not work with pypy, because it relies on
        `pythonapi` that pypy does not support.

    **Caveat**: It might not work as expected:

    The exception will be raised only when executing python bytecode. If your
    thread calls a native/built-in blocking function (such as `time.sleep()` and
    `threading.Thread.join()`), the exception will be raised only when execution
    returns to the python code.

    There is also an issue if the built-in function internally calls
    PyErr_Clear(), which would effectively cancel your pending exception. You can
    try to raise it again.

    Thus This function does not guarantee that a running thread will be
    interrupted and shut down when it is called.

    Args:

        thread(threading.Thread):
            the thread in which to raise the exception.

        exctype:
            A exception class that will be raised in the thread.

    Raises:
        InvalidThreadIdError: if the given thread is not alive or found.
        TypeError:  if any input is illegal.
        ValueError: if any input is illegal.
        SendRaiseError: for other unexpected errors.
    """
    if not isinstance(thread, threading.Thread):
        raise TypeError("Only Thread is allowed, got {t}".format(t=thread))

    _async_raise(thread.ident, exctype)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")

    if not issubclass(exctype, BaseException):
        raise ValueError("Only sub classes of BaseException can be raised")

    # PyThreadState_SetAsyncExc requires GIL to be held
    gil_state = ctypes.pythonapi.PyGILState_Ensure()
    try:
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
        if res == 0:
            # The thread is likely dead already.
            raise InvalidThreadIdError(tid)

        elif res != 1:
            # If more than one threads are affected (WTF?), we're in trouble, and
            # we try our best to revert the effect, although this may not work.
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)

            raise SendRaiseError("PyThreadState_SetAsyncExc failed", res)

    finally:
        ctypes.pythonapi.PyGILState_Release(gil_state)
