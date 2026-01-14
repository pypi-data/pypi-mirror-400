from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from permission_manager import PermissionResult


def get_result_value(
    *,
    value: bool | PermissionResult,
    with_messages: bool = False,
) -> bool | dict:
    """Serialize the result value.

    This function converts the provided value into a boolean or a dictionary
    depending on the `with_messages` flag. If `with_messages` is True, the
    result includes permission messages.

    Args:
        value (bool | PermissionResult): The value to be serialized. It
            can be a boolean, or an instance of `PermissionResult`.
        with_messages (bool): Whether to include messages in the result.
            Defaults to False.

    Returns:
        bool | dict: The serialized result. If `with_messages` is True, the
            result is a dictionary containing 'allow' and 'messages' keys.
            Otherwise, it is a boolean.
    """
    result = bool(value)

    if with_messages:
        result = {
            'allow': result,
            'messages': getattr(value, 'returned_message', None),
        }
    return result
