import dataclasses
from itertools import product

import pytest

from permission_manager import BasePermissionManager, PermissionResult, alias
from permission_manager.exceptions import (
    AliasAlreadyExistsError,
    PermissionManagerError,
)

from .managers import (
    ChildPermissionManager,
    ParentPermissionManager,
    SamplePermissionManager,
)


def test_actions():
    permission_manager = SamplePermissionManager()
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


def test_return_value():
    permission_manager = SamplePermissionManager()
    assert permission_manager.has_true_permission() is True
    assert permission_manager.has_false_permission() is False
    assert isinstance(
        permission_manager.has_result_permission(), PermissionResult
    )
    assert isinstance(
        permission_manager.has_denied_permission(), PermissionResult
    )


def test_cache():
    permission_manager = SamplePermissionManager(cache=True)
    permission_manager.has_cache_permission()
    permission_manager.has_cache_permission()
    permission_manager.has_cache_permission()
    assert permission_manager.counter == 1

    permission_manager.cache = False
    permission_manager.has_cache_permission()
    assert permission_manager.counter == 2


def test_context():
    class Instance:
        pass

    class User:
        pass

    instance = Instance()
    user = User()
    permission_manager = SamplePermissionManager(
        user=user,
        instance=instance,
        some_value='test_value',
    )
    assert permission_manager.instance is instance
    assert permission_manager.user is user
    assert permission_manager.context == {'some_value': 'test_value'}


def test_create():
    new_manager = SamplePermissionManager.create(
        'NewManager', new_attr=1, counter=10
    )
    assert new_manager.new_attr == 1
    assert new_manager.counter == 10


def test_has_permission():
    permission_manager = SamplePermissionManager()
    assert permission_manager.has_permission('true') is True

    error = '"SamplePermissionManager" doesn\'t have "wrong_action" action.'
    with pytest.raises(ValueError, match=error):
        permission_manager.has_permission('wrong_action')


def test_parent_positive():
    class Parent:
        pass

    @dataclasses.dataclass
    class Child:
        parent: Parent

    parent = Parent()
    permission_manager = ChildPermissionManager(parent=parent)
    assert permission_manager.parent is parent
    assert permission_manager.has_parent is True

    permission_manager = ChildPermissionManager(instance=Child(parent=parent))
    assert permission_manager.parent is parent
    assert permission_manager.has_parent is True


def test_parent_negative():
    permission_manager = ChildPermissionManager()
    with pytest.raises(PermissionManagerError, match=r'Instance is missing\.'):
        _ = permission_manager.parent
    assert permission_manager.has_parent is False

    permission_manager = ChildPermissionManager(instance=object())
    permission_manager.parent_attr = None
    msg = r'Attribute `parent_attr` is not defined\.'
    with pytest.raises(PermissionManagerError, match=msg):
        _ = permission_manager.parent
    assert permission_manager.has_parent is False


def test_permission_manager_from_context():
    class Parent:
        permission_manager = ParentPermissionManager

    parent = Parent()
    parent_permission_manager = SamplePermissionManager(instance=parent)
    permission_manager = ChildPermissionManager(
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
def test_parent_permission_manager(can_view, can_edit):
    @dataclasses.dataclass
    class Parent:
        can_view: bool
        can_edit: bool

        permission_manager = ParentPermissionManager

    parent = Parent(can_view=can_view, can_edit=can_edit)
    permission_manager = ChildPermissionManager(parent=parent)
    assert permission_manager.parent is parent
    assert permission_manager.has_view_permission() is can_view
    assert permission_manager.has_add_permission() is can_edit


def test_resolve():
    permission_manager = SamplePermissionManager()
    resolved = permission_manager.resolve(
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

    resolved = permission_manager.resolve(actions=('true', 'false'))
    assert resolved == {
        'true': True,
        'false': False,
    }

    resolved = permission_manager.resolve(
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
def test_alias(action, result):
    permission_manager = SamplePermissionManager()

    assert permission_manager.has_permission(action) is result


def test_alias_already_exists_negative():
    msg = (
        r'The alias "alias" is already in use for "has_create_permission" in '
        r'"TestPermissionManager"\.'
    )

    with pytest.raises(AliasAlreadyExistsError, match=msg):

        class TestPermissionManager(BasePermissionManager):
            @alias('alias')
            def has_create_permission(self) -> bool:
                return True

            @alias('alias')
            def has_update_permission(self) -> bool:
                return True
