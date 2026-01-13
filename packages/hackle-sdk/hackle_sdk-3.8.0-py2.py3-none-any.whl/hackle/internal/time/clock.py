import abc
import time

from six import add_metaclass

from hackle.internal.time.time_unit import NANOSECONDS, MILLISECONDS, SECONDS


@add_metaclass(abc.ABCMeta)
class Clock:

    @abc.abstractmethod
    def current_millis(self):
        """
        :return: epoch millis
        :rtype: int
        """
        pass

    @abc.abstractmethod
    def tick(self):
        """
        :return: nanoseconds
        :rtype: int
        """
        pass


class SystemClock(Clock):

    def current_millis(self):
        return int(round(MILLISECONDS.convert(time.time(), SECONDS)))

    def tick(self):
        return int(NANOSECONDS.convert(time.time(), SECONDS))


SYSTEM_CLOCK = SystemClock()
