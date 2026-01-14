from permission_manager import (
    AsyncPermissionManager,
    PermissionManagerDenied,
    PermissionResult,
    alias,
)


class AsyncSamplePermissionManager(AsyncPermissionManager):
    counter = 0

    @alias('positive')
    async def has_true_permission(self):
        return True

    @alias('negative', 'denial')
    async def has_false_permission(self):
        return False

    async def has_result_permission(self):
        return PermissionResult()

    async def has_result_with_message_permission(self):
        return PermissionResult(message='Test message')

    async def has_denied_permission(self):
        raise PermissionManagerDenied

    async def has_cache_permission(self):
        self.counter += 1
        return True


class AsyncParentPermissionManager(AsyncPermissionManager):
    async def has_view_permission(self):
        return self.instance.can_view

    async def has_edit_permission(self):
        return self.instance.can_edit


class AsyncChildPermissionManager(AsyncPermissionManager):
    parent_attr = 'parent'
    parent_permission_manager: AsyncParentPermissionManager

    async def has_view_permission(self):
        return await self.parent_permission_manager.has_view_permission()

    async def has_add_permission(self):
        return await self.parent_permission_manager.has_edit_permission()
