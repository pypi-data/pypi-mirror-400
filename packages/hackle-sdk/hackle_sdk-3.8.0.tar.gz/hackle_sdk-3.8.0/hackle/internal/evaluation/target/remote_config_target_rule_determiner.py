from hackle.internal.evaluation.bucket.bucketer import Bucketer
from hackle.internal.evaluation.evaluator.evaluator import Evaluator
from hackle.internal.evaluation.evaluator.remoteconfig.remote_config_request import RemoteConfigRequest
from hackle.internal.evaluation.match.target_matcher import TargetMatcher
from hackle.internal.model.entities import RemoteConfigTargetRule


class RemoteConfigTargetRuleDeterminer(object):
    def __init__(self, matcher):
        """
        :param RemoteConfigTargetRuleMatcher matcher:
        """
        self.__matcher = matcher

    def determine_target_rule_or_none(self, request, context):
        """
        :param RemoteConfigRequest request:
        :param Evaluator.Context context:

        :rtype: RemoteConfigTargetRule or None
        """

        for target_rule in request.parameter.target_rules:
            if self.__matcher.matches(request, context, target_rule):
                return target_rule
        return None


class RemoteConfigTargetRuleMatcher(object):
    def __init__(self, target_matcher, bucketer):
        """
        :param TargetMatcher target_matcher:
        :param Bucketer bucketer:
        """
        self.__target_matcher = target_matcher
        self.__bucketer = bucketer

    def matches(self, request, context, target_rule):
        """
        :param RemoteConfigRequest request:
        :param Evaluator.Context context:
        :param RemoteConfigTargetRule target_rule:

        :rtype: bool
        """
        if not self.__target_matcher.matches(request, context, target_rule.target):
            return False

        identifier = request.user.identifiers.get(request.parameter.identifier_type)
        if identifier is None:
            return False

        bucket = request.workspace.get_bucket_or_none(target_rule.bucket_id)
        if bucket is None:
            raise Exception('Bucket[{}]'.format(target_rule.bucket_id))

        return self.__bucketer.bucketing(bucket, identifier) is not None
