from hackle.internal.http.http_headers import HttpHeaders


class HttpResponse(object):
    def __init__(self, status_code, body, headers):
        """
        :param int status_code:
        :param str or None body:
        :param hackle.internal.http.http_headers.HttpHeaders headers:
        """
        self.__status_code = status_code
        self.__body = body
        self.__headers = headers

    @staticmethod
    def of(statue_code, body=None, headers=None):
        """
        :param int statue_code:
        :param str or None body:
        :param hackle.internal.http.http_headers.HttpHeaders or None headers:
        :rtype: HttpResponse
        """
        return HttpResponse(statue_code, body, headers or HttpHeaders.builder().build())

    @property
    def status_code(self):
        """
        :rtype: int
        """
        return self.__status_code

    @property
    def body(self):
        """
        :rtype: str or None
        """
        return self.__body

    @property
    def headers(self):
        """
        :rtype: hackle.internal.http.http_headers.HttpHeaders
        """
        return self.__headers

    @property
    def is_successful(self):
        return 200 <= self.__status_code < 300

    @property
    def is_not_modified(self):
        return self.__status_code == 304
