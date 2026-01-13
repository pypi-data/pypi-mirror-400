from hackle.internal.metrics.cumulative.cumulative_counter import CumulativeCounter
from hackle.internal.metrics.cumulative.cumulative_timer import CumulativeTimer
from hackle.internal.metrics.metric_registry import MetricRegistry


class CumulativeMetricRegistry(MetricRegistry):

    def create_counter(self, id_):
        return CumulativeCounter(id_)

    def create_timer(self, id_):
        return CumulativeTimer(id_)

    def close(self):
        pass
