from hackle.internal.logger.log import Log
from hackle.internal.type import hackle_types


class IdentifiersBuilder(object):
    __MAX_IDENTIFIER_TYPE_LENGTH = 128
    __MAX_IDENTIFIER_VALUE_LENGTH = 512

    def __init__(self):
        self.__identifiers = {}

    def build(self):
        return self.__identifiers

    def add_identifiers(self, identifiers):
        if identifiers is None:
            return self

        if not isinstance(identifiers, dict):
            Log.get().warning('Identifiers MUST be dictionary [Request Type={}]'.format(type(identifiers)))
            return self

        for identifier_type in identifiers:
            self.add(identifier_type, identifiers[identifier_type])

        return self

    def add(self, identifier_type, identifier_value):

        sanitized_identifier_value = self.sanitize_value_or_none(identifier_value)
        if self.__is_value_type(identifier_type) and sanitized_identifier_value is not None:
            self.__identifiers[identifier_type] = sanitized_identifier_value
        else:
            Log.get().warning('Invalid user identifier [type={}, value={}]'.format(identifier_type, identifier_value))
        return self

    @staticmethod
    def sanitize_value_or_none(identifier_value):
        if identifier_value is None:
            return None

        if hackle_types.is_not_empty_string(identifier_value) \
                and len(identifier_value) <= IdentifiersBuilder.__MAX_IDENTIFIER_VALUE_LENGTH:
            return identifier_value

        if hackle_types.is_finite_number(identifier_value):
            return str(identifier_value)

        return None

    def __is_value_type(self, identifier_type):
        if identifier_type is None:
            return False

        if not hackle_types.is_string(identifier_type):
            return False

        if hackle_types.is_empty_string(identifier_type):
            return False

        if len(identifier_type) > self.__MAX_IDENTIFIER_TYPE_LENGTH:
            return False

        return True
