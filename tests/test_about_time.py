from unittest import mock

import pytest

from about_time import about_time
from about_time.about_time import Handle


@pytest.fixture(params=[True, False])
def bool1(request):
    return request.param


def test_timer_context_manager_and_callable_handler():
    start, end = 1.4, 2.65
    with mock.patch('time.perf_counter') as mt:
        mt.side_effect = (start, end)

        if bool1:
            with about_time() as t:
                pass
        else:
            t = about_time(lambda: 1)

    assert t.duration == end - start


def test_context_manager_dont_have_result():
    with about_time() as t:
        pass

    with pytest.raises(AttributeError):
        x = t.result


def test_callable_handler_has_result():
    t = about_time(lambda: 1)
    assert t.result == 1


@pytest.mark.parametrize('duration, expected', [
    (.00001, '0.0s'),
    (.01, '0.01s'),
    (.014, '0.01s'),
    (.015, '0.01s'),
    (.0199999, '0.01s'),
    (.1099999, '0.1s'),
    (.1599999, '0.15s'),
    (.8015, '0.8s'),
    (3.434999, '3.43s'),
    (59.99, '59.99s'),
    (59.999, '59.99s'),
    (60.0, '0:01:00'),
    (68.09, '0:01:08'),
    (60.9, '0:01:00.9'),
    (60.99, '0:01:00.9'),
    (125.825, '0:02:05.8'),
    (4488.395, '1:14:48.3'),
])
def test_duration_precision(duration, expected, bool1):
    with mock.patch.object(Handle, 'duration', new_callable=mock.PropertyMock) as md:
        md.return_value = duration

        if bool1:
            with about_time() as t:
                pass
        else:
            t = about_time(lambda: 1)

        assert t.duration_human == expected
