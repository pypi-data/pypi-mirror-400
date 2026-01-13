class HttpHeaders(object):
    def __init__(self, headers):
        """
        :param dict[str, str] headers:
        """
        self.__headers = headers

    def get(self, name):
        """
        :param str name:
        :rtype: str
        """
        for header_name in self.__headers:
            if header_name.lower() == name.lower():
                return self.__headers.get(header_name)
        return None

    def as_dict(self):
        """
        :rtype: dict[str, str]
        """
        return self.__headers

    def to_builder(self):
        """
        :rtype: HttpHeadersBuilder
        """
        return HttpHeadersBuilder(self.__headers)

    @staticmethod
    def builder():
        """
        :rtype: HttpHeadersBuilder
        """
        return HttpHeadersBuilder({})

    IF_MODIFIED_SINCE = "If-Modified-Since"
    LAST_MODIFIED = "Last-Modified"


class HttpHeadersBuilder(object):

    def __init__(self, headers):
        """
        :param dict[str, str] headers:
        """
        self.__headers = headers

    def add(self, name, value):
        """
        :param str name:
        :param str value:
        :rtype: HttpHeadersBuilder
        """
        self.__headers[name] = value
        return self

    def build(self):
        return HttpHeaders(self.__headers)
