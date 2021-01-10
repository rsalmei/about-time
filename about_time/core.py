# coding=utf-8
from __future__ import absolute_import, division, unicode_literals

import sys
import time
from contextlib import contextmanager

from . import human

if sys.version_info >= (3, 3):
    timer = time.perf_counter
else:  # pragma: no cover
    timer = time.time


def about_time(func_or_it=None, *args, **kwargs):
    """Measure timing and throughput of code blocks, with beautiful
    human friendly representations.

    There're three modes of operation: context manager, callable and
    throughput.

    1. Use it like a context manager:

    >>> with about_time() as at:
    ....    # code block.

    2. Use it with a callable:

    >>> at = about_time(func, arg1, kwarg2=arg2)  # send arguments at will.

    3. Use it with an iterable or generator:

    >>> at = about_time(items)
    >>> for item in at:
    ....    # use item
    """

    timings = [0.0, 0.0]

    # use as a context manager.
    if func_or_it is None:
        return _context_timing(timings, Handle(timings))

    # use as a callable.
    if callable(func_or_it):
        with _context_timing(timings):
            result = func_or_it(*args, **kwargs)
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
    def __init__(self, timings):
        self.__timings = timings

    @property
    def duration(self):
        """Return the actual duration in seconds.
        This is dynamically updated in real time.

        Returns:
            float: the number of seconds.

        """
        return (self.__timings[1] or timer()) - self.__timings[0]

    @property
    def duration_human(self):
        """Return a beautiful representation of the duration.
        It dynamically calculates the best unit to use.

        Returns:
            str: the duration representation.

        """
        return human.duration_human(self.duration)


class HandleResult(Handle):
    def __init__(self, timings, result):
        super(HandleResult, self).__init__(timings)
        self.__result = result

    @property
    def result(self):
        """Return the result of the callable.

        Returns:
            the result of the callable.

        """
        return self.__result


class HandleStats(Handle):
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
        except ZeroDivisionError:  # pragma: no cover
            return float('nan')

    @property
    def throughput_human(self):
        """Return a beautiful representation of the current throughput.
        It dynamically calculates the best unit to use.

        Returns:
            str: the duration representation.

        """
        return human.throughput_human(self.throughput)
