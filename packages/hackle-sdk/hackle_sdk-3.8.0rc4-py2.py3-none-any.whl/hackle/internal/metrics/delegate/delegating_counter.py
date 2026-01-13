from hackle.internal.metrics.counter import Counter
from hackle.internal.metrics.delegate.delegating_metric import DelegatingMetric
from hackle.internal.metrics.noop.noop_counter import NoopCounter


class DelegatingCounter(DelegatingMetric, Counter):

    def noop_metric(self):
        return NoopCounter(self.id)

    def register_metric(self, registry):
        return registry.register_counter(self.id)

    def count(self):
        return self.first().count()

    def increment(self, delta=1):
        for metric in self.metrics:
            metric.increment(delta)
