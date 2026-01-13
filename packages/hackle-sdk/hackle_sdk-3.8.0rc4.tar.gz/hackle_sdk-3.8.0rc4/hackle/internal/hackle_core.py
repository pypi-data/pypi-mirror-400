from hackle.decision import ExperimentDecision, FeatureFlagDecision, DecisionReason, RemoteConfigDecision
from hackle.internal.evaluation.evaluator.delegating_evaluator import DelegatingEvaluator
from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_evaluator import ExperimentEvaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.evaluation.evaluator.remoteconfig.remote_config_evaluator import RemoteConfigEvaluator
from hackle.internal.evaluation.evaluator.remoteconfig.remote_config_request import RemoteConfigRequest
from hackle.internal.evaluation.flow.evaluation_flow_factory import EvaluationFlowFactory
from hackle.internal.event.event_processor import EventProcessor
from hackle.internal.event.user_event import UserEvent
from hackle.internal.event.user_event_factory import UserEventFactory
from hackle.internal.model.entities import EventType
from hackle.internal.time.clock import SYSTEM_CLOCK
from hackle.internal.user.internal_hackle_user import InternalHackleUser
from hackle.internal.workspace.workspace_fetcher import WorkspaceFetcher
from hackle.model import HackleEvent


class HackleCore(object):

    def __init__(self,
                 experiment_evaluator,
                 remote_config_evaluator,
                 workspace_fetcher,
                 event_factory,
                 event_processor):
        """
        :param ExperimentEvaluator experiment_evaluator:
        :param RemoteConfigEvaluator remote_config_evaluator:
        :param WorkspaceFetcher workspace_fetcher:
        :param UserEventFactory event_factory:
        :param EventProcessor event_processor:
        """
        self.__experiment_evaluator = experiment_evaluator
        self.__remote_config_evaluator = remote_config_evaluator
        self.__workspace_fetcher = workspace_fetcher
        self.__event_factory = event_factory
        self.__event_processor = event_processor
        self.__clock = SYSTEM_CLOCK

    @staticmethod
    def create(workspace_fetcher, event_processor):
        """
        :param WorkspaceFetcher workspace_fetcher:
        :param EventProcessor event_processor:
        :rtype: HackleCore
        """
        delegating_evaluator = DelegatingEvaluator()
        evaluation_flow_factory = EvaluationFlowFactory(delegating_evaluator)

        experiment_evaluator = ExperimentEvaluator(evaluation_flow_factory)
        remote_config_evaluator = RemoteConfigEvaluator(
            evaluation_flow_factory.remote_config_parameter_target_rule_determiner)

        delegating_evaluator.add(experiment_evaluator)
        delegating_evaluator.add(remote_config_evaluator)

        return HackleCore(
            experiment_evaluator,
            remote_config_evaluator,
            workspace_fetcher,
            UserEventFactory(),
            event_processor
        )

    def close(self):
        self.__workspace_fetcher.stop()
        self.__event_processor.stop()

    def experiment(self, experiment_key, user, default_variation_key):
        """
        :param int experiment_key:
        :param InternalHackleUser user:
        :param str default_variation_key:

        :rtype: ExperimentDecision
        """
        workspace = self.__workspace_fetcher.fetch()
        if workspace is None:
            return ExperimentDecision(default_variation_key, DecisionReason.SDK_NOK_READY)

        experiment = workspace.get_experiment_or_none(experiment_key)
        if experiment is None:
            return ExperimentDecision(default_variation_key, DecisionReason.EXPERIMENT_NOT_FOUND)

        request = ExperimentRequest.of(workspace, user, experiment, default_variation_key)
        evaluation = self.__experiment_evaluator.evaluate(request, Evaluator.context())

        events = self.__event_factory.create(request, evaluation)
        for event in events:
            self.__event_processor.process(event)

        return ExperimentDecision(evaluation.variation_key, evaluation.reason, evaluation.config)

    def feature_flag(self, feature_key, user):
        """
        :param int feature_key:
        :param InternalHackleUser user:

        :rtype: FeatureFlagDecision
        """
        workspace = self.__workspace_fetcher.fetch()
        if workspace is None:
            return FeatureFlagDecision(False, DecisionReason.SDK_NOK_READY)

        feature_flag = workspace.get_feature_flag_or_none(feature_key)
        if feature_flag is None:
            return FeatureFlagDecision(False, DecisionReason.FEATURE_FLAG_NOT_FOUND)

        request = ExperimentRequest.of(workspace, user, feature_flag, 'A')
        evaluation = self.__experiment_evaluator.evaluate(request, Evaluator.context())

        events = self.__event_factory.create(request, evaluation)
        for event in events:
            self.__event_processor.process(event)

        if evaluation.variation_key == 'A':
            return FeatureFlagDecision(False, evaluation.reason, evaluation.config)
        else:
            return FeatureFlagDecision(True, evaluation.reason, evaluation.config)

    def track(self, event, user):
        """
        :param HackleEvent event:
        :param InternalHackleUser user:
        """
        event_type = self.__event_type(event)
        self.__event_processor.process(UserEvent.track(user, event_type, event, self.__clock.current_millis()))
        return

    def __event_type(self, event):
        """
        :param hackle.model.HackleEvent event:

        :rtype: hackle.internal.model.entities.EventType
        """
        workspace = self.__workspace_fetcher.fetch()

        if workspace is None:
            return EventType(0, event.key)

        event_type = workspace.get_event_type_or_none(event.key)

        if event_type is None:
            return EventType(0, event.key)

        return event_type

    def remote_config(self, key, user, required_type, default_value):
        """
        :param str key:
        :param InternalHackleUser user:
        :param str required_type:
        :param object or None default_value:

        :rtype: RemoteConfigDecision
        """
        workspace = self.__workspace_fetcher.fetch()
        if workspace is None:
            return RemoteConfigDecision(default_value, DecisionReason.SDK_NOK_READY)

        parameter = workspace.get_remote_config_parameter_or_none(key)
        if parameter is None:
            return RemoteConfigDecision(default_value, DecisionReason.REMOTE_CONFIG_PARAMETER_NOT_FOUND)

        request = RemoteConfigRequest(workspace, user, parameter, required_type, default_value)
        evaluation = self.__remote_config_evaluator.evaluate(request, Evaluator.context())

        events = self.__event_factory.create(request, evaluation)
        for event in events:
            self.__event_processor.process(event)

        return RemoteConfigDecision(evaluation.value, evaluation.reason)
