import abc

from six import add_metaclass

from hackle.decision import DecisionReason
from hackle.internal.evaluation.action.action_resolver import ActionResolver
from hackle.internal.evaluation.container.container_resolver import ContainerResolver
from hackle.internal.evaluation.evaluator.experiment.experiment_evaluation import ExperimentEvaluation
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.evaluation.flow.evaluation_flow import EvaluationFlow
from hackle.internal.evaluation.target.experiment_target_determiner import ExperimentTargetDeterminer
from hackle.internal.evaluation.target.experiment_target_rule_determiner import ExperimentTargetRuleDeterminer
from hackle.internal.evaluation.target.override_resolver import OverrideResolver


@add_metaclass(abc.ABCMeta)
class FlowEvaluator(object):

    @abc.abstractmethod
    def evaluate(self, request, context, next_flow):
        """
        :param ExperimentRequest request:
        :param Evaluator.Context context:
        :param EvaluationFlow next_flow:

        :rtype: ExperimentEvaluation
        """
        pass


class OverrideEvaluator(FlowEvaluator):

    def __init__(self, override_resolver):
        """
        :param OverrideResolver override_resolver:
        """
        self.__override_resolver = override_resolver

    def evaluate(self, request, context, next_flow):
        overridden_variation = self.__override_resolver.resolve_or_none(request, context)

        if overridden_variation is not None:
            if request.experiment.type == 'AB_TEST':
                return ExperimentEvaluation.of(request, context, overridden_variation, DecisionReason.OVERRIDDEN)
            elif request.experiment.type == 'FEATURE_FLAG':
                return ExperimentEvaluation.of(request, context, overridden_variation,
                                               DecisionReason.INDIVIDUAL_TARGET_MATCH)
            else:
                raise Exception('experiment type [{}]'.format(request.experiment.type))
        else:
            return next_flow.evaluate(request, context)


class DraftEvaluator(FlowEvaluator):
    def evaluate(self, request, context, next_flow):
        if request.experiment.status == 'DRAFT':
            return ExperimentEvaluation.of_default(request, context, DecisionReason.EXPERIMENT_DRAFT)
        else:
            return next_flow.evaluate(request, context)


class PausedEvaluator(FlowEvaluator):
    def evaluate(self, request, context, next_flow):
        if request.experiment.status == 'PAUSED':
            if request.experiment.type == 'AB_TEST':
                return ExperimentEvaluation.of_default(request, context, DecisionReason.EXPERIMENT_PAUSED)
            elif request.experiment.type == 'FEATURE_FLAG':
                return ExperimentEvaluation.of_default(request, context, DecisionReason.FEATURE_FLAG_INACTIVE)
            else:
                raise Exception('experiment type [{}]'.format(request.experiment.type))
        else:
            return next_flow.evaluate(request, context)


class CompletedEvaluator(FlowEvaluator):
    def evaluate(self, request, context, next_flow):
        if request.experiment.status == 'COMPLETED':
            winner_variation = request.experiment.winner_variation
            if winner_variation is None:
                raise Exception('Winner variation[{}]'.format(request.experiment.id))
            return ExperimentEvaluation.of(request, context, winner_variation, DecisionReason.EXPERIMENT_COMPLETED)
        else:
            return next_flow.evaluate(request, context)


class ExperimentTargetEvaluator(FlowEvaluator):

    def __init__(self, experiment_target_determiner):
        """
        :param ExperimentTargetDeterminer experiment_target_determiner:
        """
        self.__experiment_target_determiner = experiment_target_determiner

    def evaluate(self, request, context, next_flow):
        if request.experiment.type != 'AB_TEST':
            raise Exception('experiment type must be AB_TEST [{}]'.format(request.experiment.id))

        is_user_in_experiment_target = self.__experiment_target_determiner.is_user_in_experiment_target(request,
                                                                                                        context)
        if is_user_in_experiment_target:
            return next_flow.evaluate(request, context)
        else:
            return ExperimentEvaluation.of_default(request, context, DecisionReason.NOT_IN_EXPERIMENT_TARGET)


class TrafficAllocateEvaluator(FlowEvaluator):

    def __init__(self, action_resolver):
        """
        :param ActionResolver action_resolver:
        """
        self.__action_resolver = action_resolver

    def evaluate(self, request, context, next_flow):
        if request.experiment.status != 'RUNNING':
            raise Exception('experiment status must be RUNNING [{}]'.format(request.experiment.id))

        if request.experiment.type != 'AB_TEST':
            raise Exception('experiment type must be AB_TEST [{}]'.format(request.experiment.id))

        default_rule = request.experiment.default_rule
        variation = self.__action_resolver.resolve_or_none(request, default_rule)
        if not variation:
            return ExperimentEvaluation.of_default(request, context, DecisionReason.TRAFFIC_NOT_ALLOCATED)

        if variation.is_dropped:
            return ExperimentEvaluation.of_default(request, context, DecisionReason.VARIATION_DROPPED)

        return ExperimentEvaluation.of(request, context, variation, DecisionReason.TRAFFIC_ALLOCATED)


class TargetRuleEvaluator(FlowEvaluator):

    def __init__(self, target_rule_determiner, action_resolver):
        """
        :param ExperimentTargetRuleDeterminer target_rule_determiner:
        :param ActionResolver action_resolver:
        """
        self.__target_rule_determiner = target_rule_determiner
        self.__action_resolver = action_resolver

    def evaluate(self, request, context, next_flow):
        if request.experiment.status != 'RUNNING':
            raise Exception('experiment status must be RUNNING [{}]'.format(request.experiment.id))

        if request.experiment.type != 'FEATURE_FLAG':
            raise Exception('experiment type must be FEATURE_FLAG [{}]'.format(request.experiment.id))

        if request.user.identifiers.get(request.experiment.identifier_type) is None:
            return next_flow.evaluate(request, context)

        target_rule = self.__target_rule_determiner.determine_target_rule_or_none(request, context)
        if target_rule is None:
            return next_flow.evaluate(request, context)

        variation = self.__action_resolver.resolve_or_none(request, target_rule.action)
        if not variation:
            raise Exception('FeatureFlag must decide the variation [{}]'.format(request.experiment.id))

        return ExperimentEvaluation.of(request, context, variation, DecisionReason.TARGET_RULE_MATCH)


class DefaultRuleEvaluator(FlowEvaluator):

    def __init__(self, action_resolver):
        """
        :param ActionResolver action_resolver:
        """
        self.__action_resolver = action_resolver

    def evaluate(self, request, context, next_flow):
        if request.experiment.status != 'RUNNING':
            raise Exception('experiment status must be RUNNING [{}]'.format(request.experiment.id))

        if request.experiment.type != 'FEATURE_FLAG':
            raise Exception('experiment type must be FEATURE_FLAG [{}]'.format(request.experiment.id))

        if request.user.identifiers.get(request.experiment.identifier_type) is None:
            return ExperimentEvaluation.of_default(request, context, DecisionReason.DEFAULT_RULE)

        variation = self.__action_resolver.resolve_or_none(request, request.experiment.default_rule)
        if not variation:
            raise Exception('FeatureFlag must decide the variation [{}]'.format(request.experiment.id))

        return ExperimentEvaluation.of(request, context, variation, DecisionReason.DEFAULT_RULE)


class ContainerEvaluator(FlowEvaluator):

    def __init__(self, container_resolver):
        """
        :param ContainerResolver container_resolver:
        """
        self.__container_resolver = container_resolver

    def evaluate(self, request, context, next_flow):
        experiment = request.experiment
        container_id = experiment.container_id
        if container_id is None:
            return next_flow.evaluate(request, context)

        container = request.workspace.get_container_or_none(container_id)
        if container is None:
            raise Exception('Container[{}]'.format(container_id))

        if self.__container_resolver.is_user_in_container_group(request, container):
            return next_flow.evaluate(request, context)
        else:
            return ExperimentEvaluation.of_default(request, context, DecisionReason.NOT_IN_MUTUAL_EXCLUSION_EXPERIMENT)


class IdentifierEvaluator(FlowEvaluator):
    def evaluate(self, request, context, next_flow):
        if request.user.identifiers.get(request.experiment.identifier_type) is not None:
            return next_flow.evaluate(request, context)
        else:
            return ExperimentEvaluation.of_default(request, context, DecisionReason.IDENTIFIER_NOT_FOUND)
