from hackle.internal.http.http_headers import HttpHeaders


class HttpRequest(object):
    def __init__(
            self,
            url,
            method,
            body,
            headers
    ):
        """
        :param str url:
        :param str method:
        :param str body:
        :param hackle.internal.http.http_headers.HttpHeaders headers:
        """
        self.__url = url
        self.__method = method
        self.__body = body
        self.__headers = headers

    @staticmethod
    def builder():
        """
        :rtype: HttpRequestBuilder
        """
        return HttpRequestBuilder()

    def to_builder(self):
        """
        :rtype: HttpRequestBuilder
        """
        return HttpRequestBuilder(self)

    @property
    def url(self):
        """
        :rtype str:
        """
        return self.__url

    @property
    def method(self):
        """
        :rtype: str
        """
        return self.__method

    @property
    def body(self):
        """
        :rtype: str or None
        """
        return self.__body

    @property
    def headers(self):
        """
        :rtype hackle.internal.http.http_headers.HttpHeaders:
        """
        return self.__headers


class HttpRequestBuilder(object):
    def __init__(self, request=None):
        """
        :param HttpRequest or None request:
        """
        self.__url = None
        self.__method = "GET"
        self.__body = None
        self.__headers = HttpHeaders.builder()
        if request is not None:
            self.__url = request.url
            self.__method = request.method
            self.__body = request.body
            self.__headers = request.headers.to_builder()

    def url(self, url):
        """
        :param str url:
        :rtype: HttpRequestBuilder
        """
        self.__url = url
        return self

    def method(self, method):
        """
        :param str method:
        :rtype: HttpRequestBuilder
        """
        self.__method = method
        return self

    def body(self, body):
        """
        :param str body:
        :rtype: HttpRequestBuilder
        """
        self.__body = body
        return self

    def header(self, name, value):
        """
        :param str name:
        :param str value:
        :rtype: HttpRequestBuilder
        """
        self.__headers.add(name, value)
        return self

    def build(self):
        if self.__url is None:
            raise Exception('url is None')

        return HttpRequest(
            self.__url,
            self.__method,
            self.__body,
            self.__headers.build()
        )
