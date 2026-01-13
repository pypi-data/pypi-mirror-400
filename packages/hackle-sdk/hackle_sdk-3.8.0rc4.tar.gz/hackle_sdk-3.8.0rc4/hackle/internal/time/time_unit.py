_C0 = 1.0
_C1 = _C0 * 1000
_C2 = _C1 * 1000
_C3 = _C2 * 1000

_C = [_C0, _C1, _C2, _C3]


class TimeUnit:
    def __init__(self, index):
        """
        :param int index:
        """
        self.__index = index

    @property
    def index(self):
        return self.__index

    def convert(self, source_duration, source_unit):
        """
        :param float source_duration:
        :param TimeUnit source_unit:
        :return:
        """
        return source_duration / (_C[self.index] / _C[source_unit.index])


NANOSECONDS = TimeUnit(0)
MICROSECONDS = TimeUnit(1)
MILLISECONDS = TimeUnit(2)
SECONDS = TimeUnit(3)


def nanos_to_unit(nanos, unit):
    return unit.convert(nanos, NANOSECONDS)
