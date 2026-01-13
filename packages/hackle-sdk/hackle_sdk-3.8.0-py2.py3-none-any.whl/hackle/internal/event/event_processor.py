import threading

from six.moves.queue import Queue, Full

from hackle.internal.event.event_dispatcher import EventDispatcher
from hackle.internal.event.user_event import UserEvent
from hackle.internal.logger.log import Log
from hackle.internal.time.time_unit import SECONDS


class EventProcessor(object):
    __SHUTDOWN_SIGNAL = object()
    __FLUSH_SIGNAL = object()

    def __init__(
            self,
            queue,
            event_dispatcher,
            event_dispatch_size,
            flush_scheduler,
            flush_interval_seconds,
            shutdown_timeout_seconds):
        """
        :param Queue queue:
        :param EventDispatcher event_dispatcher:
        :param Scheduler flush_scheduler:
        :param int event_dispatch_size:
        :param float flush_interval_seconds:
        :param float shutdown_timeout_seconds:
        """
        self.__lock = threading.Lock()

        self.__queue = queue
        self.__event_dispatcher = event_dispatcher
        self.__event_dispatch_size = event_dispatch_size
        self.__flush_scheduler = flush_scheduler
        self.__flush_interval_seconds = flush_interval_seconds
        self.__shutdown_timeout_seconds = shutdown_timeout_seconds

        self.__flushing_job = None
        self.__consuming_task = None
        self.__is_started = False

        self.__current_batch = list()

    def process(self, event):
        """
        :param UserEvent event:
        """
        if not isinstance(event, UserEvent):
            Log.get().warning('Invalid event type: {}. (expected: UserEvent)'.format(type(event).__name__))
            return

        try:
            self.__queue.put_nowait(event)
        except Full:
            Log.get().warning('Event not processed. Exceeded event queue capacity. (Current queue size: {})'.format(
                str(self.__queue.qsize())))

    def __flush(self):
        self.__queue.put(self.__FLUSH_SIGNAL)

    def start(self):
        if self.__is_started:
            Log.get().info("EventProcessor is already started")
            return

        self.__consuming_task = threading.Thread(target=self.__consuming)
        self.__consuming_task.daemon = True
        self.__consuming_task.start()

        self.__flushing_job = self.__flush_scheduler.schedule_periodically(
            self.__flush_interval_seconds,
            self.__flush_interval_seconds,
            SECONDS,
            self.__flush
        )

        self.__is_started = True
        Log.get().info('EventProcessor started. Flush events every {} s.'.format(self.__flush_interval_seconds))

    def stop(self):
        if not self.__is_started:
            return

        Log.get().info('Shutting down EventProcessor')

        self.__flushing_job.cancel()
        self.__flush_scheduler.close()

        self.__queue.put(self.__SHUTDOWN_SIGNAL)

        if self.__consuming_task:
            self.__consuming_task.join(self.__shutdown_timeout_seconds)

    def __consuming(self):
        try:
            while True:
                try:
                    message = self.__queue.get(True)

                    if isinstance(message, UserEvent):
                        self.__consume_event(message)
                        continue

                    if message == self.__FLUSH_SIGNAL:
                        self.__dispatch_events()
                        continue

                    if message == self.__SHUTDOWN_SIGNAL:
                        break

                except Exception as e:
                    Log.get().debug('Unexpected exception in event processor: {}'.format(str(e)))

        except Exception as e:
            Log.get().error('Unexpected exception in event processor: {}'.format(str(e)))
        finally:
            Log.get().info('Exit Event Processing loop')
            self.__dispatch_events()

    def __consume_event(self, event):
        with self.__lock:
            self.__current_batch.append(event)

        if len(self.__current_batch) >= self.__event_dispatch_size:
            self.__dispatch_events()

    def __dispatch_events(self):
        batch_len = len(self.__current_batch)
        if batch_len == 0:
            return

        with self.__lock:
            events = list(self.__current_batch)
            self.__current_batch = list()

        try:
            self.__event_dispatcher.dispatch(events)
        except Exception as e:
            Log.get().error('Failed to dispatch events: {}'.format(str(e)))
