from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.model.entities import RemoteConfigParameter
from hackle.internal.user.internal_hackle_user import InternalHackleUser
from hackle.internal.workspace.workspace import Workspace


class RemoteConfigRequest(Evaluator.Request):
    def __init__(self, workspace, user, parameter, required_type, default_value):
        """
        :param Workspace workspace:
        :param InternalHackleUser user:
        :param RemoteConfigParameter parameter:
        :param str required_type:
        :param object default_value:
        """
        super(RemoteConfigRequest, self).__init__(Evaluator.Key('REMOTE_CONFIG', parameter.id), workspace, user)
        self.__parameter = parameter
        self.__required_type = required_type
        self.__default_value = default_value

    @property
    def parameter(self):
        """
        :rtype: RemoteConfigParameter
        """
        return self.__parameter

    @property
    def required_type(self):
        """
        :rtype: str
        """
        return self.__required_type

    @property
    def default_value(self):
        """
        :rtype: object
        """
        return self.__default_value

    def __str__(self):
        return 'EvaluatorRequest(type=REMOTE_CONFIG, key={})'.format(self.__parameter.key)

    def __repr__(self):
        return self.__str__()
