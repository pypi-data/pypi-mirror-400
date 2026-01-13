from hackle.internal.evaluation.bucket.bucketer import Bucketer
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.logger.log import Log
from hackle.internal.model.entities import TargetAction, Variation


class ActionResolver(object):
    def __init__(self, bucketer):
        """
        :param Bucketer bucketer:
        """
        self.__bucketer = bucketer

    def resolve_or_none(self, request, action):
        """
        :param ExperimentRequest request:
        :param TargetAction action:
        :rtype: Variation or None
        """
        if action.type == 'VARIATION':
            return self.__resolve_variation(request, action)
        elif action.type == 'BUCKET':
            return self.__resolve_bucket(request, action)
        else:
            Log.get().debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(action.type))
            return None

    # noinspection PyMethodMayBeStatic
    def __resolve_variation(self, request, action):
        """
        :param ExperimentRequest request:
        :param TargetAction action:
        :rtype: Variation
        """
        variation = request.experiment.get_variation_by_id_or_none(action.variation_id)
        if variation is None:
            raise Exception('variation[{}]'.format(action.variation_id))
        return variation

    def __resolve_bucket(self, request, action):
        """
         :param ExperimentRequest request:
         :param TargetAction action:
         :rtype: Variation or None
         """
        bucket = request.workspace.get_bucket_or_none(action.bucket_id)
        if bucket is None:
            raise Exception('bucket[{}]'.format(action.bucket_id))

        identifier = request.user.identifiers.get(request.experiment.identifier_type)
        if identifier is None:
            return None

        allocated_slot = self.__bucketer.bucketing(bucket, identifier)
        if allocated_slot is None:
            return None

        return request.experiment.get_variation_by_id_or_none(allocated_slot.variation_id)
