# coding=utf-8
import sys
from contextlib import contextmanager

import time
from datetime import timedelta


def about_time(fn=None, it=None):
    """Measures the execution time of a block of code, and even counts iterations
    and the throughput of them, always with a beautiful "human" representation.

    There's three modes of operation: context manager, callable handler and
    iterator metrics.

    1. Use it like a context manager:

    >>> with about_time() as t_whole:
    ....    with about_time() as t_1:
    ....        func_1()
    ....    with about_time() as t_2:
    ....        func_2('params')

    >>> print(f'func_1 time: {t_1.duration_human}')
    >>> print(f'func_2 time: {t_2.duration_human}')
    >>> print(f'total time: {t_whole.duration_human}')

    The actual duration in seconds is available in:
    >>> secs = t_whole.duration

    2. You can also use it like a callable handler:

    >>> t_1 = about_time(func_1)
    >>> t_2 = about_time(lambda: func_2('params'))

    Use the field `result` to get the outcome of the function.

    Or you mix and match both:

    >>> with about_time() as t_whole:
    ....    t_1 = about_time(func_1)
    ....    t_2 = about_time(lambda: func_2('params'))

    3. And you can count and, since we have duration, also measure the throughput
    of an iterator block, specially useful in generators, which do not have length,
    but you can use with any iterables:

    >>> def callback(t_func):
    ....    logger.info('func: size=%d throughput=%s', t_func.count,
    ....                                               t_func.throughput_human)
    >>> items = filter(...)
    >>> for item in about_time(callback, items):
    ....    # use item any way you want.
    ....    pass
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

    if it is None:
        # use as context manager.
        if fn is None:
            return context()

        # use as callable handler.
        with context():
            result = fn()
        return HandleResult(timings, result)

    # use as counter/throughput iterator.
    if not fn:
        raise UserWarning('fn is required in counter mode')

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
        spec = (
            (1.e-6, 1e9, 1e3, 'ns'),
            (1.e-3, 1e6, 1e3, 'us'),
            (1., 1e3, 1e3, 'ms'),
            (60., 1e0, 60., 's'),
        )
        for top, mult, size, unit in spec:
            if value < top:
                result = round(value * mult, ndigits=2)
                if result < size:
                    return '{}{}'.format(result, unit)

        txt = str(timedelta(seconds=float('{:.1f}'.format(value))))
        pos = txt.find('.')
        if pos == -1:
            return txt
        return txt[:pos + 2]


class HandleResult(Handle):
    def __init__(self, timings, result):
        super(HandleResult, self).__init__(timings)
        self.__result = result

    @property
    def result(self):
        return self.__result


class HandleStats(Handle):
    def __init__(self, timings, count):
        super(HandleStats, self).__init__(timings)
        self.__count = count

    @property
    def count(self):
        return self.__count

    @property
    def throughput(self):
        if not self.duration:
             # In case it was too fast to be measured
            return float('NaN')
        return self.count / self.duration

    @property
    def throughput_human(self):
        value = self.throughput
        spec = (
            (1. / 60, 60 * 60, 60, '/h'),
            (1., 60, 60, '/m'),
        )
        for top, mult, size, unit in spec:
            if value < top:
                result = round(value * mult, ndigits=2)
                if result < size:
                    return '{}{}'.format(result, unit)

        result = round(value, ndigits=2)
        return '{}{}'.format(result, '/s')
