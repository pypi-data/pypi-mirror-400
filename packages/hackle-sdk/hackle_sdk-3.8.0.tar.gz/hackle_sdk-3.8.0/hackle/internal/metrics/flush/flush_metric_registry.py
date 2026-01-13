import abc

from six import add_metaclass

from hackle.internal.metrics.flush.flush_counter import FlushCounter
from hackle.internal.metrics.flush.flush_metric import FlushMetric
from hackle.internal.metrics.flush.flush_timer import FlushTimer
from hackle.internal.metrics.push.push_metric_registry import PushMetricRegistry


@add_metaclass(abc.ABCMeta)
class FlushMetricRegistry(PushMetricRegistry):

    @abc.abstractmethod
    def flush_metric(self, metrics):
        """
        :param list[hackle.internal.metrics.metric.Metric] metrics:
        """
        pass

    def publish(self):
        metrics = []
        for metric in self.metrics:
            if isinstance(metric, FlushMetric):
                metrics.append(metric.flush())
        self.flush_metric(metrics)

    def create_counter(self, id_):
        return FlushCounter(id_)

    def create_timer(self, id_):
        return FlushTimer(id_)
