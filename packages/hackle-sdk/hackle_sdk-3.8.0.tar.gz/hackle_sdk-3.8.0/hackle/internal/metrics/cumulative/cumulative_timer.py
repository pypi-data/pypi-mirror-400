from hackle.internal.concurrent.atomic.atomic_float import AtomicFloat
from hackle.internal.concurrent.atomic.atomic_integer import AtomicInteger
from hackle.internal.metrics.timer import Timer
from hackle.internal.time.time_unit import nanos_to_unit, NANOSECONDS


class CumulativeTimer(Timer):

    def __init__(self, id_):
        super(CumulativeTimer, self).__init__(id_)
        self.__count = AtomicInteger()
        self.__total = AtomicFloat()
        self.__max = AtomicFloat()

    def count(self):
        return self.__count.get()

    def total_time(self, unit):
        return nanos_to_unit(self.__total.get(), unit)

    def max(self, unit):
        return nanos_to_unit(self.__max.get(), unit)

    def record(self, duration, unit):
        if duration < 0:
            return
        nanos = NANOSECONDS.convert(duration, unit)
        self.__count.add_and_get(1)
        self.__total.add_and_get(nanos)
        self.__max.accumulate_and_get(nanos, max)
