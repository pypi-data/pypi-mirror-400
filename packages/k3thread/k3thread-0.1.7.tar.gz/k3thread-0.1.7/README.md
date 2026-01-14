# k3thread

[![Build Status](https://github.com/pykit3/k3thread/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3thread/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3thread/badge/?version=stable)](https://k3thread.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3thread)](https://pypi.org/project/k3thread)

utility to create thread.

k3thread is a component of [pykit3] project: a python3 toolkit set.


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




# Install

```
pip install k3thread
```

# Synopsis

```python
>>> th = daemon(lambda :1, after=0.2)

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3