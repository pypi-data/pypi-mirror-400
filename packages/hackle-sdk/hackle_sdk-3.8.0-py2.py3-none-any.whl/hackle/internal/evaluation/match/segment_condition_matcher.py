from hackle.internal.evaluation.match.condition_matcher import ConditionMatcher
from hackle.internal.evaluation.match.user_condition_matcher import UserConditionMatcher
from hackle.internal.logger.log import Log
from hackle.internal.model.entities import Segment, Target
from hackle.internal.type import hackle_types


class SegmentConditionMatcher(ConditionMatcher):

    def __init__(self, segment_matcher):
        """
        :param SegmentMatcher segment_matcher:
        """
        self.__segment_matcher = segment_matcher

    def matches(self, request, context, condition):
        if condition.key.type != 'SEGMENT':
            raise Exception('Unsupported target.key.type [{}]'.format(condition.key.type))

        for value in condition.match.values:
            if self.__matches(request, context, value):
                return self.__match_type(condition.match.type, True)

        return self.__match_type(condition.match.type, False)

    def __matches(self, request, context, value):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:
        :param object value:
        :rtype: bool
        """
        segment_key = value
        if not hackle_types.is_string(segment_key):
            raise Exception('SegmentKey[{}]'.format(segment_key))
        segment = request.workspace.get_segment_or_none(segment_key)
        if segment is None:
            raise Exception('Segment[{}]'.format(segment_key))

        return self.__segment_matcher.matches(request, context, segment)

    # noinspection PyMethodMayBeStatic
    def __match_type(self, match_type, is_matched):
        """
        :param str match_type:
        :param bool is_matched:

        :rtype: bool
        """
        if match_type == 'MATCH':
            return is_matched
        elif match_type == 'NOT_MATCH':
            return not is_matched
        else:
            Log.get().debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(match_type))
            return False


class SegmentMatcher(object):
    def __init__(self, user_condition_matcher):
        """
        :param UserConditionMatcher user_condition_matcher:
        """
        self.__user_condition_matcher = user_condition_matcher

    def matches(self, request, context, segment):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:
        :param Segment segment:

        :rtype: bool
        """
        for target in segment.targets:
            if self.__matches(request, context, target):
                return True
        return False

    def __matches(self, request, context, target):
        """
        :param Evaluator.Request request:
        :param Evaluator.Context context:
        :param Target target:

        :rtype: bool
        """
        for condition in target.conditions:
            if not self.__user_condition_matcher.matches(request, context, condition):
                return False
        return True
