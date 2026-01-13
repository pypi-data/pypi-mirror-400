from six.moves.queue import Queue

from . import exceptions as hackle_exceptions
from . import logger as _logging
from . import version
from .config import HackleConfig
from .decision import ExperimentDecision, DecisionReason, FeatureFlagDecision
from .internal.concurrent.schedule.thread_scheduler import ThreadScheduler
from .internal.event.event_dispatcher import EventDispatcher
from .internal.event.event_processor import EventProcessor
from .internal.hackle_core import HackleCore
from .internal.http.http_client import HttpClient
from .internal.logger.log import Log
from .internal.metrics.metrics import Metrics
from .internal.metrics.timer import TimerSample
from .internal.model.sdk import Sdk
from .internal.monitoring.metrics.decision_metrics import DecisionMetrics
from .internal.monitoring.metrics.monitoring_metric_registry import MonitoringMetricRegistry
from .internal.type import hackle_types
from .internal.user.hackle_user_resolver import HackleUserResolver
from .internal.workspace.http_workspace_fetcher import HttpWorkspaceFetcher
from .internal.workspace.workspace_fetcher import WorkspaceFetcher
from .model import HackleEvent, HackleRemoteConfig, PropertyOperations
from .remote_config import HackleRemoteConfigImpl


def __singleton(cls):
    instance = [None]

    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper


@__singleton
class Client(object):
    def __init__(self, sdk_key=None, logger=None, config=None):
        if sdk_key is None:
            raise hackle_exceptions.RequiredParameterException('sdk_key must not be empty.')

        Log.initialize(_logging.adapt_logger(logger or _logging.NoOpLogger()))

        if config is None:
            config = HackleConfig.default()

        sdk = Sdk(sdk_key, "python-sdk", version.__version__)
        http_client = HttpClient(sdk)
        scheduler = ThreadScheduler()

        metric_registry = MonitoringMetricRegistry(
            monitoring_url=config.monitoring_url,
            scheduler=scheduler,
            flush_interval_millis=60000,
            http_client=http_client
        )
        Metrics.add_registry(metric_registry)

        http_workspace_fetcher = HttpWorkspaceFetcher(
            sdk_url=config.sdk_url,
            sdk=sdk,
            http_client=http_client
        )

        workspace_fetcher = WorkspaceFetcher(
            http_workspace_fetcher=http_workspace_fetcher,
            scheduler=scheduler,
            polling_interval_seconds=10
        )

        event_processor = EventProcessor(
            queue=Queue(maxsize=1000),
            event_dispatcher=EventDispatcher(config.event_url, http_client),
            event_dispatch_size=500,
            flush_scheduler=ThreadScheduler(),
            flush_interval_seconds=10,
            shutdown_timeout_seconds=10
        )

        workspace_fetcher.start()
        event_processor.start()

        self._core = HackleCore.create(workspace_fetcher, event_processor)
        self._user_resolver = HackleUserResolver()

    def close(self):
        self._core.close()

    def __exit__(self):
        self.close()

    def variation(self, experiment_key, user, default_variation='A'):
        """
        Decide the variation to expose to the user for experiment.

        This method return the "A" if:
            - The experiment key is invalid
            - The experiment has not started yet
            - The user is not allocated to the experiment
            - The decided variation has been dropped

        :param int experiment_key: the unique key of the experiment.
        :param hackle.model.User or hackle.model.HackleUser user: the user to participate in the experiment.
        :param str default_variation: the default variation of the experiment.

        :rtype: str
        :return: the decided variation for the user, or the default variation.
        """
        return self.variation_detail(experiment_key, user, default_variation).variation

    def variation_detail(self, experiment_key, user, default_variation='A'):
        """
        Decide the variation to expose to the user for experiment, and returns an object that
        describes the way the variation was decided.

        :param int experiment_key: the unique key of the experiment.
        :param hackle.model.User or hackle.model.HackleUser user: the user to participate in the experiment.
        :param str default_variation: the default variation of the experiment.

        :rtype: hackle.decision.ExperimentDecision
        :return: an object describing the result
        """
        sample = TimerSample.start()
        decision = self.__variation_detail(experiment_key, user, default_variation)
        DecisionMetrics.experiment(sample, experiment_key, decision)
        return decision

    def __variation_detail(self, experiment_key, user, default_variation):
        """
        :param int experiment_key:
        :param hackle.model.User or hackle.model.HackleUser user:
        :param str default_variation:

        :rtype: hackle.decision.ExperimentDecision
        """
        try:
            if not hackle_types.is_positive_int(experiment_key):
                Log.get().warning('Invalid experiment_key: {} (expected: positive integer)'.format(experiment_key))
                return ExperimentDecision(default_variation, DecisionReason.INVALID_INPUT)

            hackle_user = self._user_resolver.resolve_or_none(user)
            if hackle_user is None:
                return ExperimentDecision(default_variation, DecisionReason.INVALID_INPUT)

            return self._core.experiment(experiment_key, hackle_user, default_variation)
        except Exception as e:
            Log.get().error(
                'Unexpected error while deciding variation of experiment[{}]: {}'.format(experiment_key, str(e)))
            return ExperimentDecision(default_variation, DecisionReason.EXCEPTION)

    def is_feature_on(self, feature_key, user):
        """
        Decide whether the feature is turned on to the user.

        :param int feature_key: the unique key for the feature.
        :param hackle.model.User or hackle.model.HackleUser user: the user requesting the feature.

        :rtype: bool
        :return: True if the feature is on
                 False if the feature is off
        """
        return self.feature_flag_detail(feature_key, user).is_on

    def feature_flag_detail(self, feature_key, user):
        """
        Decide whether the feature is turned on to the user, and returns an object that
        describes the way the value was decided.

        :param int feature_key: the unique key of the feature.
        :param hackle.model.User or hackle.model.HackleUser user: the user requesting the feature.

        :rtype: hackle.decision.FeatureFlagDecision
        :return: an object describing the result
        """
        sample = TimerSample.start()
        decision = self.__feature_flag_detail(feature_key, user)
        DecisionMetrics.feature_flag(sample, feature_key, decision)
        return decision

    def __feature_flag_detail(self, feature_key, user):
        """
        :param int feature_key:
        :param hackle.model.User or hackle.model.HackleUser user:

        :rtype: hackle.decision.FeatureFlagDecision
        """
        try:
            if not hackle_types.is_positive_int(feature_key):
                Log.get().warning('Invalid feature_key: {} (expected: positive integer)'.format(feature_key))
                return FeatureFlagDecision(False, DecisionReason.INVALID_INPUT)

            hackle_user = self._user_resolver.resolve_or_none(user)
            if hackle_user is None:
                return FeatureFlagDecision(False, DecisionReason.INVALID_INPUT)

            return self._core.feature_flag(feature_key, hackle_user)
        except Exception as e:
            Log.get().error('Unexpected error while deciding feature flag[{}]: {}'.format(feature_key, str(e)))
            return FeatureFlagDecision(False, DecisionReason.EXCEPTION)

    def track(self, event, user):
        """
        Records the event that occurred by the user.

        :param hackle.model.Event or hackle.model.HackleEvent event: the event that occurred.
        :param hackle.model.User or hackle.model.HackleUser user: the user that occurred the event.
        """
        try:
            hackle_event = HackleEvent.from_event(event)
            if not hackle_event.is_valid:
                Log.get().warning('Invalid event for track: [{}]'.format(hackle_event.error_or_none))
                return

            hackle_user = self._user_resolver.resolve_or_none(user)
            if hackle_user is None:
                return

            self._core.track(hackle_event, hackle_user)
        except Exception as e:
            Log.get().error('Unexpected error while tracking event: {}'.format(str(e)))

    def remote_config(self, user):
        """
        Returns a instance of Hackle Remote Config.

        :param hackle.model.User or hackle.model.HackleUser user: the identifier of user.
        :rtype: HackleRemoteConfig
        """
        return HackleRemoteConfigImpl(user, self._core, self._user_resolver)

    def update_user_properties(self, operations, user):
        """
        Updates the user's properties.

        :param hackle.model.PropertyOperations operations: Property operations to update user properties.
        :param hackle.model.HackleUser user: the user whos properties will be updated.
        """
        try:
            if not isinstance(operations, PropertyOperations):
                Log.get().warning(
                    'Invalid user property update operations: {} (expected: PropertyOperations)'.format(operations))
                return

            event = operations.to_event()
            self.track(event, user)
        except Exception as e:
            Log.get().error('Unexpected exception while update user properties: {}'.format(str(e)))
