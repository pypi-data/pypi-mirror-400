import abc

from six import add_metaclass

from hackle.internal.metrics.measurement import Measurement, Measurements
from hackle.internal.metrics.metric import Metric, MetricId, MetricType
from hackle.internal.time.clock import SYSTEM_CLOCK
from hackle.internal.time.time_unit import MILLISECONDS, NANOSECONDS


@add_metaclass(abc.ABCMeta)
class Timer(Metric):

    @abc.abstractmethod
    def count(self):
        """
        :rtype: int
        """
        pass

    @abc.abstractmethod
    def total_time(self, unit):
        """
        :param hackle.internal.time.time_unit.TimeUnit unit:
        :rtype: float
        """
        pass

    @abc.abstractmethod
    def max(self, unit):
        """
        :param hackle.internal.time.time_unit.TimeUnit unit:
        :rtype: float
        """
        pass

    def mean(self, unit):
        """
        :param hackle.internal.time.time_unit.TimeUnit unit:
        :rtype: float
        """
        count = self.count()
        if count == 0:
            return 0
        else:
            return self.total_time(unit) / count

    @abc.abstractmethod
    def record(self, duration, unit):
        """
        :param float duration:
        :param hackle.internal.time.time_unit.TimeUnit unit:
        :rtype: None
        """
        pass

    def measure(self):
        """
        :rtype: list[hackle.internal.metrics.measurement.Measurement]
        """
        return [
            Measurement(Measurements.COUNT, lambda: float(self.count())),
            Measurement(Measurements.TOTAL, lambda: self.total_time(MILLISECONDS)),
            Measurement(Measurements.MAX, lambda: self.max(MILLISECONDS)),
            Measurement(Measurements.MEAN, lambda: self.mean(MILLISECONDS))
        ]


class TimerSample:
    def __init__(self, clock=SYSTEM_CLOCK):
        """
        :param hackle.internal.time.clock.Clock clock:
        """
        self.__clock = clock
        self.__start_tick = clock.tick()

    @staticmethod
    def start(clock=SYSTEM_CLOCK):
        return TimerSample(clock)

    def stop(self, timer):
        """
        :param hackle.internal.metrics.timer.Timer timer:
        :rtype: int
        """
        duration_nanos = self.__clock.tick() - self.__start_tick
        timer.record(duration_nanos, NANOSECONDS)
        return duration_nanos


class TimerBuilder:

    def __init__(self, name):
        """
        :param str name:
        """
        self.__name = name
        self.__tags = {}

    def tags(self, tags):
        """
        :param dict[str, str] tags:
        :rtype: hackle.internal.metrics.timer.TimerBuilder
        """
        for key in tags.keys():
            self.__tags[key] = tags[key]
        return self

    def tag(self, key, value):
        """
        :param str key:
        :param str value:
        :rtype: hackle.internal.metrics.timer.TimerBuilder
        """
        self.__tags[key] = value
        return self

    def register(self, registry):
        """
        :param hackle.internal.metrics.metric_registry.MetricRegistry registry:
        :rtype: hackle.internal.metrics.timer.Timer
        """
        metric_id = MetricId(self.__name, self.__tags, MetricType.TIMER)
        return registry.register_timer(metric_id)
