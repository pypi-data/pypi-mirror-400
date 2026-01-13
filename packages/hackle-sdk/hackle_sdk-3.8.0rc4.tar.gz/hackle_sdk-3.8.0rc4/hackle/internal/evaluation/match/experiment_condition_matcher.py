import abc

from six import add_metaclass

from hackle.decision import DecisionReason
from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_evaluation import ExperimentEvaluation
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.evaluation.match.condition_matcher import ConditionMatcher
from hackle.internal.evaluation.match.value_operator_matcher import ValueOperatorMatcher
from hackle.internal.model.entities import TargetCondition, Experiment
from hackle.internal.type import hackle_types


class ExperimentConditionMatcher(ConditionMatcher):

    def __init__(self, ab_test_matcher, feature_flag_matcher):
        """
        :param AbTestConditionMatcher ab_test_matcher:
        :param FeatureFlagConditionMatcher feature_flag_matcher:
        """
        self.__ab_test_matcher = ab_test_matcher
        self.__feature_flag_matcher = feature_flag_matcher

    def matches(self, request, context, condition):
        if condition.key.type == 'AB_TEST':
            return self.__ab_test_matcher.matches(request, context, condition)
        elif condition.key.type == 'FEATURE_FLAG':
            return self.__feature_flag_matcher.matches(request, context, condition)
        else:
            raise Exception('Unsupported TargetKeyType[{}]'.format(condition.key.type))


@add_metaclass(abc.ABCMeta)
class ExperimentMatcher(object):
    def __init__(self, evaluator):
        """
        :param Evaluator evaluator:
        """
        self.__evaluator = evaluator

    def matches(self, request, context, condition):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:
        :param TargetCondition condition:

        :rtype: bool
        """
        key = hackle_types.as_int_or_none(condition.key.name)
        if key is None:
            raise Exception('Invalid key [{}, {}]'.format(condition.key.type, condition.key.name))
        experiment = self._experiment_or_none(request, key)
        if experiment is None:
            return False

        evaluation = context.get_evaluation_or_none(experiment)
        if evaluation is None:
            evaluation = self.__evaluate(request, context, experiment)
        return self._evaluation_matches(evaluation, condition)

    def __evaluate(self, request, context, experiment):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:
        :param Experiment experiment:

        :rtype: ExperimentEvaluation
        """
        experiment_request = ExperimentRequest.from_request(request, experiment)
        evaluation = self.__evaluator.evaluate(experiment_request, context)
        if not isinstance(evaluation, ExperimentEvaluation):
            raise Exception('Unexpected evaluation: {} (expected: ExperimentEvaluation)'.format(evaluation))
        experiment_evaluation = self._resolve(request, evaluation)
        context.add_evaluation(experiment_evaluation)
        return experiment_evaluation

    @abc.abstractmethod
    def _experiment_or_none(self, request, key):
        """
        :param Evaluator.Request request:
        :param int key:

        :rtype: Experiment or None
        """
        pass

    @abc.abstractmethod
    def _resolve(self, request, evaluation):
        """
        :param Evaluator.Request request:
        :param ExperimentEvaluation evaluation:

        :rtype: ExperimentEvaluation
        """
        pass

    @abc.abstractmethod
    def _evaluation_matches(self, evaluation, condition):
        """
        :param ExperimentEvaluation evaluation:
        :param TargetCondition condition:

        :rtype: bool
        """
        pass


class AbTestConditionMatcher(ExperimentMatcher):
    __AB_TEST_MATCHED_REASONS = [
        DecisionReason.OVERRIDDEN,
        DecisionReason.TRAFFIC_ALLOCATED,
        DecisionReason.TRAFFIC_ALLOCATED_BY_TARGETING,
        DecisionReason.EXPERIMENT_COMPLETED,
    ]

    def __init__(self, evaluator, value_operator_matcher):
        """
        :param Evaluator evaluator:
        :param ValueOperatorMatcher value_operator_matcher:
        """
        super(AbTestConditionMatcher, self).__init__(evaluator)
        self.__value_operator_matcher = value_operator_matcher

    def _experiment_or_none(self, request, key):
        return request.workspace.get_experiment_or_none(key)

    def _resolve(self, request, evaluation):
        if isinstance(request, ExperimentRequest) and evaluation.reason == DecisionReason.TRAFFIC_ALLOCATED:
            return evaluation.copy_with(DecisionReason.TRAFFIC_ALLOCATED_BY_TARGETING)
        return evaluation

    def _evaluation_matches(self, evaluation, condition):
        if not evaluation.reason in self.__AB_TEST_MATCHED_REASONS:
            return False
        return self.__value_operator_matcher.matches(evaluation.variation_key, condition.match)


class FeatureFlagConditionMatcher(ExperimentMatcher):
    def __init__(self, evaluator, value_operator_matcher):
        """
        :param Evaluator evaluator:
        :param ValueOperatorMatcher value_operator_matcher:
        """
        super(FeatureFlagConditionMatcher, self).__init__(evaluator)
        self.__value_operator_matcher = value_operator_matcher

    def _experiment_or_none(self, request, key):
        return request.workspace.get_feature_flag_or_none(key)

    def _resolve(self, request, evaluation):
        return evaluation

    def _evaluation_matches(self, evaluation, condition):
        on = evaluation.variation_key != 'A'
        return self.__value_operator_matcher.matches(on, condition.match)
