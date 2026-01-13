import abc
import uuid

from six import add_metaclass

from hackle.internal.evaluation.evaluator.experiment.experiment_evaluation import ExperimentEvaluation
from hackle.internal.evaluation.evaluator.remoteconfig.remote_config_evaluation import RemoteConfigEvaluation
from hackle.internal.model.entities import EventType, Experiment, RemoteConfigParameter
from hackle.internal.user.internal_hackle_user import InternalHackleUser
from hackle.model import HackleEvent


@add_metaclass(abc.ABCMeta)
class UserEvent(object):

    def __init__(self, insert_id, timestamp, user):
        """
        :param str insert_id:
        :param int timestamp:
        :param InternalHackleUser user:
        """
        self.__insert_id = insert_id
        self.__timestamp = timestamp
        self.__user = user

    @property
    def insert_id(self):
        """
        :rtype: str
        """
        return self.__insert_id

    @property
    def timestamp(self):
        """
        :rtype: int
        """
        return self.__timestamp

    @property
    def user(self):
        """
        :rtype: InternalHackleUser
        """
        return self.__user

    @staticmethod
    def exposure(user, evaluation, properties, timestamp):
        """
        :param InternalHackleUser user:
        :param ExperimentEvaluation evaluation:
        :param dict[str, object] properties:
        :param int timestamp:
        :rtype: ExposureEvent
        """
        return ExposureEvent(
            UserEvent.__insert_id(),
            timestamp,
            user,
            evaluation.experiment,
            evaluation.variation_id,
            evaluation.variation_key,
            evaluation.reason,
            properties
        )

    @staticmethod
    def track(user, event_type, event, timestamp):
        """
        :param InternalHackleUser user:
        :param EventType event_type:
        :param HackleEvent event:
        :param int timestamp:

        :rtype: TrackEvent
        """
        return TrackEvent(
            UserEvent.__insert_id(),
            timestamp,
            user,
            event_type,
            event
        )

    @staticmethod
    def remote_config(user, evaluation, properties, timestamp):
        """
        :param InternalHackleUser user:
        :param RemoteConfigEvaluation evaluation:
        :param dict[str, object] properties:
        :param int timestamp:
        :rtype: RemoteConfigEvent
        """
        return RemoteConfigEvent(
            UserEvent.__insert_id(),
            timestamp,
            user,
            evaluation.parameter,
            evaluation.value_id,
            evaluation.reason,
            properties
        )

    @staticmethod
    def __insert_id():
        """
        :rtype: str
        """
        return str(uuid.uuid4())


class ExposureEvent(UserEvent):

    def __init__(self, insert_id, timestamp, user, experiment, variation_id, variation_key, reason, properties):
        """
        :param str insert_id:
        :param int timestamp:
        :param InternalHackleUser user:
        :param Experiment experiment:
        :param int or None variation_id:
        :param str variation_key:
        :param str reason:
        :param dict[str, object] properties:
        """
        super(ExposureEvent, self).__init__(insert_id, timestamp, user)
        self.experiment = experiment
        self.variation_id = variation_id
        self.variation_key = variation_key
        self.reason = reason
        self.properties = properties


class TrackEvent(UserEvent):

    def __init__(self, insert_id, timestamp, user, event_type, event):
        """
        :param str insert_id:
        :param int timestamp:
        :param InternalHackleUser user:
        :param EventType event_type:
        :param HackleEvent event:
        """
        super(TrackEvent, self).__init__(insert_id, timestamp, user)
        self.event_type = event_type
        self.event = event


class RemoteConfigEvent(UserEvent):

    def __init__(self, insert_id, timestamp, user, parameter, value_id, reason, properties):
        """
        :param str insert_id:
        :param int timestamp:
        :param InternalHackleUser user:
        :param RemoteConfigParameter parameter:
        :param int or None value_id:
        :param str reason:
        :param dict[str, object] properties:
        """
        super(RemoteConfigEvent, self).__init__(insert_id, timestamp, user)
        self.parameter = parameter
        self.value_id = value_id
        self.reason = reason
        self.properties = properties
