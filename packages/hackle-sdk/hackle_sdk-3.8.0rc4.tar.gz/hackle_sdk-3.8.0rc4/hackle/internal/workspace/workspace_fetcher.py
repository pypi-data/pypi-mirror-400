from hackle.internal.logger.log import Log
from hackle.internal.time.time_unit import SECONDS
from hackle.internal.workspace.workspace import Workspace


class WorkspaceFetcher(object):
    def __init__(self, http_workspace_fetcher, scheduler, polling_interval_seconds):
        """
        :param hackle.internal.workspace.http_workspace_fetcher.HttpWorkspaceFetcher http_workspace_fetcher:
        :param hackle.internal.concurrent.schedule.scheduler.Scheduler scheduler:
        :param float polling_interval_seconds:
        """
        self.__http_workspace_fetcher = http_workspace_fetcher
        self.__scheduler = scheduler
        self.__polling_interval_seconds = polling_interval_seconds
        self.__polling_job = None
        self.__workspace = None

    def fetch(self):
        """
        :rtype: Workspace or None
        """
        return self.__workspace

    def start(self):
        if self.__polling_job is None:
            self.__poll()
            self.__polling_job = self.__scheduler.schedule_periodically(
                self.__polling_interval_seconds,
                self.__polling_interval_seconds,
                SECONDS,
                self.__poll
            )

    def stop(self):
        if self.__polling_job is not None:
            self.__polling_job.cancel()
        self.__scheduler.close()

    def __poll(self):
        try:
            workspace = self.__http_workspace_fetcher.fetch_if_modified()
            if workspace is not None:
                self.__workspace = workspace
        except Exception as e:
            Log.get().error('Failed to poll Workspace: {}'.format(str(e)))
