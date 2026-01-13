from threading import Lock


class AtomicFloat(object):

    def __init__(self, value=0.0):
        self.__value = value
        self.__lock = Lock()

    def get(self):
        """
        :rtype: float
        """
        with self.__lock:
            return self.__value

    def add_and_get(self, delta):
        """
        :param float delta:
        :rtype: float
        """
        with self.__lock:
            self.__value += delta
            return self.__value

    def accumulate_and_get(self, value, accumulator):
        """
        :param float value:
        :param function accumulator:
        :rtype: float
        """
        with self.__lock:
            prev = self.__value
            next_ = accumulator(prev, value)
            self.__value = next_
            return next_
