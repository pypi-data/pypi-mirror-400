from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.evaluation.match.target_matcher import TargetMatcher


class ExperimentTargetDeterminer(object):
    def __init__(self, target_matcher):
        """
        :param TargetMatcher target_matcher:
        """
        self.__target_matcher = target_matcher

    def is_user_in_experiment_target(self, request, context):
        """
        :param ExperimentRequest request:
        :param Evaluator.Context context:
        :rtype: bool
        """
        if not request.experiment.target_audiences:
            return True

        for target in request.experiment.target_audiences:
            if self.__target_matcher.matches(request, context, target):
                return True

        return False
