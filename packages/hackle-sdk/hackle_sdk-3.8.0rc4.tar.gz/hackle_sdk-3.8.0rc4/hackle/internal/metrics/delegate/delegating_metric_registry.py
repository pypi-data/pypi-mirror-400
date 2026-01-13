from hackle.internal.metrics.delegate.delegating_counter import DelegatingCounter
from hackle.internal.metrics.delegate.delegating_metric import DelegatingMetric
from hackle.internal.metrics.delegate.delegating_timer import DelegatingTimer
from hackle.internal.metrics.metric_registry import MetricRegistry


class DelegatingMetricRegistry(MetricRegistry):

    def __init__(self):
        super(DelegatingMetricRegistry, self).__init__()
        self.__registries = set()

    def create_counter(self, id_):
        counter = DelegatingCounter(id_)
        self.__add_registries(counter)
        return counter

    def create_timer(self, id_):
        timer = DelegatingTimer(id_)
        self.__add_registries(timer)
        return timer

    def __add_registries(self, metric):
        for registry in self.__registries:
            metric.add(registry)

    def add(self, registry):
        """
        :param hackle.internal.metrics.metric_registry.MetricRegistry registry:
        """
        if isinstance(registry, DelegatingMetricRegistry):
            return

        with self._lock:
            if registry not in self.__registries:
                self.__registries.add(registry)
                for metric in self.metrics:
                    if isinstance(metric, DelegatingMetric):
                        metric.add(registry)

    def close(self):
        for registry in self.__registries:
            registry.close()
