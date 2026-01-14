import sys
import time
import unittest

import k3thread
import k3ut

dd = k3ut.dd


def _work(sess):
    try:
        while True:
            _ = 1

    except SystemExit:
        sess["raised"] = True


class TestThread(unittest.TestCase):
    def _verify_exception_raised(self, sess, thread):
        # we wait few seconds for the exception to be raised.
        for _ in range(100):
            if sess["raised"]:
                # The thread might still be alive at this point.
                time.sleep(0.2)
                self.assertFalse(thread.is_alive())
                break

            time.sleep(0.1)

        else:
            assert False, "SystemError is not raised"

    def test_send_exception(self):
        # send_exception does not work with PyPy
        if "PyPy" in sys.version:
            return

        sess = {"raised": False}

        t = k3thread.start(_work, args=(sess,), daemon=True)
        self.assertFalse(sess["raised"])

        with self.assertRaises(TypeError):
            k3thread.send_exception("thread", SystemExit)

        with self.assertRaises(TypeError):
            k3thread.send_exception(t, SystemExit())

        class SomeClass(object):
            pass

        with self.assertRaises(ValueError):
            k3thread.send_exception(t, SomeClass)

        k3thread.send_exception(t, SystemExit)
        self._verify_exception_raised(sess, t)

    def test_send_exception_many_times(self):
        # send_exception does not work with PyPy
        if "PyPy" in sys.version:
            return

        sess = {"raised": False}

        t = k3thread.start(_work, args=(sess,), daemon=True)
        self.assertFalse(sess["raised"])

        for _ in range(5):
            try:
                k3thread.send_exception(t, SystemExit)
            except k3thread.InvalidThreadIdError:
                # This will happen if the thread is already terminated by
                # a previous send_exception call.
                pass

        self._verify_exception_raised(sess, t)

        # Raising in a dead thread shoud not break.
        with self.assertRaises(k3thread.InvalidThreadIdError):
            k3thread.send_exception(t, SystemExit)

    def test_start(self):
        def _sort(a, reverse=False):
            a.sort(reverse=reverse)

        array = [3, 1, 2]
        t = k3thread.start(_sort, args=(array,))
        t.join()

        self.assertEqual(array, [1, 2, 3])

        t = k3thread.start(_sort, args=(array,), kwargs={"reverse": True})
        t.join()

        self.assertEqual(array, [3, 2, 1])

    def test_daemon(self):
        def noop():
            return None

        # Thread should be non-daemon by default
        t = k3thread.start(noop)
        self.assertFalse(t.daemon)

        t = k3thread.start(noop, daemon=True)
        self.assertTrue(t.daemon)

        t = k3thread.daemon(noop)
        self.assertTrue(t.daemon)

    def test_thread_after(self):
        def _do():
            pass

        with k3ut.Timer() as t:
            th = k3thread.start(target=_do, after=None)
            th.join()
            self.assertAlmostEqual(0, t.spent(), delta=0.1)

        with k3ut.Timer() as t:
            th = k3thread.start(target=_do, after=0.5)
            th.join()
            self.assertAlmostEqual(0.5, t.spent(), delta=0.1)

    def test_daemon_after(self):
        def _do():
            pass

        with k3ut.Timer() as t:
            th = k3thread.daemon(target=_do, after=None)
            th.join()
            self.assertAlmostEqual(0, t.spent(), delta=0.1)

        with k3ut.Timer() as t:
            th = k3thread.daemon(target=_do, after=0.5)
            th.join()
            self.assertAlmostEqual(0.5, t.spent(), delta=0.1)
