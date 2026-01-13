from hackle.internal.metrics.cumulative.cumulative_timer import CumulativeTimer
from hackle.internal.metrics.flush.flush_metric import FlushMetric
from hackle.internal.metrics.timer import Timer


class FlushTimer(FlushMetric, Timer):
    def initial_metric(self):
        return CumulativeTimer(self.id)

    def count(self):
        return self.current.count()

    def total_time(self, unit):
        return self.current.total_time(unit)

    def max(self, unit):
        return self.current.max(unit)

    def record(self, duration, unit):
        return self.current.record(duration, unit)
