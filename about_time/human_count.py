from .features import FEATURES

SI_1000_SPEC = ('', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
SI_1024_SPEC = ('', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
IEC_1024_SPEC = ('', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi')
DECIMALS = [1, 1, 1, 2, 2, 2, 2, 2, 2]


def div_spec() -> (int, tuple):
    return {
        (False, False): (1000, SI_1000_SPEC),
        (True, False): (1024, SI_1024_SPEC),
        (True, True): (1024, IEC_1024_SPEC),
    }[(FEATURES.feature_1024, FEATURES.feature_iec)]


def as_human(val: float, unit: str):
    space = FEATURES.conv_space
    divisor, spec = div_spec()
    for scale, dec in zip(spec, DECIMALS):
        r = round(val, dec)
        if r >= divisor:
            val /= divisor
        elif r % 1. == 0.:
            return '{:.0f}{}{}{}'.format(r, space, scale, unit)
        elif (r * 10.) % 1. == 0.:
            return '{:.1f}{}{}{}'.format(r, space, scale, unit)
        else:
            return '{:.2f}{}{}{}'.format(r, space, scale, unit)

    return '{:.2f}{}+{}'.format(val, space, unit)


class HumanCount(object):
    def __init__(self, value, unit):
        assert value >= 0.
        self._value = value
        self._unit = unit

    @property
    def value(self):
        return self._value

    def unit(self, value: str) -> 'HumanCount':
        self._unit = value
        return self

    def as_human(self) -> str:
        """Return a beautiful representation of this count.
        It dynamically calculates the best scale to use.

        Returns:
            the human friendly representation.

        """
        return as_human(self._value, self._unit)

    def __str__(self):
        return self.as_human()

    def __repr__(self):  # pragma: no cover
        return 'HumanCount{{ value={} }} -> {}'.format(self._value, self)

    def __eq__(self, other):
        return self.__str__() == other
