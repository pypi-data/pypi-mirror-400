import abc

from six import add_metaclass, string_types

from hackle.internal.evaluation.match.semantic_version import SemanticVersion
from hackle.internal.type import hackle_types


@add_metaclass(abc.ABCMeta)
class ValueMatcher(object):

    @abc.abstractmethod
    def matches(self, operator_matcher, user_value, match_value):
        pass


class StringValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        str_user_value = self.__string_or_none(user_value)
        str_match_value = self.__string_or_none(match_value)
        if str_user_value is not None and str_match_value is not None:
            return operator_matcher.string_matches(str_user_value, str_match_value)
        else:
            return False

    @staticmethod
    def __string_or_none(value):
        if isinstance(value, string_types):
            return value
        elif hackle_types.is_finite_number(value):
            return str(value)
        else:
            return None


class NumberValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        number_user_value = self.__number_or_none(user_value)
        number_match_value = self.__number_or_none(match_value)
        if number_user_value is not None and number_match_value is not None:
            return operator_matcher.number_matches(number_user_value, number_match_value)
        else:
            return False

    @staticmethod
    def __number_or_none(value):
        if hackle_types.is_finite_number(value):
            return value
        elif isinstance(value, string_types):
            try:
                number = float(value)
                if hackle_types.is_finite_number(number):
                    return number
                else:
                    return None
            except ValueError:
                return None
        else:
            return None


class BoolValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        if isinstance(user_value, bool) and isinstance(match_value, bool):
            return operator_matcher.bool_matches(user_value, match_value)
        else:
            return False


class VersionValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        user_version = SemanticVersion.parse_or_none(user_value)
        match_version = SemanticVersion.parse_or_none(match_value)
        if user_version is not None and match_version is not None:
            return operator_matcher.version_matches(user_version, match_version)
        else:
            return False


class NoneValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        return False
