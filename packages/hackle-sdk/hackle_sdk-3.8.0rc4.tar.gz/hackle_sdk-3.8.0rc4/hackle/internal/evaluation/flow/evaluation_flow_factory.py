from hackle.internal.evaluation.bucket.bucketer import Bucketer
from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.flow.flow_evaluator import *
from hackle.internal.evaluation.match.condition_matcher_factory import ConditionMatcherFactory
from hackle.internal.evaluation.match.target_matcher import TargetMatcher
from hackle.internal.evaluation.target.experiment_target_determiner import ExperimentTargetDeterminer
from hackle.internal.evaluation.target.experiment_target_rule_determiner import ExperimentTargetRuleDeterminer
from hackle.internal.evaluation.target.override_resolver import OverrideResolver
from hackle.internal.evaluation.target.remote_config_target_rule_determiner import RemoteConfigTargetRuleDeterminer, \
    RemoteConfigTargetRuleMatcher


class EvaluationFlowFactory(object):

    def __init__(self, evaluator):
        """
        :param Evaluator evaluator:
        """
        bucketer = Bucketer()
        target_matcher = TargetMatcher(ConditionMatcherFactory(evaluator))
        action_resolver = ActionResolver(bucketer)
        override_resolver = OverrideResolver(target_matcher, action_resolver)
        container_resolver = ContainerResolver(bucketer)

        self.__ab_test_flow = EvaluationFlow.of(
            OverrideEvaluator(override_resolver),
            IdentifierEvaluator(),
            ContainerEvaluator(container_resolver),
            ExperimentTargetEvaluator(ExperimentTargetDeterminer(target_matcher)),
            DraftEvaluator(),
            PausedEvaluator(),
            CompletedEvaluator(),
            TrafficAllocateEvaluator(action_resolver)
        )

        self.__feature_flag_flow = EvaluationFlow.of(
            DraftEvaluator(),
            PausedEvaluator(),
            CompletedEvaluator(),
            OverrideEvaluator(override_resolver),
            IdentifierEvaluator(),
            TargetRuleEvaluator(ExperimentTargetRuleDeterminer(target_matcher), action_resolver),
            DefaultRuleEvaluator(action_resolver)
        )

        self.__remote_config_parameter_target_rule_determiner = RemoteConfigTargetRuleDeterminer(
            RemoteConfigTargetRuleMatcher(target_matcher, bucketer))

    def get_evaluation_flow(self, experiment_type):
        if experiment_type == 'AB_TEST':
            return self.__ab_test_flow
        elif experiment_type == 'FEATURE_FLAG':
            return self.__feature_flag_flow
        else:
            raise Exception('Unsupported type [{}]'.format(experiment_type))

    @property
    def remote_config_parameter_target_rule_determiner(self):
        """
        :rtype: RemoteConfigTargetRuleDeterminer 
        """
        return self.__remote_config_parameter_target_rule_determiner
