================
PermissionResult
================

If you want to add the reason for permission denial, you can use
``PermissionResult`` class, which acts like a ``bool``, but also stores
a message:

.. code-block:: Python

    from permission_manager import PermissionResult

    class Manager(BasePermissionManager):
        def has_create_permission(self) -> bool:
            return PermissionResult('Creation is prohibited.')


    Manager().has_permission('create')
    > PermissionResult(value=False, message=['Creation is prohibited.'])


You can pass multiple messages:

.. code-block:: Python

    PermissionResult(['Creation is prohibited.', 'Try later.'])
    > PermissionResult(value=False, message=['Creation is prohibited.', 'Try later.'])


Of course, you can change the value:

.. code-block:: Python

    PermissionResult(
        message='Test message',
        value=True,
    )
    > PermissionResult(value=True, message=['Test message'])


By default, the ``.resolve()`` method of a permission manager only returns
message if the ``value`` is ``False``. However, you can change this behavior,
for example, to provide some hints.:

.. code-block:: Python

    PermissionResult(
        message='Test message',
        value=True,
        message_if_true=True,
    )
