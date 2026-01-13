from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.match.condition_matcher_factory import ConditionMatcherFactory
from hackle.internal.logger.log import Log
from hackle.internal.model.entities import Target, TargetCondition


class TargetMatcher(object):

    def __init__(self, condition_matcher_factory):
        """
        :param ConditionMatcherFactory condition_matcher_factory:
        """
        self.condition_matcher_factory = condition_matcher_factory

    def matches(self, request, context, target):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:
        :param Target target:

        :rtype: bool
        """
        for condition in target.conditions:
            if not self.__matches(request, context, condition):
                return False
        return True

    def __matches(self, request, context, condition):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:
        :param TargetCondition condition:

        :rtype: bool
        """
        condition_matcher = self.condition_matcher_factory.get_condition_matcher_or_none(condition.key.type)
        if condition_matcher is None:
            Log.get().debug('Unsupported type [{}]. Please use the latest version of sdk.'.format(condition.key.type))
            return False
        return condition_matcher.matches(request, context, condition)
