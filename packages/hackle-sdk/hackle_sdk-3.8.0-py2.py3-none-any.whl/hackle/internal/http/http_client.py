import requests

from hackle.internal.http.http_headers import HttpHeaders
from hackle.internal.http.http_response import HttpResponse
from hackle.internal.model.sdk import Sdk
from hackle.internal.time.clock import SYSTEM_CLOCK, Clock


class HttpClient(object):
    __SDK_KEY_HEADER_NAME = 'X-HACKLE-SDK-KEY'
    __SDK_NAME_HEADER_NAME = 'X-HACKLE-SDK-NAME'
    __SDK_VERSION_HEADER_NAME = 'X-HACKLE-SDK-VERSION'
    __SDK_TIME_HEADER_NAME = 'X-HACKLE-SDK-TIME'
    __CONTENT_TYPE_HEADER_NAME = 'Content-Type'
    __CONTENT_TYPE_VALUE = 'application/json'
    __TIMEOUT_SECONDS = 10

    def __init__(self, sdk, clock=SYSTEM_CLOCK):
        """
        :param Sdk sdk:
        :param Clock clock:
        """
        self.__sdk = sdk
        self.__clock = clock

    def execute(self, request):
        """
        :param hackle.internal.http.http_request.HttpRequest request:
        :rtype: hackle.internal.http.http_response.HttpResponse
        """
        new_request = self.__decorate(request)
        response = requests.request(
            new_request.method,
            new_request.url,
            data=new_request.body,
            headers=new_request.headers.as_dict(),
            timeout=self.__TIMEOUT_SECONDS
        )
        return HttpResponse(
            response.status_code,
            response.content.decode('utf-8'),
            HttpHeaders(dict(response.headers))
        )

    def __decorate(self, request):
        """
        :param hackle.internal.http.http_request.HttpRequest request:
        :rtype: hackle.internal.http.http_request.HttpRequest
        """
        return request.to_builder() \
            .header(self.__SDK_KEY_HEADER_NAME, self.__sdk.key) \
            .header(self.__SDK_NAME_HEADER_NAME, self.__sdk.name) \
            .header(self.__SDK_VERSION_HEADER_NAME, self.__sdk.version) \
            .header(self.__SDK_TIME_HEADER_NAME, str(self.__clock.current_millis())) \
            .build()
