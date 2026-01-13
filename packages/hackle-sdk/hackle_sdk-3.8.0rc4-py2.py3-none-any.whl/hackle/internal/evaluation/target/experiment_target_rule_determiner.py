from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.evaluation.match.target_matcher import TargetMatcher
from hackle.internal.model.entities import TargetRule


class ExperimentTargetRuleDeterminer(object):
    def __init__(self, target_matcher):
        """
        :param TargetMatcher target_matcher: 
        """
        self.__target_matcher = target_matcher

    def determine_target_rule_or_none(self, request, context):
        """
        :param ExperimentRequest request: 
        :param Evaluator.Context context: 
        :rtype: TargetRule 
        """
        for target_rule in request.experiment.target_rules:
            if self.__target_matcher.matches(request, context, target_rule.target):
                return target_rule

        return None
