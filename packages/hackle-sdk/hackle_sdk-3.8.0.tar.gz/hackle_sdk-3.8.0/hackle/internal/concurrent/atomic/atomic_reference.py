from threading import Lock


class AtomicReference(object):

    def __init__(self, value):
        self.__value = value
        self.__lock = Lock()

    def get(self):
        with self.__lock:
            return self.__value

    def get_and_set(self, value):
        with self.__lock:
            old_value = self.__value
            self.__value = value
            return old_value
