from permission_manager import (
    PermissionManager,
    PermissionManagerDenied,
    PermissionResult,
    alias,
)


class SamplePermissionManager(PermissionManager):
    counter = 0

    @alias('positive')
    def has_true_permission(self):
        return True

    @alias('negative', 'denial')
    def has_false_permission(self):
        return False

    def has_result_permission(self):
        return PermissionResult()

    def has_result_with_message_permission(self):
        return PermissionResult(message='Test message')

    def has_denied_permission(self):
        raise PermissionManagerDenied

    def has_cache_permission(self):
        self.counter += 1
        return True


class ParentPermissionManager(PermissionManager):
    def has_view_permission(self):
        return self.instance.can_view

    def has_edit_permission(self):
        return self.instance.can_edit


class ChildPermissionManager(PermissionManager):
    parent_attr = 'parent'
    parent_permission_manager: ParentPermissionManager

    def has_view_permission(self):
        return self.parent_permission_manager.has_view_permission()

    def has_add_permission(self):
        return self.parent_permission_manager.has_edit_permission()
