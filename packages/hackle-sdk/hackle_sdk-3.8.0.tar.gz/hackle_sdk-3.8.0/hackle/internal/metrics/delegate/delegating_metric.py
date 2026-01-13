import abc
from threading import Lock

from six import add_metaclass

from hackle.internal.metrics.metric import Metric


@add_metaclass(abc.ABCMeta)
class DelegatingMetric(Metric):

    def __init__(self, id_):
        super(DelegatingMetric, self).__init__(id_)
        self.__lock = Lock()
        self.__metrics = {}

    @property
    def metrics(self):
        """
        :rtype: list[hackle.internal.metrics.metric.Metric]
        """
        return list(self.__metrics.values())

    def first(self):
        """
        :rtype: hackle.internal.metrics.metric.Metric
        """
        metric = self.metrics
        return metric[0] if len(metric) > 0 else self.noop_metric()

    def add(self, registry):
        new_metric = self.register_metric(registry)
        with self.__lock:
            new_metrics = self.__metrics.copy()
            new_metrics[registry] = new_metric
            self.__metrics = new_metrics

    @abc.abstractmethod
    def noop_metric(self):
        """
        :rtype: hackle.internal.metrics.metric.Metric
        """
        pass

    @abc.abstractmethod
    def register_metric(self, registry):
        """
        :param hackle.internal.metrics.metric_registry.MetricRegistry registry:
        :rtype: hackle.internal.metrics.metric.Metric
        """
        pass
