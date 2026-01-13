import abc

from six import add_metaclass

from .internal.logger.log import Log
from .internal.model.properties_builder import PropertiesBuilder
from .internal.type import hackle_types
from .internal.user.identifiers_builder import IdentifiersBuilder


class User(object):
    def __init__(self, id, properties):
        self.id = id
        self.properties = properties

    def __str__(self):
        return 'User(id={}, properties={})'.format(self.id, self.properties)


class HackleUser(object):
    def __init__(
            self,
            id=None,
            user_id=None,
            device_id=None,
            identifiers=None,
            properties=None):
        self.__id = id
        self.__user_id = user_id
        self.__device_id = device_id
        self.__identifiers = identifiers
        self.__properties = properties

    @staticmethod
    def builder():
        return HackleUserBuilder()

    @staticmethod
    def of(user):
        return HackleUser.builder().id(user.id).properties(user.properties).build()

    @property
    def id(self):
        """
        :rtype: string or None
        """
        return self.__id

    @property
    def user_id(self):
        """
        :rtype: string or None
        """
        return self.__user_id

    @property
    def device_id(self):
        """
        :rtype: string or None
        """
        return self.__device_id

    @property
    def identifiers(self):
        """
        :rtype: dict[str, str]
        """
        return self.__identifiers

    @property
    def properties(self):
        """
        :rtype: dict[str, object]
        """
        return self.__properties

    def __str__(self):
        return 'HackleUser(id={}, user_id={}, device_id={}, identifiers={}, properties={})'.format(self.__id,
                                                                                                   self.__user_id,
                                                                                                   self.__device_id,
                                                                                                   self.__identifiers,
                                                                                                   self.__properties)

    def __repr__(self):
        return self.__str__()


class HackleUserBuilder:

    def __init__(self):
        self.__id = None
        self.__user_id = None
        self.__device_id = None
        self.__identifiers = IdentifiersBuilder()
        self.__properties = PropertiesBuilder()

    def id(self, id_):
        self.__id = IdentifiersBuilder.sanitize_value_or_none(id_)
        return self

    def user_id(self, user_id):
        self.__user_id = IdentifiersBuilder.sanitize_value_or_none(user_id)
        return self

    def device_id(self, device_id):
        self.__device_id = IdentifiersBuilder.sanitize_value_or_none(device_id)
        return self

    def session_id(self, session_id):
        return self.identifier("$sessionId", session_id)

    def identifier(self, identifier_type, identifier_value):
        self.__identifiers.add(identifier_type, identifier_value)
        return self

    def identifiers(self, identifiers):
        self.__identifiers.add_identifiers(identifiers)
        return self

    def property(self, property_key, property_value):
        self.__properties.add(property_key, property_value)
        return self

    def properties(self, properties):
        self.__properties.add_properties(properties)
        return self

    def build(self):
        return HackleUser(
            self.__id,
            self.__user_id,
            self.__device_id,
            self.__identifiers.build(),
            self.__properties.build(),
        )


class Event(object):
    def __init__(self, key, value, properties):
        self.key = key
        self.value = value
        self.properties = properties


class HackleEvent(object):
    def __init__(self, key, value, properties):
        """
        :param str key:
        :param float or None value:
        :param dict properties:
        """
        self.__key = key
        self.__value = value
        self.__properties = properties

    @staticmethod
    def builder(key):
        return HackleEventBuilder(key)

    @staticmethod
    def from_event(event):
        if isinstance(event, HackleEvent):
            return event

        return HackleEvent.builder(event.key) \
            .value(event.value) \
            .properties(event.properties) \
            .build()

    @property
    def key(self):
        """
        :rtype: str
        """
        return self.__key

    @property
    def value(self):
        """
        :rtype: float or None
        """
        return self.__value

    @property
    def properties(self):
        """
        :rtype: dict[str, object]
        """
        return self.__properties

    @property
    def is_valid(self):
        """
        :rtype: bool
        """
        return self.error_or_none is None

    @property
    def error_or_none(self):
        """
        :rtype: str or None
        """
        if not hackle_types.is_not_empty_string(self.__key):
            return "Invalid event key: {} (expected: not empty string)".format(self.__key)

        if self.__value is not None and not hackle_types.is_finite_number(self.__value):
            return "Invalid event value: {} (expected: finite number)"

        if self.__properties is None or not isinstance(self.__properties, dict):
            return "Invalid event properties: {} (expected: dict)".format(self.__properties)

        return None

    def __eq__(self, other):
        if not isinstance(other, HackleEvent):
            return False
        return self.__key == other.__key and self.__value == other.__value and self.__properties == other.__properties

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if not self.is_valid:
            return "InvalidHackleEvent({})".format(self.error_or_none)

        return "HackleEvent(key={}, value={}, properties={})".format(self.__key, self.__value, self.__properties)

    def __repr__(self):
        return self.__str__()


class HackleEventBuilder(object):

    def __init__(self, key):
        self.__key = key
        self.__value = None
        self.__properties = PropertiesBuilder()

    def build(self):
        return HackleEvent(
            self.__key,
            self.__value,
            self.__properties.build()
        )

    def value(self, value):
        self.__value = value
        return self

    def property(self, key, value):
        self.__properties.add(key, value)
        return self

    def properties(self, properties):
        self.__properties.add_properties(properties)
        return self


class PropertyOperation(object):
    SET = '$set'
    SET_ONCE = '$setOnce'
    UNSET = '$unset'
    INCREMENT = '$increment'
    APPEND = '$append'
    APPEND_ONCE = '$appendOnce'
    PREPEND = '$prepend'
    PREPEND_ONCE = '$prependOnce'
    REMOVE = '$remove'
    CLEAR_ALL = '$clearAll'


class PropertyOperations(object):

    def __init__(self, operations):
        """
        :param dict[str, dict[str, object]] operations:
        """
        self.__operations = operations

    @staticmethod
    def builder():
        """
        :rtype:  PropertyOperationsBuilder
        """
        return PropertyOperationsBuilder()

    def to_event(self):
        """
        :rtype: HackleEvent
        """
        builder = HackleEvent.builder('$properties')
        for operation in self.__operations:
            builder.property(operation, self.__operations[operation])
        return builder.build()

    def __iter__(self):
        for operation in self.__operations:
            yield operation, self.__operations[operation]

    def __str__(self):
        return 'PropertyOperations({})'.format(self.__operations.__str__())

    def __repr__(self):
        return self.__str__()


class PropertyOperationsBuilder(object):

    def __init__(self):
        self.__operations = {}  # type: dict[str, PropertiesBuilder]

    def set(self, key, value):
        """
        :param str key:
        :param object value:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.SET, key, value)
        return self

    def set_once(self, key, value):
        """
        :param str key:
        :param object value:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.SET_ONCE, key, value)
        return self

    def unset(self, key):
        """
        :param str key:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.UNSET, key, '-')
        return self

    def increment(self, key, value):
        """
        :param str key:
        :param float value:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.INCREMENT, key, value)
        return self

    def append(self, key, value):
        """
        :param str key:
        :param object value:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.APPEND, key, value)
        return self

    def append_once(self, key, value):
        """
        :param str key:
        :param object value:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.APPEND_ONCE, key, value)
        return self

    def prepend(self, key, value):
        """
        :param str key:
        :param object value:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.PREPEND, key, value)
        return self

    def prepend_once(self, key, value):
        """
        :param str key:
        :param object value:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.PREPEND_ONCE, key, value)
        return self

    def remove(self, key, value):
        """
        :param str key:
        :param object value:
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.REMOVE, key, value)
        return self

    def clear_all(self):
        """
        :rtype: PropertyOperationsBuilder
        """
        self.__add(PropertyOperation.CLEAR_ALL, 'clearAll', '-')
        return self

    def __add(self, operation, key, value):
        """
        :param str operation:
        :param str key:
        :param object or None value:
        """
        if self.__contains__(key):
            Log.get().debug('Property already added. Ignore the operation. [operation={}, key={}, value={}]'
                      .format(operation, key, value))
            return

        builder = self.__operations.get(operation) or self.__operations.setdefault(operation, PropertiesBuilder())
        builder.add(key, value)

    def build(self):
        """
        :rtype: PropertyOperations
        """
        operations = {}
        for operation in self.__operations:
            operations[operation] = self.__operations[operation].build()
        return PropertyOperations(operations)

    def __contains__(self, item):
        for operation in self.__operations:
            if item in self.__operations[operation]:
                return True
        return False


class Hackle:
    @staticmethod
    def user(id, **kwargs):
        return User(id, kwargs)

    @staticmethod
    def event(key, value=None, **kwargs):
        return Event(key, value, kwargs)


@add_metaclass(abc.ABCMeta)
class HackleRemoteConfig(object):
    @abc.abstractmethod
    def get(self, key, default=None):
        pass
