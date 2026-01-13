class Measurement:
    def __init__(self, name, value_supplier):
        """
        :param str name:
        :param function value_supplier: () => float
        """
        self.__name = name
        self.__value_supplier = value_supplier

    @property
    def name(self):
        """
        :rtype: str
        """
        return self.__name

    @property
    def value(self):
        """
        :rtype: float
        """
        return self.__value_supplier()


class Measurements:
    COUNT = "count"
    TOTAL = "total"
    MAX = "max"
    MEAN = "mean"
