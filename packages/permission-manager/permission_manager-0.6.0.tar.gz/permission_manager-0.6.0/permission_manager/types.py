from typing import TypedDict


class ResolveWithMessageResult(TypedDict):
    """TypedDict for permission resolution results with messages.

    Attributes:
        allow (bool): Indicates whether the permission is granted.
        messages (list[str] | None): List of messages associated with the
            permission check, or None if there are no messages.
    """

    allow: bool
    messages: list[str] | None
