from .decision import RemoteConfigDecision, DecisionReason
from .internal.hackle_core import HackleCore
from .internal.metrics.timer import TimerSample
from .internal.monitoring.metrics.decision_metrics import DecisionMetrics
from .internal.type import hackle_types
from .internal.user.hackle_user_resolver import HackleUserResolver
from .model import HackleRemoteConfig, HackleUser


class HackleRemoteConfigImpl(HackleRemoteConfig):
    def __init__(self, user, core, hackle_user_resolver):
        """
        :param HackleUser user:
        :param HackleCore core:
        :param HackleUserResolver hackle_user_resolver:
        """
        self.__user = user
        self.__core = core
        self.__hackle_user_resolver = hackle_user_resolver

    def get(self, key, default=None):
        if hackle_types.is_string(default):
            return self.__get(key, 'STRING', default).value
        elif hackle_types.is_number(default):
            return self.__get(key, 'NUMBER', default).value
        elif hackle_types.is_bool(default):
            return self.__get(key, 'BOOLEAN', default).value
        elif default is None:
            return self.__get(key, 'NULL', default).value
        else:
            return self.__get(key, 'UNKNOWN', default).value

    def __get(self, key, required_type, default):
        """
        :param str key:
        :param str required_type:
        :param object default:

        :rtype: hackle.decision.RemoteConfigDecision
        """
        sample = TimerSample.start()
        decision = self.__decision(key, required_type, default)
        DecisionMetrics.remote_config(sample, key, decision)
        return decision

    def __decision(self, key, required_type, default):
        """
        :param str key:`
        :param str required_type:
        :param object default:

        :rtype: hackle.decision.RemoteConfigDecision
        """
        hackle_user = self.__hackle_user_resolver.resolve_or_none(self.__user)

        if hackle_user is None:
            return RemoteConfigDecision(default, DecisionReason.INVALID_INPUT)

        if key is None:
            return RemoteConfigDecision(default, DecisionReason.INVALID_INPUT)

        return self.__core.remote_config(key, hackle_user, required_type, default)
