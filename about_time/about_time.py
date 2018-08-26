import sys
from contextlib import contextmanager

import time
from datetime import timedelta


    """Measures the execution time of a block of code.
def about_time(fn=None, it=None):

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

    # use as context manager.
    if not (fn or it):
        return context()

    # use as callable handler.
    if not it:
        with context():
            result = fn()
        return HandleResult(timings, result)

    # use as counter/throughput iterator.
    def counter():
        i = -1
        with context():
            for i, elem in enumerate(it):
                yield elem
        fn(HandleStats(timings, i + 1))

    return counter()


class Handle(object):
    def __init__(self, timings):
        self.__timings = timings

    @property
    def duration(self):
        return self.__timings[1] - self.__timings[0]

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


class HandleResult(Handle):
    def __init__(self, timings, result):
        super().__init__(timings)
        self.__result = result

    @property
    def result(self):
        return self.__result
