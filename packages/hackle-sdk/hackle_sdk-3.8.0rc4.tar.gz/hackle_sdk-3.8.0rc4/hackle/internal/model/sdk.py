class Sdk(object):
    def __init__(self, key, name, version):
        """
        :param str key:
        :param str name:
        :param str version:
        """
        self.__key = key
        self.__name = name
        self.__version = version

    @property
    def key(self):
        """
        :rtype: str
        """
        return self.__key

    @property
    def name(self):
        """
        :rtype: str
        """
        return self.__name

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.__version

