from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_evaluation import ExperimentEvaluation
from hackle.internal.evaluation.evaluator.remoteconfig.remote_config_evaluation import RemoteConfigEvaluation
from hackle.internal.event.user_event import UserEvent
from hackle.internal.model.properties_builder import PropertiesBuilder
from hackle.internal.time.clock import SYSTEM_CLOCK


class UserEventFactory(object):
    __ROOT_TYPE = "$targetingRootType"
    __ROOT_ID = "$targetingRootId"
    __CONFIG_ID_PROPERTY_KEY = "$parameterConfigurationId"

    __EXPERIMENT_VERSION_KEY = "$experiment_version"
    __EXECUTION_VERSION_KEY = "$execution_version"

    def __init__(self, clock=SYSTEM_CLOCK):
        self.__clock = clock

    def create(self, request, evaluation):
        """
        :param Evaluator.Request request:
        :param Evaluator.Evaluation evaluation:
        :rtype: list[UserEvent]
        """

        timestamp = self.__clock.current_millis()
        events = []

        root_event = self.__create(request, evaluation, timestamp, PropertiesBuilder())
        events.append(root_event)

        for target_evaluation in evaluation.target_evaluations:
            properties_builder = PropertiesBuilder()
            properties_builder.add(UserEventFactory.__ROOT_TYPE, request.key.type)
            properties_builder.add(UserEventFactory.__ROOT_ID, request.key.id)
            target_event = self.__create(request, target_evaluation, timestamp, properties_builder)
            events.append(target_event)

        return events

    # noinspection PyMethodMayBeStatic
    def __create(self, request, evaluation, timestamp, properties_builder):
        """

        :param Evaluator.Request request:
        :param Evaluator.Evaluation evaluation:
        :param int timestamp:
        :param PropertiesBuilder properties_builder:
        :return:
        """
        if isinstance(evaluation, ExperimentEvaluation):
            if evaluation.config is not None:
                properties_builder.add(UserEventFactory.__CONFIG_ID_PROPERTY_KEY, evaluation.config.id)
            properties_builder.add(UserEventFactory.__EXPERIMENT_VERSION_KEY, evaluation.experiment.version)
            properties_builder.add(UserEventFactory.__EXECUTION_VERSION_KEY, evaluation.experiment.execution_version)
            return UserEvent.exposure(request.user, evaluation, properties_builder.build(), timestamp)

        if isinstance(evaluation, RemoteConfigEvaluation):
            properties_builder.add_properties(evaluation.properties)
            return UserEvent.remote_config(request.user, evaluation, properties_builder.build(), timestamp)

        raise Exception('Unsupported Evaluation [{}]'.format(evaluation.__class__.__name__))
