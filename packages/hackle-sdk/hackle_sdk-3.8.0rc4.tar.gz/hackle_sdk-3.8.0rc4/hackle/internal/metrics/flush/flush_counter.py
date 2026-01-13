from hackle.internal.metrics.counter import Counter
from hackle.internal.metrics.cumulative.cumulative_counter import CumulativeCounter
from hackle.internal.metrics.flush.flush_metric import FlushMetric


class FlushCounter(FlushMetric, Counter):
    def initial_metric(self):
        return CumulativeCounter(self.id)

    def count(self):
        return self.current.count()

    def increment(self, delta=1):
        self.current.increment(delta)
