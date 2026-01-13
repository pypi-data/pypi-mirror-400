from threading import Lock


class AtomicInteger(object):

    def __init__(self, value=0):
        self.__value = value
        self.__lock = Lock()

    def get(self):
        """
        :rtype: int
        """
        with self.__lock:
            return self.__value

    def add_and_get(self, delta):
        """
        :param int delta:
        :rtype: int
        """
        with self.__lock:
            self.__value += delta
            return self.__value

    def get_and_add(self, delta):
        """
        :param int delta:
        :rtype: int
        """
        with self.__lock:
            old_value = self.__value
            self.__value += delta
            return old_value
