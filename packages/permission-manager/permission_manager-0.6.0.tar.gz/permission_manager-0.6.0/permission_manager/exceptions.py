class PermissionManagerError(Exception):
    """Base permission manager exception.

    This is the base class for all exceptions raised by the permission manager.
    """


class PermissionManagerDenied(PermissionManagerError):  # noqa: N818
    """Exception for negative result.

    This exception is raised when a permission check is denied.
    """


class AliasAlreadyExistsError(PermissionManagerError):
    """Exception for duplicate alias.

    This exception is raised when an attempt is made to add an alias that
    already exists.
    """
