from hackle.decision import DecisionReason
from hackle.internal.evaluation.evaluator.evaluator import ContextualEvaluator, Evaluator
from hackle.internal.evaluation.evaluator.remoteconfig.remote_config_evaluation import RemoteConfigEvaluation
from hackle.internal.evaluation.evaluator.remoteconfig.remote_config_request import RemoteConfigRequest
from hackle.internal.evaluation.target.remote_config_target_rule_determiner import RemoteConfigTargetRuleDeterminer
from hackle.internal.model.entities import RemoteConfigParameterValue
from hackle.internal.model.properties_builder import PropertiesBuilder
from hackle.internal.type import hackle_types


class RemoteConfigEvaluator(ContextualEvaluator):

    def __init__(self, target_rule_determiner):
        """
        :param RemoteConfigTargetRuleDeterminer target_rule_determiner:
        """
        super(RemoteConfigEvaluator, self).__init__()
        self.__target_rule_determiner = target_rule_determiner

    def supports(self, request):
        return isinstance(request, RemoteConfigRequest)

    def evaluate_internal(self, request, context):
        """
        :param RemoteConfigRequest request:
        :param Evaluator.Context context:

        :rtype: RemoteConfigEvaluation
        """
        properties_builder = PropertiesBuilder() \
            .add("requestValueType", request.required_type) \
            .add("requestDefaultValue", request.default_value)

        if request.user.identifiers.get(request.parameter.identifier_type) is None:
            return RemoteConfigEvaluation.of_default(
                request, context, DecisionReason.IDENTIFIER_NOT_FOUND, properties_builder)

        target_rule = self.__target_rule_determiner.determine_target_rule_or_none(request, context)
        if target_rule is not None:
            properties_builder.add("targetRuleKey", target_rule.key)
            properties_builder.add("targetRuleName", target_rule.name)
            return self.__evaluation(
                request, context, target_rule.value, DecisionReason.TARGET_RULE_MATCH, properties_builder)

        return self.__evaluation(
            request, context, request.parameter.default_value, DecisionReason.DEFAULT_RULE, properties_builder)

    def __evaluation(self, request, context, parameter_value, reason, properties_builder):
        """
        :param RemoteConfigRequest request:
        :param Evaluator.Context context:
        :param RemoteConfigParameterValue parameter_value:
        :param str reason:
        :param PropertiesBuilder properties_builder:

        :rtype: RemoteConfigEvaluation
        """
        if self.__is_valid(request.required_type, parameter_value.raw_value):
            return RemoteConfigEvaluation.of(
                request,
                context,
                parameter_value.id,
                parameter_value.raw_value,
                reason,
                properties_builder
            )
        else:
            return RemoteConfigEvaluation.of_default(
                request,
                context,
                DecisionReason.TYPE_MISMATCH,
                properties_builder
            )

    # noinspection PyMethodMayBeStatic
    def __is_valid(self, required_type, value):
        if required_type == 'NULL':
            return True
        elif required_type == 'STRING':
            return hackle_types.is_string(value)
        elif required_type == 'NUMBER':
            return hackle_types.is_number(value)
        elif required_type == 'BOOLEAN':
            return hackle_types.is_bool(value)
        else:
            return False
