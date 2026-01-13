from hackle.internal.logger.log import Log
from hackle.internal.type import hackle_types


class PropertiesBuilder(object):
    __SYSTEM_PROPERTY_KEY_PREFIX = '$'
    __MAX_PROPERTIES_COUNT = 128
    __MAX_PROPERTY_KEY_LENGTH = 128
    __MAX_PROPERTY_VALUE_LENGTH = 1024

    def __init__(self):
        self.__properties = {}  # type: dict[str, object]

    @staticmethod
    def sanitize(properties):
        """
        :param dict or None properties:
        :rtype: dict
        """
        return PropertiesBuilder().add_properties(properties or {}).build()

    def build(self):
        """
        :rtype: dict
        """
        return self.__properties

    def add_properties(self, properties):
        """
        :param dict properties:
        :rtype: PropertiesBuilder
        """
        if properties is None or not isinstance(properties, dict):
            Log.get().warning('Invalid properties: {} (expected: dict)'.format(properties))
            return self

        for property_key in properties:
            self.add(property_key, properties[property_key])

        return self

    def add(self, key, value):
        """
        :param str key:
        :param object value:
        :rtype: PropertiesBuilder
        """
        if len(self.__properties) >= self.__MAX_PROPERTIES_COUNT:
            return self

        if not self.__is_valid_key(key):
            Log.get().warning('Invalid property key: {} (expected: string[1..128])')
            return self

        sanitized_value = self.__sanitize_value_or_none(key, value)
        if sanitized_value is None:
            return self

        self.__properties[key] = sanitized_value

        return self

    def __is_valid_key(self, key):
        if key is None:
            return False

        if not hackle_types.is_string(key):
            return False

        if len(key) == 0:
            return False

        if len(key) > self.__MAX_PROPERTY_KEY_LENGTH:
            return False

        return True

    def __sanitize_value_or_none(self, key, value):
        """
        :param str key:
        :param object or None value:
        :rtype: object or None
        """
        if value is None:
            return None

        if isinstance(value, list):
            values = []
            for element in value:
                if element is not None and self.__is_valid_element(element):
                    values.append(element)
            return values

        if self.__is_valid_value(value):
            return value

        if key.startswith(self.__SYSTEM_PROPERTY_KEY_PREFIX):
            return value

        return None

    def __is_valid_element(self, element):
        if hackle_types.is_string(element):
            return len(element) <= self.__MAX_PROPERTY_VALUE_LENGTH
        elif hackle_types.is_finite_number(element):
            return True
        else:
            return False

    def __is_valid_value(self, value):
        if hackle_types.is_string(value):
            return len(value) <= self.__MAX_PROPERTY_VALUE_LENGTH
        elif hackle_types.is_finite_number(value):
            return True
        elif hackle_types.is_bool(value):
            return True
        else:
            return False

    def __contains__(self, item):
        return item in self.__properties
