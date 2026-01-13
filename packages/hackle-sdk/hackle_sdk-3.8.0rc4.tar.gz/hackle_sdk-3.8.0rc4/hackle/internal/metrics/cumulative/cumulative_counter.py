from hackle.internal.concurrent.atomic.atomic_integer import AtomicInteger
from hackle.internal.metrics.counter import Counter


class CumulativeCounter(Counter):

    def __init__(self, id_):
        super(CumulativeCounter, self).__init__(id_)
        self.__value = AtomicInteger()

    def count(self):
        return self.__value.get()

    def increment(self, delta=1):
        self.__value.add_and_get(delta)
