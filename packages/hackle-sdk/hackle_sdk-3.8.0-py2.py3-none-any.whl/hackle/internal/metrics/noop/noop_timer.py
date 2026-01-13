from hackle.internal.metrics.timer import Timer


class NoopTimer(Timer):

    def count(self):
        return 0

    def total_time(self, uni):
        return 0

    def max(self, unit):
        return 0

    def record(self, duration, unit):
        return
