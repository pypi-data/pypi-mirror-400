from hackle.internal.logger.log import Log
from hackle.internal.metrics.flush.flush_metric_registry import FlushMetricRegistry


class LoggingMetricRegistry(FlushMetricRegistry):

    def __init__(self, scheduler, push_interval_millis):
        """
        :param hackle.internal.concurrency.schedule.scheduler.Scheduler scheduler:
        :param int push_interval_millis:
        """
        super(LoggingMetricRegistry, self).__init__(scheduler, push_interval_millis)
        self.start()

    def flush_metric(self, metrics):
        for metric in sorted(metrics, key=lambda m: m.id.name):
            self.__print(metric)

    # noinspection PyMethodMayBeStatic
    def __print(self, metric):
        name = "{} {}".format(metric.id.name, metric.id.tags)
        measurements = " ".join(
            map(lambda measurement: "{}={}".format(measurement.name, measurement.value), metric.measure()))
        message = "{} {}".format(name, measurements)
        Log.get().info(message)
