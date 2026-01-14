===============
Getting Started
===============

Let's start with some class:

.. code-block:: Python

    import dataclasses


    @dataclasses.dataclass
    class Post:
        title: str
        content: str
        status: str = 'draft'


Write permission class for it:

.. code-block:: Python

    from permission_manager import BasePermissionManager


    class PostPermissionManager(BasePermissionManager):
        def has_create_permission(self) -> bool:
            return True

        def has_delete_permission(self) -> bool:
            return False


Now we can check permissions:

.. code-block:: Python

    manager = PostPermissionManager()

    manager.has_permission('create')
    # > True

    manager.has_permission('delete')
    # > False


User and instance
-----------------

To check the permissions of a specific instance and for a specific user, you
need to pass arguments to the manager, which will be available as
corresponding attributes.

Let's write example user class and change permissions:

.. code-block:: Python

    @dataclasses.dataclass
    class User:
        username: str


    class PostPermissionManager(BasePermissionManager):
        def has_create_permission(self) -> bool:
            return self.user.username == 'admin'

        def has_update_permission(self) -> bool:
            return self.has_permission('create')

        def has_delete_permission(self) -> bool:
            return self.instance.status == 'draft'


    manager = PostPermissionManager(
        user=User(username='admin'),
        instance=Post(
            title='New post',
            content='Test content',
            status='published',
        )
    )

    manager.has_permission('update')
    # > True

    manager.has_permission('delete')
    # > False
