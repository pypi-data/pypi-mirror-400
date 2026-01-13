from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.match.condition_matcher import ConditionMatcher
from hackle.internal.evaluation.match.experiment_condition_matcher import ExperimentConditionMatcher, \
    AbTestConditionMatcher, \
    FeatureFlagConditionMatcher
from hackle.internal.evaluation.match.segment_condition_matcher import SegmentConditionMatcher, SegmentMatcher
from hackle.internal.evaluation.match.user_condition_matcher import UserConditionMatcher, UserValueResolver
from hackle.internal.evaluation.match.value_operator_matcher import ValueOperatorMatcher, ValueOperatorMatcherFactory


class ConditionMatcherFactory(object):

    def __init__(self, evaluator):
        """
        :param Evaluator evaluator:
        """
        value_operator_matcher = ValueOperatorMatcher(ValueOperatorMatcherFactory())
        self.__user_condition_matcher = UserConditionMatcher(UserValueResolver(), value_operator_matcher)
        self.__segment_condition_matcher = SegmentConditionMatcher(SegmentMatcher(self.__user_condition_matcher))
        self.__experiment_condition_matcher = ExperimentConditionMatcher(
            AbTestConditionMatcher(evaluator, value_operator_matcher),
            FeatureFlagConditionMatcher(evaluator, value_operator_matcher)
        )

    def get_condition_matcher_or_none(self, target_key_type):
        """
        :param str target_key_type:

        :rtype: ConditionMatcher or None
        """
        if target_key_type == 'USER_ID':
            return self.__user_condition_matcher
        elif target_key_type == 'USER_PROPERTY':
            return self.__user_condition_matcher
        elif target_key_type == 'HACKLE_PROPERTY':
            return self.__user_condition_matcher
        elif target_key_type == 'SEGMENT':
            return self.__segment_condition_matcher
        elif target_key_type == 'AB_TEST':
            return self.__experiment_condition_matcher
        elif target_key_type == 'FEATURE_FLAG':
            return self.__experiment_condition_matcher
        else:
            return None
