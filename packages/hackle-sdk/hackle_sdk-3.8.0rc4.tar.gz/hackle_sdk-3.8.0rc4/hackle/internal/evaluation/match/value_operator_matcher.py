from hackle.internal.evaluation.match.operator_matcher import *
from hackle.internal.evaluation.match.value_matcher import *
from hackle.internal.logger.log import Log


class ValueOperatorMatcher(object):

    def __init__(self, factory):
        self.factory = factory

    def matches(self, user_value, match):
        value_matcher = self.factory.get_value_matcher_or_none(match.value_type)
        if not value_matcher:
            Log.get().debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(match.value_type))
            return False

        operator_matcher = self.factory.get_operator_matcher_or_none(match.operator)
        if not operator_matcher:
            Log.get().debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(match.operator))
            return False

        is_matched = self.__matches(user_value, match, value_matcher, operator_matcher)
        return self.__type_matches(match.type, is_matched)

    def __matches(self, user_value, match, value_matcher, operator_matcher):
        if isinstance(user_value, list):
            return self.__array_matches(user_value, match, value_matcher, operator_matcher)
        else:
            return self.__single_matches(user_value, match, value_matcher, operator_matcher)

    # noinspection PyMethodMayBeStatic
    def __single_matches(self, user_value, match, value_matcher, operator_matcher):
        for match_value in match.values:
            if value_matcher.matches(operator_matcher, user_value, match_value):
                return True
        return False

    def __array_matches(self, user_values, match, value_matcher, operator_matcher):
        for user_value in user_values:
            if self.__single_matches(user_value, match, value_matcher, operator_matcher):
                return True
        return False

    # noinspection PyMethodMayBeStatic
    def __type_matches(self, match_type, is_matched):
        if match_type == 'MATCH':
            return is_matched
        elif match_type == 'NOT_MATCH':
            return not is_matched
        else:
            Log.get().debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(match_type))
            return False


class ValueOperatorMatcherFactory(object):

    def __init__(self):
        self._value_matchers = {
            'STRING': StringValueMatcher(),
            'NUMBER': NumberValueMatcher(),
            'BOOLEAN': BoolValueMatcher(),
            'VERSION': VersionValueMatcher(),
            'NULL': NoneValueMatcher(),
            'UNKNOWN': NoneValueMatcher()
        }
        self._operator_matchers = {
            'IN': InMatcher(),
            'CONTAINS': ContainsMatcher(),
            'STARTS_WITH': StartsWithMatcher(),
            'ENDS_WITH': EndsWithMatcher(),
            'GT': GreaterThanMatcher(),
            'GTE': GreaterThanOrEqualToMatcher(),
            'LT': LessThanMatcher(),
            'LTE': LessThanOrEqualToMatcher()
        }

    def get_value_matcher_or_none(self, value_type):
        return self._value_matchers.get(value_type)

    def get_operator_matcher_or_none(self, operator):
        return self._operator_matchers.get(operator)
