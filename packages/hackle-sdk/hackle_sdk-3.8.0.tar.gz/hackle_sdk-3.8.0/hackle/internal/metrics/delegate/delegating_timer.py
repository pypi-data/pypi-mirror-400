from hackle.internal.metrics.delegate.delegating_metric import DelegatingMetric
from hackle.internal.metrics.noop.noop_timer import NoopTimer
from hackle.internal.metrics.timer import Timer


class DelegatingTimer(DelegatingMetric, Timer):

    def noop_metric(self):
        return NoopTimer(self.id)

    def register_metric(self, registry):
        return registry.register_timer(self.id)

    def count(self):
        return self.first().count()

    def total_time(self, unit):
        return self.first().total_time(unit)

    def max(self, unit):
        return self.first().max(unit)

    def record(self, duration, unit):
        for metric in self.metrics:
            metric.record(duration, unit)
