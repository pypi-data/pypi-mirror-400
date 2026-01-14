========
Managers
========

BasePermissionManager
=====================

``BasePermissionManager`` provides base functionality for checking permissions.

Arguments
---------

    * ``user``: Any user class, which will be stored as a manager attribute.
    * ``instance``: Any class instance, which will be stored as a manager
      attribute.
    * ``cache``: A boolean flag, that caches permission results. It's useful if
      you want to collect all permissions results. It reduces calculations
      of permissions if some of them calls another ones. **Don't use it, if
      you don't know what are you doing.**
    * ``**context``: Any arguments you want to pass to manager.


Methods
-------

``has_permission``
~~~~~~~~~~~~~~~~~~

The main method to check permissions.

.. code-block:: Python

    manager.has_permission('create')


``resolve``
~~~~~~~~~~~

The method, which serialize permissions to dictionary.

Arguments:
    * ``actions``: a list of permissions to resolve.
    * ``with_messages``: a flag indicating whether to include the message from
      ``PermissionResult``.

.. code-block:: Python

    from permission_manager import BasePermissionManager, PermissionResult

    class PermissionManager(BasePermissionManager):
        def has_create_permission(self) -> bool:
            return True

        def has_update_permission(self) -> bool:
            return False

        def has_delete_permission(self) -> bool:
            return PermissionResult('Permission denied.')

    manager = PermissionManager()
    manager.resolve(actions=('create', 'update'))
    # > {'create': True, 'update': False}

    manager.resolve(actions=('create', 'update', 'delete'), with_messages=True)
    # > {'create': {'allow': True, 'messages': None},
    #    'delete': {'allow': False, 'messages': ['Permission denied.']},
    #    'update': {'allow': False, 'messages': None}}


PermissionManager
=================

The same as ``BasePermissionManager``, but with additional functionality
to check parent permissions.

Attributes
----------

    * ``parent_attr``: the instance's attribute, where the parent instance is
      stored.

Properties
----------

    * ``parent``: the parent instance, obtained from ``context`` or from
      instance's ``parent_attr`` attribute.
    * ``has_parent``: the property that returns ``True`` if the instance has a
      parent.
    * ``parent_permission_manager``: the parent permission manager, which
      obtained from ``context`` or from instance's ``permission_manager``
      attribute.

Usage
-----

.. code-block:: Python

    import dataclasses

    from permission_manager import PermissionManager

    class PostPermissionManager(PermissionManager):
        def has_update_permission(self) -> bool:
            return self.instance.status == 'draft'


    @dataclasses.dataclass
    class Post:
        title: str
        status: str = 'draft'

        permission_manager = PostPermissionManager

    class ImagePermissionManager(PermissionManager):
        parent_attr = 'post'

        def has_update_permission(self):
            return self.parent_permission_manager.has_permission('update')


    @dataclasses.dataclass
    class Image:
        post: Post
        file: str

    post = Post(title='Test')
    manager = ImagePermissionManager(
        instance=Image(
            post=post,
            file='/path/to/file',
        ),
    )
    manager.has_permission('update')
    # > True

    post.status = 'published'
    manager.has_permission('update')
    # > False
