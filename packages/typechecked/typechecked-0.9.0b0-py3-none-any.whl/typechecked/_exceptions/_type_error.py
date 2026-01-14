"""TypeChecked TypeError exceptions."""
from ._error_tag import ErrorTag
from ._tagged_exception import TaggedException, generate_message


class TypeCheckedTypeError(TaggedException[TypeError], TypeError):
    """Base class for all TypeChecked TypeErrors.

    It differs from a standard TypeError by the addition of a
    tag code used to very specifically identify where the error
    was thrown in the code for testing and development support.

    This tag code does not have a direct semantic meaning except to identify
    the specific code throwing the exception for tests.

    Usage:
        raise TypeCheckedTypeError("An error occurred", tag=MyErrorTags.SOME_ERROR)

    :param str msg: The error message.
    :param ErrorTag tag: The tag code.
    """
    def __init__(self, msg: str, *, tag: ErrorTag) -> None:
        """Raises a TypeCheckedTypeError with the given message and tag.

        :param str msg: The error message.
        :param ErrorTag tag: The tag code.
        """
        message = generate_message(msg, tag)
        super().__init__(message, tag=tag)
