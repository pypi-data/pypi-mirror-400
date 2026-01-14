import dataclasses
from itertools import product

import pytest

from permission_manager import (
    AsyncBasePermissionManager,
    PermissionResult,
    alias,
)
from permission_manager.exceptions import (
    AliasAlreadyExistsError,
    PermissionManagerError,
)

from .async_managers import (
    AsyncChildPermissionManager,
    AsyncParentPermissionManager,
    AsyncSamplePermissionManager,
)


async def test_actions():
    permission_manager = AsyncSamplePermissionManager()
    assert sorted(permission_manager._actions) == sorted(
        [
            'true',
            'false',
            'result',
            'result_with_message',
            'denied',
            'cache',
        ]
    )


async def test_return_value():
    permission_manager = AsyncSamplePermissionManager()
    assert await permission_manager.has_true_permission() is True
    assert await permission_manager.has_false_permission() is False
    assert isinstance(
        await permission_manager.has_result_permission(), PermissionResult
    )
    assert isinstance(
        await permission_manager.has_denied_permission(), PermissionResult
    )


async def test_cache():
    permission_manager = AsyncSamplePermissionManager(cache=True)
    await permission_manager.has_cache_permission()
    await permission_manager.has_cache_permission()
    await permission_manager.has_cache_permission()
    assert permission_manager.counter == 1

    permission_manager.cache = False
    await permission_manager.has_cache_permission()
    assert permission_manager.counter == 2


async def test_context():
    class Instance:
        pass

    class User:
        pass

    instance = Instance()
    user = User()
    permission_manager = AsyncSamplePermissionManager(
        user=user,
        instance=instance,
        some_value='test_value',
    )
    assert permission_manager.instance is instance
    assert permission_manager.user is user
    assert permission_manager.context == {'some_value': 'test_value'}


async def test_create():
    new_manager = AsyncSamplePermissionManager.create(
        'NewManager', new_attr=1, counter=10
    )
    assert new_manager.new_attr == 1
    assert new_manager.counter == 10


async def test_has_permission():
    permission_manager = AsyncSamplePermissionManager()
    assert await permission_manager.has_permission('true') is True

    error = (
        '"AsyncSamplePermissionManager" doesn\'t have "wrong_action" action.'
    )
    with pytest.raises(ValueError, match=error):
        await permission_manager.has_permission('wrong_action')


async def test_parent_positive():
    class Parent:
        pass

    @dataclasses.dataclass
    class Child:
        parent: Parent

    parent = Parent()
    permission_manager = AsyncChildPermissionManager(parent=parent)
    assert permission_manager.parent is parent
    assert permission_manager.has_parent is True

    permission_manager = AsyncChildPermissionManager(
        instance=Child(parent=parent)
    )
    assert permission_manager.parent is parent
    assert permission_manager.has_parent is True


async def test_parent_negative():
    permission_manager = AsyncChildPermissionManager()
    with pytest.raises(PermissionManagerError, match=r'Instance is missing\.'):
        _ = permission_manager.parent
    assert permission_manager.has_parent is False

    permission_manager = AsyncChildPermissionManager(instance=object())
    permission_manager.parent_attr = None
    msg = r'Attribute `parent_attr` is not defined\.'
    with pytest.raises(PermissionManagerError, match=msg):
        _ = permission_manager.parent
    assert permission_manager.has_parent is False


async def test_permission_manager_from_context():
    class Parent:
        permission_manager = AsyncParentPermissionManager

    parent = Parent()
    parent_permission_manager = AsyncSamplePermissionManager(instance=parent)
    permission_manager = AsyncChildPermissionManager(
        parent=parent,
        parent_permission_manager=parent_permission_manager,
    )
    assert (
        permission_manager.parent_permission_manager
        is parent_permission_manager
    )


@pytest.mark.parametrize(
    ('can_view', 'can_edit'), product([True, False], repeat=2)
)
async def test_parent_permission_manager(can_view, can_edit):
    @dataclasses.dataclass
    class Parent:
        can_view: bool
        can_edit: bool

        permission_manager = AsyncParentPermissionManager

    parent = Parent(can_view=can_view, can_edit=can_edit)
    permission_manager = AsyncChildPermissionManager(parent=parent)
    assert permission_manager.parent is parent
    assert await permission_manager.has_view_permission() is can_view
    assert await permission_manager.has_add_permission() is can_edit


async def test_resolve():
    permission_manager = AsyncSamplePermissionManager()
    resolved = await permission_manager.resolve(
        actions=(
            'true',
            'false',
            'result',
            'result_with_message',
            'denied',
            'cache',
        )
    )
    assert resolved == {
        'true': True,
        'false': False,
        'result': False,
        'result_with_message': False,
        'denied': False,
        'cache': True,
    }

    resolved = await permission_manager.resolve(actions=('true', 'false'))
    assert resolved == {
        'true': True,
        'false': False,
    }

    resolved = await permission_manager.resolve(
        actions=('true', 'false', 'result', 'result_with_message'),
        with_messages=True,
    )
    assert resolved == {
        'true': {'allow': True, 'messages': None},
        'false': {'allow': False, 'messages': None},
        'result': {'allow': False, 'messages': None},
        'result_with_message': {'allow': False, 'messages': ['Test message']},
    }


@pytest.mark.parametrize(
    ('action', 'result'),
    [
        ('positive', True),
        ('negative', False),
        ('denial', False),
    ],
)
async def test_alias(action, result):
    permission_manager = AsyncSamplePermissionManager()

    assert await permission_manager.has_permission(action) is result


async def test_alias_already_exists_negative():
    msg = (
        r'The alias "alias" is already in use for "has_create_permission" in '
        r'"TestPermissionManager"\.'
    )

    with pytest.raises(AliasAlreadyExistsError, match=msg):

        class TestPermissionManager(AsyncBasePermissionManager):
            @alias('alias')
            def has_create_permission(self) -> bool:
                return True

            @alias('alias')
            def has_update_permission(self) -> bool:
                return True
