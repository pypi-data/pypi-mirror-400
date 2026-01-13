from hackle.internal.metrics.metrics import Metrics


class ApiCallMetrics:

    @staticmethod
    def record(operation, sample, response):
        """
        :param str operation:
        :param hackle.internal.metrics.timer.TimerSample sample:
        :param hackle.internal.http.http_response.HttpResponse or None response:
        """
        tags = {
            "operation": operation,
            "success": ApiCallMetrics.__success(response)
        }
        timer = Metrics.timer("api.call", tags)
        sample.stop(timer)

    @staticmethod
    def __success(response):
        """
        :param hackle.internal.http.http_response.HttpResponse or None response:
        :rtype: str
        """
        if response is None:
            return "false"

        return "true" if response.is_successful or response.is_not_modified else "false"
