# coding=utf-8
import sys
import time
from contextlib import contextmanager
from datetime import timedelta

if sys.version_info >= (3, 3):
    timer = time.perf_counter
else:  # pragma: no cover
    timer = time.time

    """Measures the execution time of a block of code, and even counts iterations
    and the throughput of them, always with a beautiful "human" representation.

    There's three modes of operation: context manager, callable handler and
    iterator metrics.
def about_time(func_or_it=None):

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

    timings = [0.0, 0.0]

    # use as a context manager.
    if func_or_it is None:
        return _context_timing(timings, Handle(timings))

    # use as a callable.
    if callable(func_or_it):
        with _context_timing(timings):
            result = func_or_it()
        return HandleResult(timings, result)

    try:
        it = iter(func_or_it)
    except TypeError:
        raise UserWarning('param should be callable or iterable.')

    # use as a counter/throughput iterator.
    def it_closure():
        with _context_timing(timings):
            for it_closure.count, elem in enumerate(it, 1):  # iterators are iterable.
                yield elem

    it_closure.count = 0  # the count will only be updated after starting iterating.
    return HandleStats(timings, it_closure)


@contextmanager
def _context_timing(timings, handle=None):
    timings[0] = timer()
    yield handle
    timings[1] = timer()


class Handle(object):
    DURATION_HUMAN_SPEC = (
        (1.e-6, 1e9, 1e3, 'ns'),
        (1.e-3, 1e6, 1e3, 'us'),
        (1., 1e3, 1e3, 'ms'),
        (60., 1e0, 60., 's'),
    )

    def __init__(self, timings):
        self.__timings = timings

    @property
    def duration(self):
        return self.__timings[1] - self.__timings[0]

    @property
    def duration_human(self):
        value = self.duration
        for top, mult, size, unit in Handle.DURATION_HUMAN_SPEC:
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
    THROUGHPUT_HUMAN_SPEC = (
        (1. / 60 / 24, 60 * 60 * 24, 24, '/d'),
        (1. / 60, 60 * 60, 60, '/h'),
        (1., 60, 60, '/m'),
        (float('inf'), 1, float('inf'), '/s'),
    )

    def __init__(self, timings, it_closure):
        super(HandleStats, self).__init__(timings)
        self.__it = it_closure

    def __iter__(self):
        return self.__it()

    @property
    def count(self):
        """Return the current iteration count.
        This is dynamically updated in real time.

        Returns:
            int: the current iteration count.

        """
        return self.__it.count

    @property
    def throughput(self):
        """Return the current throughput in items per second.
        This is dynamically updated in real time.

        Returns:
            float: the number of items per second.

        """
        try:
            return self.count / self.duration
        except ZeroDivisionError:
            return float('nan')

    @property
    def throughput_human(self):
        """Return a beautiful representation of the current throughput.
        It dynamically calculates the best unit to use.

        Returns:
            str: the duration representation.

        """
        if self.count == 0:
            return '-'

        value = self.throughput
        for top, mult, size, unit in HandleStats.THROUGHPUT_HUMAN_SPEC:
            if value < top:
                result = round(value * mult, ndigits=2)
                if result < size:
                    return '{}{}'.format(result, unit)
        return '?'
