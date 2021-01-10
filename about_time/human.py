from datetime import timedelta

DURATION_HUMAN_SPEC = (
    (1.e-6, 1e9, 1e3, 'ns'),
    (1.e-3, 1e6, 1e3, 'us'),
    (1., 1e3, 1e3, 'ms'),
    (60., 1e0, 60., 's'),
)


def duration_human(value):
    """Return a beautiful representation of the duration.
    It dynamically calculates the best unit to use.

    Returns:
        str: the duration representation.

    """
    for top, mult, size, unit in DURATION_HUMAN_SPEC:
        if value < top:
            result = round(value * mult, ndigits=2)
            if result < size:
                return '{}{}'.format(result, unit)

    txt = str(timedelta(seconds=float('{:.1f}'.format(value))))
    pos = txt.find('.')
    if pos == -1:
        return txt
    return txt[:pos + 2]


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
