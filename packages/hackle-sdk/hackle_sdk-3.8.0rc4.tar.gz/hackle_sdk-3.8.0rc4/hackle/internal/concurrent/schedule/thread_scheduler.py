import time
from threading import Thread, Event

from hackle.internal.concurrent.schedule.scheduler import Scheduler, ScheduledJob
from hackle.internal.logger.log import Log
from hackle.internal.time.time_unit import SECONDS


class ThreadScheduledJob(ScheduledJob):

    def __init__(self, delay, period, task):
        super(ThreadScheduledJob, self).__init__()
        self.__delay = delay
        self.__period = period
        self.__task = task
        self.__stop = Event()
        self.__thread = Thread(target=self.__run)
        self.__thread.daemon = True

    def start(self):
        self.__thread.start()

    def cancel(self):
        self.__stop.set()

    def __run(self):
        if self.__delay > 0:
            if self.__stop.wait(self.__delay):
                return

        is_stopped = self.__stop.is_set()
        while not is_stopped:
            next_time = time.time() + self.__period
            try:
                self.__task()
            except Exception as e:
                Log.get().error("Unexpected exception on scheduler: {}".format(str(e)))
            delay = next_time - time.time()
            is_stopped = self.__stop.wait(delay) if delay > 0 else self.__stop.is_set()


class ThreadScheduler(Scheduler):

    def __init__(self):
        super(ThreadScheduler, self).__init__()

    def schedule_periodically(self, delay, period, unit, task):
        job = ThreadScheduledJob(SECONDS.convert(delay, unit), SECONDS.convert(period, unit), task)
        job.start()
        return job

    def close(self):
        pass
