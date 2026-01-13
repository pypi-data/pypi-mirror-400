from hackle.internal.evaluation.action.action_resolver import ActionResolver
from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.evaluation.match.target_matcher import TargetMatcher
from hackle.internal.model.entities import Variation


class OverrideResolver(object):
    def __init__(self, target_matcher, action_resolver):
        """
        :param TargetMatcher target_matcher:
        :param ActionResolver action_resolver:
        """
        self.__target_matcher = target_matcher
        self.__action_resolver = action_resolver

    def resolve_or_none(self, request, context):
        """
        :param ExperimentRequest request:
        :param Evaluator.Context context:

        :rtype: Variation or None
        """
        user_overridden_variation = self.__resolve_user_override_or_none(request)
        if user_overridden_variation is not None:
            return user_overridden_variation

        return self.__resolve_segment_override(request, context)

    # noinspection PyMethodMayBeStatic
    def __resolve_user_override_or_none(self, request):
        """
        :param ExperimentRequest request:
        :rtype: Variation or None
        """
        experiment = request.experiment
        identifier = request.user.identifiers.get(experiment.identifier_type)
        if identifier is None:
            return None

        overridden_variation_id = experiment.user_overrides.get(identifier)
        if overridden_variation_id is None:
            return None

        return experiment.get_variation_by_id_or_none(overridden_variation_id)

    def __resolve_segment_override(self, request, context):
        """
        :param ExperimentRequest request:
        :param Evaluator.Context context:
        :rtype: Variation or None
        """
        for overridden_rule in request.experiment.segment_overrides:
            if self.__target_matcher.matches(request, context, overridden_rule.target):
                return self.__action_resolver.resolve_or_none(request, overridden_rule.action)

        return None
