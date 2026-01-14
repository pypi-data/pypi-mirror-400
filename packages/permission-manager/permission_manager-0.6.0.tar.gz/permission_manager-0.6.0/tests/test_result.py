import pytest

from permission_manager import PermissionResult


@pytest.mark.parametrize('value', [True, False])
def test_value(value):
    result = PermissionResult(value=value)
    assert bool(result) is value
    assert result.message is None


@pytest.mark.parametrize('value', [True, False])
@pytest.mark.parametrize('message', ['test', ['1', '2']])
def test_message(value, message):
    result = PermissionResult(value=value, message=message)
    if not isinstance(message, list):
        message = [message]
    assert result.message == message


@pytest.mark.parametrize(
    ('value', 'message_if_true', 'message', 'expected'),
    [
        (True, True, ['Test'], ['Test']),
        (False, False, ['Test'], ['Test']),
        (True, False, ['Test'], None),
        (False, True, ['Test'], ['Test']),
    ],
)
def test_returned_message(value, message_if_true, message, expected):
    result = PermissionResult(
        value=value, message=message, message_if_true=message_if_true
    )
    assert result.returned_message == expected


@pytest.mark.parametrize('value', [True, False])
@pytest.mark.parametrize(
    ('message', 'expect_message'),
    [
        (None, None),
        ('test string', ['test string']),
        (['test list'], ['test list']),
    ],
)
def test_repr(value, message, expect_message):
    result = PermissionResult(value=value, message=message)
    assert (
        repr(result)
        == f'PermissionResult(value={value}, message={expect_message})'
    )
