import json

from hackle.internal.http.http_request import HttpRequest
from hackle.internal.logger.log import Log
from hackle.internal.metrics.flush.flush_metric_registry import FlushMetricRegistry
from hackle.internal.metrics.metric import MetricType
from hackle.internal.time.clock import SYSTEM_CLOCK


# noinspection PyMethodMayBeStatic
class MonitoringMetricRegistry(FlushMetricRegistry):

    def __init__(self, monitoring_url, scheduler, flush_interval_millis, http_client):
        """
        :param str monitoring_url:
        :param hackle.internal.concurrency.schedule.scheduler.Scheduler scheduler:
        :param int flush_interval_millis:
        :param hackle.internal.http.http_client.HttpClient http_client:
        """
        super(MonitoringMetricRegistry, self).__init__(scheduler, flush_interval_millis)
        self.__url = monitoring_url + '/metrics'
        self.__http_client = http_client
        self.__clock = SYSTEM_CLOCK
        self.start()

    def flush_metric(self, metrics):
        for chunk in self.__chunk(list(filter(self.__is_dispatch_target, metrics)), 500):
            self.__dispatch(chunk)

    def __chunk(self, metrics, size):
        return [metrics[i:i + size] for i in range(0, len(metrics), size)]

    def __is_dispatch_target(self, metric):
        if metric.id.type == MetricType.COUNTER:
            return metric.count() > 0
        elif metric.id.type == MetricType.TIMER:
            return metric.count() > 0
        else:
            return False

    def __dispatch(self, metrics):
        try:
            request = self.__create_request(metrics)
            response = self.__http_client.execute(request)
            self.__handle_response(response)
        except Exception as e:
            Log.get().warning("Unexpected exception while publishing metrics: {}".format(str(e)))

    def __create_request(self, metrics):
        body = {"metrics": [self.__metric(metric) for metric in metrics]}
        return HttpRequest.builder() \
            .method("POST") \
            .url(self.__url) \
            .body(json.dumps(body)) \
            .header("Content-Type", "application/json") \
            .build()

    def __handle_response(self, response):
        """
        :param HttpResponse response:
        """
        if not response.is_successful:
            raise Exception('Http status code: {}'.format(response.status_code))

    def __metric(self, metric):
        return {
            "name": metric.id.name,
            "tags": metric.id.tags,
            "type": metric.id.type,
            "measurements": {measurement.name: measurement.value for measurement in metric.measure()}
        }
