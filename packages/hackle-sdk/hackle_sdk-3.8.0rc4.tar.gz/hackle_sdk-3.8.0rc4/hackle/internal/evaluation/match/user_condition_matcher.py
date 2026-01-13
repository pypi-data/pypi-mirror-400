from hackle.internal.evaluation.match.condition_matcher import ConditionMatcher
from hackle.internal.evaluation.match.value_operator_matcher import ValueOperatorMatcher
from hackle.internal.logger.log import Log
from hackle.internal.model.entities import TargetKey
from hackle.internal.user.internal_hackle_user import InternalHackleUser


class UserConditionMatcher(ConditionMatcher):

    def __init__(self, user_value_resolver, value_operator_matcher):
        """
        :param UserValueResolver user_value_resolver:
        :param ValueOperatorMatcher value_operator_matcher:
        """
        self.__user_value_resolver = user_value_resolver
        self.__value_operator_matcher = value_operator_matcher

    def matches(self, request, context, condition):
        user_value = self.__user_value_resolver.resolve_or_none(request.user, condition.key)
        if user_value is None:
            return False
        return self.__value_operator_matcher.matches(user_value, condition.match)


class UserValueResolver(object):

    # noinspection PyMethodMayBeStatic
    def resolve_or_none(self, user, target_key):
        """
        :param InternalHackleUser user:
        :param TargetKey target_key:

        :rtype: object or None
        """
        if target_key.type == 'USER_ID':
            return user.identifiers.get(target_key.name)
        elif target_key.type == 'USER_PROPERTY':
            return user.properties.get(target_key.name)
        elif target_key.type == 'HACKLE_PROPERTY':
            return None
        elif target_key.type == 'SEGMENT':
            raise Exception('Unsupported target_key.type [SEGMENT]')
        else:
            Log.get().debug('Unsupported type [{}]. Please use the latest version of sdk.'.format(target_key))
            return None
