from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.remoteconfig.remote_config_request import RemoteConfigRequest
from hackle.internal.model.properties_builder import PropertiesBuilder


class RemoteConfigEvaluation(Evaluator.Evaluation):
    def __init__(self, reason, target_evaluations, parameter, value_id, value, properties):
        """

        :param str reason:
        :param list[Evaluator.Evaluation] target_evaluations:
        :param RemoteConfigParameter parameter:
        :param int or None value_id:
        :param object or None value:
        :param dict[str, object] properties:
        """
        super(RemoteConfigEvaluation, self).__init__(reason, target_evaluations)
        self.__parameter = parameter
        self.__value_id = value_id
        self.__value = value
        self.__properties = properties

    @staticmethod
    def of(request, context, value_id, value, reason, properties_builder):
        """
        :param RemoteConfigRequest request:
        :param Evaluator.Context context:
        :param int or None value_id:
        :param object value:
        :param str reason:
        :param PropertiesBuilder properties_builder:

        :rtype: RemoteConfigEvaluation
        """
        properties_builder.add("returnValue", value)
        return RemoteConfigEvaluation(
            reason,
            context.target_evaluations,
            request.parameter,
            value_id,
            value,
            properties_builder.build()
        )

    @staticmethod
    def of_default(request, context, reason, properties_builder):
        """

        :param RemoteConfigRequest request:
        :param Evaluator.Context context:
        :param str reason:
        :param PropertiesBuilder properties_builder:

        :rtype: RemoteConfigEvaluation
        """
        return RemoteConfigEvaluation.of(request, context, None, request.default_value, reason, properties_builder)

    @property
    def parameter(self):
        """
        :rtype: RemoteConfigParameter
        """
        return self.__parameter

    @property
    def value_id(self):
        """
        :rtype: int or None
        """
        return self.__value_id

    @property
    def value(self):
        """
        :rtype: object or None
        """
        return self.__value

    @property
    def properties(self):
        """
        :rtype: dict[str, object]
        """
        return self.__properties
