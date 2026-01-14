# Changelog

### 0.4.2
- Make the "actions" attribute required in the "resolve" method.

### 0.4.1
- Prevent methods from being decorated twice.

### 0.4.0
- Add the ability to specify multiple aliases for a permission.
- Rename "message_if_false" -> "message_if_true" in PermissionResult.
- Move "get_result_value" from manager to utils.

### 0.3.0
- Get a parent_permission_manager from the `context` in the `PermissionManager` if it's passed.
- Add `message_if_false` that indicating whether to include the `message` when the `value` is False.
- Rename `message` -> `messages` in the `resolve` method if `with_messages` is passed.
- Rename `PermissionManagerException` -> `PermissionManagerError`

### 0.2.0
- Add `alias` decorator
