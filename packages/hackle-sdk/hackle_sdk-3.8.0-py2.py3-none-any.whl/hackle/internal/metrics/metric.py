import abc

from six import add_metaclass


@add_metaclass(abc.ABCMeta)
class Metric(object):

    def __init__(self, id_):
        """
        :param hackle.internal.metrics.metric.MetricId id_:
        """
        self.__id = id_

    @property
    def id(self):
        """
        :rtype: hackle.internal.metrics.metric.MetricId
        """
        return self.__id

    @abc.abstractmethod
    def measure(self):
        """
        :rtype: list[hackle.internal.metrics.measurement.Measurement]
        """
        pass

    def __eq__(self, other):
        if not isinstance(other, Metric):
            return False
        return self.__id == other.__id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__id)


class MetricId:
    def __init__(self, name, tags, type_):
        """
        :param str name:
        :param dict[str, str] tags:
        :param str type_:
        """
        self.__name = name
        self.__tags = tags
        self.__type = type_
        self.__hash = hash((name, frozenset(tags.items())))

    @property
    def name(self):
        """
        :rtype: str
        """
        return self.__name

    @property
    def tags(self):
        """
        :rtype: dict[str, str]
        """
        return self.__tags

    @property
    def type(self):
        """
        :rtype: str 
        """
        return self.__type

    def __eq__(self, other):
        if not isinstance(other, MetricId):
            return False
        return self.__name == other.__name and self.__tags == other.__tags

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "MetricId(name={}, tags={})".format(self.__name, self.__tags)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.__hash


class MetricType:
    COUNTER = "COUNTER"
    TIMER = "TIMER"
