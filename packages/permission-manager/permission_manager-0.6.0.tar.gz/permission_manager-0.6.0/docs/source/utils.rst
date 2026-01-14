=====
Utils
=====

Alias decorator
---------------

The decorator that add aliases to permissions.

.. code-block:: Python

    from permission_manager import BasePermissionManager
    from permission_manager.decorators import alias

    class PermissionManager(BasePermissionManager):
        @alias('update', 'delete')
        def has_create_permission(self) -> bool:
            return True

    manager = PermissionManager()
    manager.has_permission('create')
    > True
    manager.has_permission('update')
    > True
    manager.has_permission('delete')
    > True
