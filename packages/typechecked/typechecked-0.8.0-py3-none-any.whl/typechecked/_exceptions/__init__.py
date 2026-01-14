"""Custom exceptions for the typechecked package."""
from ._error_tag import ErrorTag
from ._tagged_exception import TaggedException
from ._recursion_error import TypeCheckedRecursionError
from ._type_error import TypeCheckedTypeError
from ._value_error import TypeCheckedValueError

__all__ = [
    "TaggedException",
    "TypeCheckedRecursionError",
    "TypeCheckedTypeError",
    "TypeCheckedValueError",
    "ErrorTag",
]
