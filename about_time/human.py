from datetime import timedelta

DURATION_HUMAN_SPEC = (
    (1.e-6, 1.e9, 1.e3, 'ns'),
    (1.e-3, 1.e6, 1.e3, 'µs'),
    (1., 1.e3, 1.e3, 'ms'),
    (60., 1., 1., 's'),  # size=1 because it won't change the unit.
    # 00:01:00 and beyond in code.
)


def duration_human(value):
    """Return a beautiful representation of some duration.
    It dynamically calculates the best unit to use.

    Args:
        value (float): value to be formatted

    Returns:
        str: the human friendly representation.

    """
    enter = next((i for i, s in enumerate(DURATION_HUMAN_SPEC) if value < s[0]), 99)
    if enter != 99:
        value *= DURATION_HUMAN_SPEC[enter][1]

    for _, _, size, unit in DURATION_HUMAN_SPEC[enter:]:
        if value < 9.995:
            return '{:1.2f}{}'.format(value, unit)
        if value < 99.95:
            return '{:2.1f}{}'.format(value, unit)
        if value < 999.5:
            return '{:3.0f}{}'.format(value, unit)
        value /= size

    return str(timedelta(seconds=round(value, 0)))


THROUGHPUT_HUMAN_SPEC = (
    (1. / 60 / 24, 60 * 60 * 24, 24, '/d'),
    (1. / 60, 60 * 60, 60, '/h'),
    (1., 60, 60, '/m'),
    (float('inf'), 1, float('inf'), '/s'),
)


def throughput_human(value):
    """Return a beautiful representation of the current throughput.
    It dynamically calculates the best unit to use.

    Returns:
        str: the duration representation.

    """
    for top, mult, size, unit in THROUGHPUT_HUMAN_SPEC:
        if value < top:
            result = round(value * mult, ndigits=2)
            if result < size:
                return '{}{}'.format(result, unit)
    return '?'
