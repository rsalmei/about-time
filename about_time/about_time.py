import sys
from contextlib import contextmanager

import time
from datetime import timedelta


def about_time(fn=None):
    """Measures the execution time of a block of code.

    Use it like:

    >>> with about_time() as t_whole:
    ....    with about_time() as t_1:
    ....        func_1()
    ....    with about_time() as t_2:
    ....        func_2('params')

    >>> print(f'func_1 time: {t_1.duration_human}')
    >>> print(f'func_2 time: {t_2.duration_human}')
    >>> print(f'total time: {t_whole.duration_human}')

    You can also use it like:

    >>> t = about_time(func_1)
    >>> t = about_time(lambda: func_2('params'))

    Or you mix and match both:

    >>> with about_time() as t_whole:
    ....    t_1 = about_time(func_1)
    ....    t_2 = about_time(lambda: func_2('params'))
    """

    # has to be here to be mockable.
    if sys.version_info >= (3, 3):
        timer = time.perf_counter
    else:  # pragma: no cover
        timer = time.time

    @contextmanager
    def context():
        timings[0] = timer()
        yield handle
        timings[1] = timer()

    timings = [0.0, 0.0]
    handle = Handle(timings)
    if not fn:
        return context()

    with context():
        handle.result = fn()
    return handle


class Handle(object):
    def __init__(self, timings):
        self.timings = timings

    @property
    def duration(self):
        return self.timings[1] - self.timings[0]

    @property
    def duration_human(self):
        value = self.duration
        if value < 60:
            return '{}s'.format(int(value * 100) / 100.)

        txt = str(timedelta(seconds=int(value * 10) / 10.))
        pos = txt.find('.')
        if pos == -1:
            return txt
        return txt[:pos + 2]
