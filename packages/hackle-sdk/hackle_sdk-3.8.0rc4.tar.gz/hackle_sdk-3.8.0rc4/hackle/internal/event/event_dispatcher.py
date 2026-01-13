import json

from hackle.internal.event.user_event import UserEvent, TrackEvent, ExposureEvent, RemoteConfigEvent
from hackle.internal.http.http_client import HttpClient
from hackle.internal.http.http_request import HttpRequest
from hackle.internal.http.http_response import HttpResponse
from hackle.internal.metrics.timer import TimerSample
from hackle.internal.monitoring.metrics.api_call_metrics import ApiCallMetrics
from hackle.internal.user.identifier_type import IdentifierType


# noinspection PyMethodMayBeStatic
class EventSerializer(object):

    def serialize(self, events):
        """
        :param list[UserEvent] events:
        :rtype: str
        """
        return json.dumps(self.__payload(events))

    def __payload(self, events):
        """
        :param list[UserEvent] events:
        :rtype: dict
        """
        exposure_events = []
        track_events = []
        remote_config_events = []
        for event in events:
            if isinstance(event, ExposureEvent):
                exposure_events.append(self.__exposure_event(event))

            if isinstance(event, TrackEvent):
                track_events.append(self.__track_event(event))

            if isinstance(event, RemoteConfigEvent):
                remote_config_events.append(self.__remote_config_event(event))

        return {
            'exposureEvents': exposure_events,
            'trackEvents': track_events,
            'remoteConfigEvents': remote_config_events
        }

    def __exposure_event(self, event):
        """
        :param ExposureEvent event:
        :rtype: dict
        """
        return {
            "insertId": event.insert_id,
            "timestamp": event.timestamp,

            "userId": event.user.identifiers.get(IdentifierType.ID),
            "identifiers": event.user.identifiers,
            "userProperties": event.user.properties,
            "hackleProperties": {},

            "experimentId": event.experiment.id,
            "experimentKey": event.experiment.key,
            "experimentType": event.experiment.type,
            "experimentVersion": event.experiment.version,
            "variationId": event.variation_id,
            "variationKey": event.variation_key,
            "decisionReason": event.reason,
            "properties": event.properties
        }

    def __track_event(self, event):
        """
        :param  TrackEvent event:
        :rtype: dict
        """
        return {
            "insertId": event.insert_id,
            "timestamp": event.timestamp,

            "userId": event.user.identifiers.get(IdentifierType.ID),
            "identifiers": event.user.identifiers,
            "userProperties": event.user.properties,
            "hackleProperties": {},

            "eventTypeId": event.event_type.id,
            "eventTypeKey": event.event_type.key,
            "value": event.event.value,
            "properties": event.event.properties
        }

    def __remote_config_event(self, event):
        """
        :param RemoteConfigEvent event:
        :rtype: dict
        """
        return {
            "insertId": event.insert_id,
            "timestamp": event.timestamp,

            "userId": event.user.identifiers.get(IdentifierType.ID),
            "identifiers": event.user.identifiers,
            "userProperties": event.user.properties,
            "hackleProperties": {},

            "parameterId": event.parameter.id,
            "parameterKey": event.parameter.key,
            "parameterType": event.parameter.type,
            "valueId": event.value_id,
            "decisionReason": event.reason,
            "properties": event.properties
        }


class EventDispatcher(object):
    def __init__(self, event_url, http_client):
        """
        :param str event_url:
        :param HttpClient http_client:
        """
        self.__url = event_url + '/api/v2/events'
        self.__http_client = http_client
        self.__serializer = EventSerializer()

    def dispatch(self, events):
        """
        :param list[UserEvent] events:
        """
        request = self.__create_request(events)
        response = self.__execute(request)
        self.__handle_response(response)

    def __create_request(self, events):
        """
        :param list[UserEvent] events::
        :rtype: HttpRequest
        """
        body = self.__serializer.serialize(events)
        return HttpRequest.builder() \
            .method("POST") \
            .url(self.__url) \
            .body(body) \
            .header("Content-Type", "application/json") \
            .build()

    def __execute(self, request):
        """
        :param HttpRequest request:
        :rtype: HttpResponse
        """
        sample = TimerSample.start()
        try:
            response = self.__http_client.execute(request)
            ApiCallMetrics.record("post.events", sample, response)
            return response
        except Exception as e:
            ApiCallMetrics.record("post.events", sample, None)
            raise e

    # noinspection PyMethodMayBeStatic
    def __handle_response(self, response):
        """
        :param HttpResponse response:
        """
        if not response.is_successful:
            raise Exception('Http status code: {}'.format(response.status_code))
