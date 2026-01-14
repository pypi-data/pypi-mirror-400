from dataclasses import dataclass


@dataclass
class PermissionResult:
    """Dataclass for storing permission value and messages.

    Attributes:
        message (str | list | None): The message associated with the
            permission result. It can be a string, a list of strings, or None.
        value (bool): The boolean value indicating the permission result.
        message_if_true (bool): A flag indicating whether to include the
            message when the value is True.
    """

    message: str | list | None = None
    value: bool = False
    message_if_true: bool = False

    def __post_init__(self) -> None:
        """Ensure the message attribute is a list.

        If the message attribute is not a list, convert it to a list.
        """
        if self.message and not isinstance(self.message, list):
            self.message = [self.message]

    def __bool__(self) -> bool:
        """Return the boolean value of the PermissionResult object.

        Returns:
            bool: The boolean value indicating the permission result.
        """
        return self.value

    def __repr__(self) -> str:
        """Return a string representation of the PermissionResult object.

        Returns:
            str: A string representation of the PermissionResult object.
        """
        return (
            f'PermissionResult(value={self.value!r}, message={self.message!r})'
        )

    @property
    def returned_message(self) -> list | None:
        """Return the message based on the value and message_if_true flag.

        If the value is True and message_if_true is False, return None.
        Otherwise, return the message.

        Returns:
            list | None: The message associated with the permission
                result, or None if the value is True and message_if_true is
                False.
        """
        if self.value and not self.message_if_true:
            return None
        return self.message
