from hackle.internal.metrics.delegate.delegating_metric_registry import DelegatingMetricRegistry


class Metrics:
    __global_registry = DelegatingMetricRegistry()

    @staticmethod
    def add_registry(registry):
        """
        :param hackle.internal.metrics.metric_registry.MetricRegistry registry:
        :rtype: None
        """
        Metrics.__global_registry.add(registry)

    @staticmethod
    def counter(name, tags=None):
        """
        :param str name:
        :param dict[str, str] tags:
        :rtype: hackle.internal.metrics.counter.Counter
        """
        return Metrics.__global_registry.counter(name, tags)

    @staticmethod
    def timer(name, tags=None):
        """
        :param str name:
        :param dict[str, str] tags:
        :rtype: hackle.internal.metrics.timer.Timer
        """
        return Metrics.__global_registry.timer(name, tags)
