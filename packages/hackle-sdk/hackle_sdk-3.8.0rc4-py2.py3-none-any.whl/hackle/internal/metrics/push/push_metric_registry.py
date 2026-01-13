import abc
from threading import Lock

from six import add_metaclass

from hackle.internal.logger.log import Log
from hackle.internal.metrics.metric_registry import MetricRegistry
from hackle.internal.time.clock import SYSTEM_CLOCK
from hackle.internal.time.time_unit import MILLISECONDS


@add_metaclass(abc.ABCMeta)
class PushMetricRegistry(MetricRegistry):

    def __init__(self, scheduler, push_interval_millis):
        """
        :param hackle.internal.concurrency.schedule.scheduler.Scheduler scheduler:
        :param in push_interval_millis:
        """
        super(PushMetricRegistry, self).__init__()
        self.__lock = Lock()
        self.__scheduler = scheduler
        self.__push_interval_millis = push_interval_millis
        self.__publishing_job = None

    @abc.abstractmethod
    def publish(self):
        pass

    def __safe_publish(self):
        try:
            self.publish()
        except Exception as e:
            Log.get().warning(
                "Unexpected exception while publishing metrics for [{}]: {}".format(self.__class__.__name__, str(e)))

    def start(self):
        with self.__lock:
            if self.__publishing_job is not None:
                return
            delay = self.__push_interval_millis - (SYSTEM_CLOCK.current_millis() % self.__push_interval_millis) + 1
            self.__publishing_job = self.__scheduler.schedule_periodically(delay,
                                                                           self.__push_interval_millis,
                                                                           MILLISECONDS,
                                                                           self.__safe_publish)

            Log.get().info(
                "{} started. Publish metrics every {}ms".format(self.__class__.__name__, self.__push_interval_millis))

    def stop(self):
        with self.__lock:
            if self.__publishing_job is None:
                return
            self.__publishing_job.cancel()
            self.__publishing_job = None
            self.__safe_publish()
            Log.get().info("{} stopped".format(self.__class__.__name__))

    def close(self):
        self.stop()
        self.__scheduler.close()
