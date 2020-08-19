# coding=utf-8
from __future__ import absolute_import, division, unicode_literals

import random
from datetime import datetime
from decimal import Decimal
from itertools import chain, repeat, tee

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from about_time import about_time
from about_time.core import Handle, HandleStats


@pytest.fixture
def rand_offset():
    return random.random() * 1000


@pytest.fixture
def mock_timer():
    with mock.patch('about_time.core.timer') as mt:
        yield mt


def test_duration_context_manager_mode(rand_offset, mock_timer):
    start, end = 1.4 + rand_offset, 2.65 + rand_offset
    mock_timer.side_effect = start, end

    with about_time() as at:
        pass

    assert at.duration == pytest.approx(end - start)


def test_duration_callable_mode(rand_offset, mock_timer):
    start, end = 1.4 + rand_offset, 2.65 + rand_offset
    mock_timer.side_effect = start, end

    at = about_time(lambda: 1)

    assert at.duration == pytest.approx(end - start)


def test_duration_counter_throughput_mode(rand_offset, mock_timer):
    start, end = 1.4 + rand_offset, 2.65 + rand_offset
    mock_timer.side_effect = start, end

    at = about_time(range(2))
    for _ in at:
        pass

    assert at.duration == pytest.approx(end - start)


@pytest.mark.parametrize('call, args, kwargs, expected', [
    (lambda: 123, (), {}, 123),
    (str, (), {}, ''),
    (list, (), {}, []),
    (lambda x: x + 1, (123,), {}, 124),
    (str, ('cool',), {}, 'cool'),
    (list, ((1, 2, 3),), {}, [1, 2, 3]),
    (lambda x: x + 1, (), {'x': 123}, 124),
])
def test_callable_mode_result(call, args, kwargs, expected):
    at = about_time(call, *args, **kwargs)
    assert at.result == expected


@pytest.mark.parametrize('it', [
    [],
    [1, 2, 3],
    range(0),
    range(12),
    'string',
    (x ** 2 for x in range(8)),
])
def test_counter_throughput_mode(it, rand_offset, mock_timer):
    start, end = 1.4 + rand_offset, 2.65 + rand_offset
    mock_timer.side_effect = chain((start,), repeat(end))
    it_see, it_copy = tee(it)

    at = about_time(it_see)
    assert at.count == 0  # count should work even before starting iterating.

    i = 0
    for i, elem in enumerate(at, 1):
        assert elem == next(it_copy)
        assert at.count == i  # count works in real time now!
        assert at.duration > 0  # ensure the timing ending is also updated in real time.

    assert at.throughput == pytest.approx(i / 1.25)


@pytest.mark.parametrize('field', [
    'result',
    'count',
    'throughput',
    'throughput_human',
])
def test_context_manager_mode_dont_have_field(field):
    with about_time() as at:
        pass

    with pytest.raises(AttributeError):
        getattr(at, field)


@pytest.mark.parametrize('field', [
    'count',
    'throughput',
    'throughput_human',
])
def test_callable_mode_dont_have_field(field):
    at = about_time(lambda: 1)

    with pytest.raises(AttributeError):
        getattr(at, field)


@pytest.mark.parametrize('field', [
    'result',
])
def test_counter_throughput_mode_dont_have_field(field):
    at = about_time(range(2))

    with pytest.raises(AttributeError):
        getattr(at, field)


@pytest.mark.parametrize('value', [
    123,
    .1,
    object(),
    datetime.now(),
    Decimal(),
])
def test_wrong_params_must_complain(value):
    with pytest.raises(UserWarning):
        about_time(value)


@pytest.mark.parametrize('duration, expected', [
    (.00000000123, '1.23ns'),
    (.00000000185, '1.85ns'),
    (.000000001855, '1.85ns'),
    (.0000000018551, '1.86ns'),
    (.000001, '1.0us'),
    (.000000999996, '1.0us'),
    (.00001, '10.0us'),
    (.0000156, '15.6us'),
    (.01, '10.0ms'),
    (.0141233333333, '14.12ms'),
    (.0199999, '20.0ms'),
    (.1099999, '110.0ms'),
    (.1599999, '160.0ms'),
    (.8015, '801.5ms'),
    (3.434999, '3.43s'),
    (3.435999, '3.44s'),
    (59.99, '59.99s'),
    (59.999, '0:01:00'),
    (60.0, '0:01:00'),
    (68.5, '0:01:08.5'),
    (68.09, '0:01:08.1'),
    (60.99, '0:01:01'),
    (125.825, '0:02:05.8'),
    (4488.395, '1:14:48.4'),
])
def test_duration_human(duration, expected):
    h = Handle([0., duration])

    assert h.duration_human == expected


@pytest.mark.parametrize('end, count, expected', [
    (0., 1, '?'),
    (1., 0, '-'),
    (1., 1, '1.0/s'),
    (1., 10, '10.0/s'),
    (1., 2500, '2500.0/s'),
    (1., 1825000, '1825000.0/s'),
    (5.47945205e-07, 1, '1825000.0/s'),
    (2., 1, '30.0/m'),
    (2., 10, '5.0/s'),
    (2., 11, '5.5/s'),
    (1.981981981981982, 11, '5.55/s'),
    (100., 10, '6.0/m'),
    (100., 3, '1.8/m'),
    (110., 8, '4.36/m'),
    (1600., 3, '6.75/h'),
    (67587655435., 5432737542, '4.82/m'),
    (67587655435., 543273754, '28.94/h'),
    (67587655435., 543273754271, '8.04/s'),
    (.99, 1, '1.01/s'),
    (.999, 1, '1.0/s'),
    (1.00001, 1, '1.0/s'),
    (1.0001, 1, '59.99/m'),
    (1165263., 123, '9.12/d'),
    (3600., 1, '1.0/h'),
    (3601., 1, '23.99/d'),
    (80000., 2, '2.16/d'),
])
def test_throughput_human(end, count, expected, rand_offset):
    def it_closure():
        pass

    it_closure.count = count
    h = HandleStats([rand_offset, end + rand_offset], it_closure)

    assert h.throughput_human == expected
