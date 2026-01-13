import abc

from six import add_metaclass

from hackle.internal.time.time_unit import TimeUnit


@add_metaclass(abc.ABCMeta)
class Scheduler(object):

    @abc.abstractmethod
    def schedule_periodically(self, delay, period, unit, task):
        """
        :param float delay:
        :param float period:
        :param TimeUnit unit:
        :param function task:
        :rtype: ScheduledJob
        """
        pass

    @abc.abstractmethod
    def close(self):
        pass


@add_metaclass(abc.ABCMeta)
class ScheduledJob(object):
    @abc.abstractmethod
    def cancel(self):
        pass
