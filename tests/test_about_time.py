import random
from unittest import mock

import pytest
from itertools import tee

from about_time import about_time
from about_time.about_time import Handle, HandleStats


@pytest.fixture(params=[0, 1, 2])
def mode(request):
    return request.param


@pytest.fixture
def rand_offset():
    return random.random() * 1000


def test_timer_all_modes(mode, rand_offset):
    start, end = 1.4 + rand_offset, 2.65 + rand_offset
    with mock.patch('time.perf_counter') as mt:
        mt.side_effect = (start, end)

        t = [None]
        if mode == 0:
            with about_time() as t[0]:
                pass
        elif mode == 1:
            t[0] = about_time(lambda: 1)
        else:
            def callback(h):
                t[0] = h

            for _ in about_time(callback, range(2)):
                pass

    assert t[0].duration == pytest.approx(end - start)


@pytest.mark.parametrize('it, expected', [
    ([], 0),
    ([1, 2, 3], 3),
    (range(0), 0),
    (range(12), 12),
    ('string', 6),
    ((x ** 2 for x in range(8)), 8),
])
def test_counter_throughput(it, expected, rand_offset):
    callback = mock.Mock()

    start, end = 1.4 + rand_offset, 2.65 + rand_offset
    with mock.patch('time.perf_counter') as mt:
        mt.side_effect = (start, end)

        if expected:
            it_see, it_copy = tee(it)
        else:
            it_see, it_copy = it, None
        for elem in about_time(callback, it_see):
            assert elem == next(it_copy)

    callback.assert_called_once()
    (h,), _ = callback.call_args
    print(h)
    assert h.count == expected
    assert h.throughput == pytest.approx(expected / 1.25)


@pytest.mark.parametrize('dont', [
    'result', 'count', 'throughput', 'throughput_human'
])
def test_context_manager_dont_have_x(dont):
    with about_time() as t:
        pass

    with pytest.raises(AttributeError):
        getattr(t, dont)


def test_callable_handler_has_result():
    t = about_time(lambda: 1)
    assert t.result == 1


def test_counter_throughput_must_have_fn():
    with pytest.raises(UserWarning):
        about_time(it=[])


@pytest.mark.parametrize('dont', [
    'count', 'throughput', 'throughput_human'
])
def test_callable_handler_dont_have_x(dont):
    t = about_time(lambda: 1)

    with pytest.raises(AttributeError):
        getattr(t, dont)


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
    t = Handle([0., duration])

    assert t.duration_human == expected


@pytest.mark.parametrize('end, count, expected', [
    (1., 1, '1.0/s'),
    (1., 10, '10.0/s'),
    (1., 2500, '2500.0/s'),
    (1., 1825000, '1825000.0/s'),
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
    (1165263., 123, '0.38/h'),
])
def test_throughput_human(end, count, expected, rand_offset):
    t = HandleStats([rand_offset, end + rand_offset], count)

    assert t.throughput_human == expected
