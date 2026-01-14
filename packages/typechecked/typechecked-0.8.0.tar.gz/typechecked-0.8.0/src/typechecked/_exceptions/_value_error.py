"""TypeChecked ValueError exceptions."""
from ._error_tag import ErrorTag
from ._tagged_exception import TaggedException, generate_message


class TypeCheckedValueError(TaggedException[ValueError], ValueError):
    """Base class for all TypeChecked ValueErrors.

    It differs from a standard ValueError by the addition of a
    tag code used to very specifically identify where the error
    was thrown in the code for testing and development support.

    This tag code does not have a direct semantic meaning except to identify
    the specific code throwing the exception for tests.

    Usage:
        raise TypeCheckedValueError("An error occurred", tag=MyErrorTags.SOME_ERROR)

    Args:
        msg (str): The error message.
        tag (ErrorTag): The tag code.
    """
    def __init__(self, msg: str, *, tag: ErrorTag) -> None:
        """Raises a TypeCheckedValueError with the given message and tag.

        :param str msg: The error message.
        :param ErrorTag tag: The tag code.
        """
        message = generate_message(msg, tag)
        super().__init__(message, tag=tag)
