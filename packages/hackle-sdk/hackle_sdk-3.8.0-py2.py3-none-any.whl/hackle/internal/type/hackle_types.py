import math
import numbers

from six import integer_types
from six import string_types


# String type

def is_string(value):
    return value is not None and isinstance(value, string_types)


def is_empty_string(value):
    return is_string(value) and len(value) == 0


def is_not_empty_string(value):
    return is_string(value) and len(value) > 0


# Number type

def is_number(value):
    return value is not None and not isinstance(value, bool) and isinstance(value, numbers.Number)


def is_finite_number(value):
    if not isinstance(value, (numbers.Integral, float)):
        # numbers.Integral instead of int to accommodate long integer in python 2
        return False

    if isinstance(value, bool):
        # bool is a subclass of int
        return False

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return False

    if abs(value) > (2 ** 53):
        return False

    return True


def is_positive_int(value):
    return is_number(value) and isinstance(value, integer_types) and value > 0


def as_int_or_none(value):
    try:
        return int(value)
    except ValueError:
        return None


# Bool

def is_bool(value):
    return value is not None and isinstance(value, bool)
