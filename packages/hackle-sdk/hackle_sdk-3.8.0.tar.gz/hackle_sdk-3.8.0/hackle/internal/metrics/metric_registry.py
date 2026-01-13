import abc
from threading import Lock

from six import add_metaclass

from hackle.internal.metrics.counter import CounterBuilder
from hackle.internal.metrics.timer import TimerBuilder


@add_metaclass(abc.ABCMeta)
class MetricRegistry(object):

    def __init__(self):
        self._lock = Lock()
        self.__metrics = {}

    @property
    def metrics(self):
        """
        :rtype: list[hackle.internal.metrics.metric.Metric]
        """
        return list(self.__metrics.values())

    @abc.abstractmethod
    def create_counter(self, id_):
        """
        :param hackle.internal.metrics.metric.MetricId id_:
        :rtype: hackle.internal.metrics.counter.Counter
        """
        pass

    @abc.abstractmethod
    def create_timer(self, id_):
        """
        :param hackle.internal.metrics.metric.MetricId id_:
        :rtype: hackle.internal.metrics.timer.Timer
        """
        pass

    @abc.abstractmethod
    def close(self):
        pass

    def counter(self, name, tags=None):
        """
        :param str name:
        :param dict[str, str] tags:
        :rtype: hackle.internal.metrics.counter.Counter
        """
        if tags is None:
            tags = {}
        return CounterBuilder(name).tags(tags).register(self)

    def timer(self, name, tags=None):
        """
        :param str name:
        :param dict[str, str] tags:
        :rtype: hackle.internal.metrics.timer.Timer
        """
        if tags is None:
            tags = {}
        return TimerBuilder(name).tags(tags).register(self)

    def register_counter(self, id_):
        """
        :param hackle.internal.metrics.metric.MetricId id_:
        :rtype: hackle.internal.metrics.counter.Counter
        """
        return self.__register_metric_if_necessary(id_, self.create_counter)

    def register_timer(self, id_):
        """
        :param hackle.internal.metrics.metric.MetricId id_:
        :rtype: hackle.internal.metrics.timer.Timer
        """
        return self.__register_metric_if_necessary(id_, self.create_timer)

    def __register_metric_if_necessary(self, id_, create):
        with self._lock:
            metric = self.__metrics.get(id_)
            if metric is not None:
                return metric
            metric = create(id_)
            self.__metrics[id_] = metric
            return metric
