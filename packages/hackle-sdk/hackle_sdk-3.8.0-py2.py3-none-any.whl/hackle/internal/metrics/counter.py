import abc

from six import add_metaclass

from hackle.internal.metrics.measurement import Measurement, Measurements
from hackle.internal.metrics.metric import Metric, MetricId, MetricType


@add_metaclass(abc.ABCMeta)
class Counter(Metric):

    @abc.abstractmethod
    def count(self):
        """
        :rtype: int
        """
        pass

    @abc.abstractmethod
    def increment(self, delta=1):
        """
        :param int delta:
        :rtype: None
        """
        pass

    def measure(self):
        """
        :rtype: list[hackle.internal.metrics.measurement.Measurement]
        """
        return [Measurement(Measurements.COUNT, lambda: float(self.count()))]


class CounterBuilder:

    def __init__(self, name):
        """
        :param str name:
        """
        self.__name = name
        self.__tags = {}

    def tags(self, tags):
        """
        :param dict[str, str] tags:
        :rtype: hackle.internal.metrics.counter.CounterBuilder
        """
        for key in tags.keys():
            self.__tags[key] = tags[key]
        return self

    def tag(self, key, value):
        """
        :param str key:
        :param str value:
        :rtype: hackle.internal.metrics.counter.CounterBuilder
        """
        self.__tags[key] = value
        return self

    def register(self, registry):
        """
        :param hackle.internal.metrics.metric_registry.MetricRegistry registry:
        :rtype: hackle.internal.metrics.counter.Counter
        """
        metric_id = MetricId(self.__name, self.__tags, MetricType.COUNTER)
        return registry.register_counter(metric_id)
