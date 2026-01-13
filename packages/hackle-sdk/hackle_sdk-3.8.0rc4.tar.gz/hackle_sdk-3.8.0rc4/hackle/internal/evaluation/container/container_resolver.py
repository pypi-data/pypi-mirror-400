from hackle.internal.evaluation.bucket.bucketer import Bucketer
from hackle.internal.evaluation.evaluator.experiment.experiment_request import ExperimentRequest
from hackle.internal.model.entities import Container


class ContainerResolver(object):

    def __init__(self, bucketer):
        """
        :param Bucketer bucketer:
        """
        self.__bucketer = bucketer

    def is_user_in_container_group(self, request, container):
        """
        :param ExperimentRequest request:
        :param Container container:

        :rtype: bool
        """

        identifier = request.user.identifiers.get(request.experiment.identifier_type)
        if identifier is None:
            return False

        bucket = request.workspace.get_bucket_or_none(container.bucket_id)
        if bucket is None:
            raise Exception('Bucket[{}]'.format(container.bucket_id))

        slot = self.__bucketer.bucketing(bucket, identifier)
        if slot is None:
            return False

        container_group = container.get_group_or_none(slot.variation_id)
        if container_group is None:
            raise Exception('ContainerGroup[{}]'.format(slot.variation_id))

        return request.experiment.id in container_group.experiments
