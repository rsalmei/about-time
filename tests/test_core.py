import random
from datetime import datetime
from decimal import Decimal
from itertools import chain, repeat, tee
from unittest import mock

import pytest

from about_time import about_time
from about_time.core import Handle, HandleStats


@pytest.fixture
def rand_offset():
    return random.random() * 1000


@pytest.fixture
def mock_timer():
    with mock.patch('time.perf_counter') as mt:
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
    'count_human',
    'count_human_as',
    'throughput',
    'throughput_human',
    'throughput_human_as',
])
def test_context_manager_mode_dont_have_field(field):
    with about_time() as at:
        pass

    with pytest.raises(AttributeError):
        getattr(at, field)


@pytest.mark.parametrize('field', [
    'count',
    'count_human',
    'count_human_as',
    'throughput',
    'throughput_human',
    'throughput_human_as',
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


def test_handle_duration_human():
    h = Handle([1, 2])
    assert h.duration_human.value == 1


def test_handle_count_human():
    def it_closure():
        pass

    it_closure.count = 1
    h = HandleStats([1, 2], it_closure)
    assert h.count_human.value == 1


def test_handle_throughput_human():
    def it_closure():
        pass

    it_closure.count = 1
    h = HandleStats([1, 2], it_closure)
    assert h.throughput_human.value == 1
