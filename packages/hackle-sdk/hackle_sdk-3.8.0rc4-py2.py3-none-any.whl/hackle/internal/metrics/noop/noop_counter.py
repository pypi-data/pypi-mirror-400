from hackle.internal.metrics.counter import Counter


class NoopCounter(Counter):

    def count(self):
        return 0

    def increment(self, delta=1):
        return
