from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING, Any

from .decorators import wrap_permission
from .exceptions import AliasAlreadyExistsError, PermissionManagerError
from .utils import get_result_value


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from .result import PermissionResult
    from .types import ResolveWithMessageResult


permission_re = re.compile(r'^has_(\w+)_permission$')


class BasePermissionMeta(type):
    """Metaclass for binding permission actions.

    This metaclass collects all permission actions and applies specified
    decorators to them.
    """

    def __new__(cls, *args, **kwargs) -> type:
        """Create a new class and bind actions.

        Returns:
            type: The newly created class.
        """
        new_cls = super().__new__(cls, *args, **kwargs)
        new_cls._actions = {}
        new_cls._aliases = {}
        new_cls.bind_actions()
        return new_cls

    def bind_actions(cls) -> None:
        """Collect all actions and add decorators.

        This method collects all methods that match the permission action
        pattern, applies decorators.
        """
        for attr_name in dir(cls):
            if action_name := permission_re.match(attr_name):
                permission_fn = getattr(cls, attr_name)
                permission_fn = wrap_permission(permission_fn)

                setattr(cls, attr_name, permission_fn)
                cls._actions[action_name.group(1)] = permission_fn

                for alias in getattr(permission_fn, 'aliases', ()):
                    if alias in cls._aliases:
                        msg = (
                            f'The alias "{alias}" is already in use for '
                            f'"{cls._aliases[alias].__name__}" in '
                            f'"{cls.__name__}".'
                        )
                        raise AliasAlreadyExistsError(msg)
                    cls._aliases[alias] = permission_fn


class PermissionMixin:
    """Mixin class for permission logic.

    This class provides common functionality for permission managers.
    """

    def __init__(
        self,
        *,
        user: Any | None = None,
        instance: Any | None = None,
        cache: bool = False,
        **context,
    ) -> None:
        """Initialize the PermissionManager.

        Args:
            user (Any | None): The user for whom permissions are checked.
            instance (Any | None): The instance associated with the
                permissions.
            cache (bool): Whether to cache permission results.
            **context: Additional context for permission checks.
        """
        self.user = user
        self.instance = instance
        self.context = context
        self.cache = cache
        self._cache = {}

    @classmethod
    def create(
        cls: type[BasePermissionManager],
        name: str,
        **type_dict,
    ) -> type:
        """Create a new permission manager class dynamically.

        Args:
            name (str): The name of the new manager class.
            **type_dict: Attributes and methods for the new manager class.

        Returns:
            type: The newly created manager class.
        """
        return type(name, (cls,), type_dict)

    def _get_action(self, action: str) -> Callable:
        if action in self._actions:
            return self._actions[action]
        if action in self._aliases:
            return self._aliases[action]
        raise ValueError(
            f'"{self.__class__.__name__}" doesn\'t have "{action}" action.'
        )


class BasePermissionManager(PermissionMixin, metaclass=BasePermissionMeta):
    """Base permission manager class.

    This class provides basic functionality to manage and check permissions.

    Attributes:
        user (Any | None): The user for whom permissions are checked.
        instance (Any | None): The instance associated with the permissions.
        cache (bool): Whether to cache permission results.
        context (dict): Additional context for permission checks.
    """

    def has_permission(self, action: str) -> bool | PermissionResult:
        """Check if the permission is granted for a specific action.

        Args:
            action (str): The action to check permission for.

        Returns:
            bool: True if the permission is granted, False otherwise.

        Raises:
            ValueError: If the action is not found in the permissions.
        """
        return self._get_action(action)(self)

    def resolve(
        self,
        *,
        actions: Iterable[str],
        with_messages: bool = False,
    ) -> dict[str, bool] | dict[str, ResolveWithMessageResult]:
        """Resolve a list of actions and their permission status.

        Args:
            actions (Iterable[str]): The list of actions to check.
            with_messages (bool): Whether to include messages in the result.

        Returns:
            dict[str, bool] | dict[str, ResolveWithMessageResult]: A dictionary
                with actions as keys and permission status as values. If
                `with_messages` is True, the values include permission status
                and associated messages.
        """
        return {
            action: get_result_value(
                value=self.has_permission(action),
                with_messages=with_messages,
            )
            for action in actions
        }


class ParentMixin:
    """Mixin class with parent checking functionality.

    Attributes:
        parent_attr (str | None): The attribute name to access the parent
            object.
    """

    parent_attr: str | None = None

    @cached_property
    def parent(self) -> Any:
        """Get the parent object.

        Returns:
            Any: The parent object.

        Raises:
            PermissionManagerError: If the parent object cannot be determined.
        """
        if parent := self.context.get('parent'):
            return parent
        return self.get_parent_from_instance()

    def get_parent_from_instance(self) -> Any:
        """Get the parent object from the instance.

        Returns:
            Any: The parent object.

        Raises:
            PermissionManagerError: If the instance or parent attribute is
                missing.
        """
        if not self.instance:
            raise PermissionManagerError('Instance is missing.')

        if not self.parent_attr:
            raise PermissionManagerError(
                'Attribute `parent_attr` is not defined.'
            )

        return getattr(self.instance, self.parent_attr)

    @property
    def has_parent(self) -> bool:
        """Check if a parent exists.

        Returns:
            bool: True if a parent exists, False otherwise.
        """
        try:
            return bool(self.parent)
        except PermissionManagerError:
            return False

    @cached_property
    def parent_permission_manager(
        self,
    ) -> PermissionManager | AsyncPermissionManager:
        """Get the parent permission manager.

        Returns:
            PermissionManager | AsyncPermissionManager: The parent permission
                manager.

        Raises:
            PermissionManagerError: If the parent permission manager cannot be
                determined.
        """
        if from_context := self.context.get('parent_permission_manager'):
            return from_context

        return self.parent.permission_manager(
            user=self.user,
            instance=self.parent,
            context=self.context,
        )


class PermissionManager(ParentMixin, BasePermissionManager):
    """Permission manager class with parent checking functionality."""


class AsyncBasePermissionManager(
    PermissionMixin, metaclass=BasePermissionMeta
):
    """Base async permission manager class."""

    async def has_permission(self, action: str) -> bool:
        """Check if the permission is granted for a specific action.

        Args:
            action (str): The action to check permission for.

        Returns:
            bool: True if the permission is granted, False otherwise.

        Raises:
            ValueError: If the action is not found in the permissions.
        """
        return await self._get_action(action)(self)

    async def resolve(
        self,
        *,
        actions: Iterable[str],
        with_messages: bool = False,
    ) -> dict[str, bool] | dict[str, ResolveWithMessageResult]:
        """Resolve a list of actions and their permission status.

        Args:
            actions (Iterable[str]): The list of actions to check.
            with_messages (bool): Whether to include messages in the result.

        Returns:
            dict[str, bool] | dict[str, ResolveWithMessageResult]: A dictionary
                with actions as keys and permission status as values. If
                `with_messages` is True, the values include permission status
                and associated messages.
        """
        return {
            action: get_result_value(
                value=await self.has_permission(action),
                with_messages=with_messages,
            )
            for action in actions
        }


class AsyncPermissionManager(ParentMixin, AsyncBasePermissionManager):
    """Async permission manager class with parent checking functionality."""
