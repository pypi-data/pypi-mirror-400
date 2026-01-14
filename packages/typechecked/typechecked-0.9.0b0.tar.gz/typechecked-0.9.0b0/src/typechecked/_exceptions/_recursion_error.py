"""TypeChecked Recursion Error Exception."""
from ._error_tag import ErrorTag
from ._tagged_exception import TaggedException, generate_message


class TypeCheckedRecursionError(TaggedException[RecursionError], RecursionError):
    """Exception raised when maximum recursion depth is exceeded in typechecked.

    Usage:
        raise TypeCheckedRecursionError("An error occurred",
                                        tag=MyErrorTags.SOME_ERROR)

    :param str msg: The error message.
    :param ErrorTag tag: The tag code.
    """
    def __init__(self, msg: str, *, tag: ErrorTag) -> None:
        """Raises a TypeCheckedRecursionError with the given message and tag.

        :param str msg: The error message.
        :param ErrorTag tag: The tag code.
        """
        message = generate_message(msg, tag)
        super().__init__(message, tag=tag)
        super().__init__(message, tag=tag)
