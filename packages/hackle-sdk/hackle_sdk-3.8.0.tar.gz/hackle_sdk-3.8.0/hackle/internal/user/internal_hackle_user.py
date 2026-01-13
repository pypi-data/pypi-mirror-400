from hackle.internal.model.properties_builder import PropertiesBuilder
from hackle.internal.user.identifiers_builder import IdentifiersBuilder


class InternalHackleUser(object):
    def __init__(self, identifiers, properties):
        """

        :param dict[str, str] identifiers:
        :param dict[str, object] properties:
        """
        self.__identifiers = identifiers
        self.__properties = properties

    @staticmethod
    def builder():
        return InternalHackleUser.Builder()

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

    def __eq__(self, other):
        if not isinstance(other, InternalHackleUser):
            return False
        return self.identifiers == other.identifiers and self.properties == other.properties

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "HackleUser(identifiers={}, properties={})".format(self.__identifiers, self.__properties)

    def __repr__(self):
        return self.__str__()

    class Builder(object):

        def __init__(self):
            self.__identifiers = IdentifiersBuilder()
            self.__properties = PropertiesBuilder()

        def identifier(self, identifier_type, identifier_value):
            """
            :param str identifier_type:
            :param str identifier_value:
            :rtype: InternalHackleUser.Builder
            """
            self.__identifiers.add(identifier_type, identifier_value)
            return self

        def identifiers(self, identifiers):
            """
            :param dict[str, str] identifiers:
            :rtype: InternalHackleUser.Builder
            """
            self.__identifiers.add_identifiers(identifiers)
            return self

        def property(self, property_key, property_value):
            """
            :param str property_key:
            :param object property_value:
            :rtype: InternalHackleUser.Builder
            """
            self.__properties.add(property_key, property_value)
            return self

        def properties(self, properties):
            """
            :param dict[str, object] properties:
            :rtype: InternalHackleUser.Builder
            """
            self.__properties.add_properties(properties)
            return self

        def build(self):
            """
            :rtype: InternalHackleUser
            """
            return InternalHackleUser(self.__identifiers.build(), self.__properties.build())
