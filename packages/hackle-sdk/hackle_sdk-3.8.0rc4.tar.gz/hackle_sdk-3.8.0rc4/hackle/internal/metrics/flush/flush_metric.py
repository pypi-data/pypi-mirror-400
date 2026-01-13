import abc

from six import add_metaclass

from hackle.internal.concurrent.atomic.atomic_reference import AtomicReference
from hackle.internal.metrics.metric import Metric


@add_metaclass(abc.ABCMeta)
class FlushMetric(Metric):

    def __init__(self, id_):
        super(FlushMetric, self).__init__(id_)
        self.__current = AtomicReference(self.initial_metric())

    @property
    def current(self):
        return self.__current.get()

    def flush(self):
        return self.__current.get_and_set(self.initial_metric())

    @abc.abstractmethod
    def initial_metric(self):
        pass
