from hackle.internal.http.http_headers import HttpHeaders
from hackle.internal.http.http_request import HttpRequest
from hackle.internal.http.http_response import HttpResponse
from hackle.internal.metrics.timer import TimerSample
from hackle.internal.monitoring.metrics.api_call_metrics import ApiCallMetrics
from hackle.internal.workspace.workspace import Workspace


class HttpWorkspaceFetcher(object):

    def __init__(self, sdk_url, sdk, http_client):
        """
        :param str sdk_url:
        :param hackle.internal.model.sdk.Sdk sdk:
        :param hackle.internal.http.http_client.HttpClient http_client:
        """
        self.__url = sdk_url + '/api/v2/workspaces/' + sdk.key + '/config'
        self.__http_client = http_client
        self.__last_modified = None  # type: str or None

    def fetch_if_modified(self):
        """
        :rtype: Workspace or None
        """
        request = self.__create_request()
        response = self.__execute(request)
        return self.__handle_response(response)

    def __create_request(self):
        builder = HttpRequest.builder().url(self.__url).method('GET')
        if self.__last_modified is not None:
            builder.header(HttpHeaders.IF_MODIFIED_SINCE, self.__last_modified)
        return builder.build()

    def __execute(self, request):
        """
        :param HttpRequest request:
        :rtype: HttpResponse
        """
        sample = TimerSample.start()
        try:
            response = self.__http_client.execute(request)
            ApiCallMetrics.record("get.workspace", sample, response)
            return response
        except Exception as e:
            ApiCallMetrics.record("get.workspace", sample, None)
            raise e

    # noinspection PyMethodMayBeStatic
    def __handle_response(self, response):
        """
        :param HttpResponse response:
        :rtype: Workspace or None
        """
        if response.is_not_modified:
            return None

        if not response.is_successful:
            raise Exception('Http status code: {}'.format(response.status_code))

        if response.body is None:
            raise Exception('Response body is empty')

        self.__last_modified = response.headers.get(HttpHeaders.LAST_MODIFIED)
        return Workspace(response.body)
