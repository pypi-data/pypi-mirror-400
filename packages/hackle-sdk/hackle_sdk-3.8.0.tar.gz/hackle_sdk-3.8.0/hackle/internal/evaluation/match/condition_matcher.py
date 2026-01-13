import abc

from six import add_metaclass

from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.model.entities import TargetCondition


@add_metaclass(abc.ABCMeta)
class ConditionMatcher(object):

    @abc.abstractmethod
    def matches(self, request, context, condition):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:
        :param TargetCondition condition:

        :rtype: bool
        """
        pass
