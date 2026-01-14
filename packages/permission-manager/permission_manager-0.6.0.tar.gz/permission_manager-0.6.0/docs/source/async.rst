==============
Async Managers
==============

The asynchronous versions of permission managers allow for non-blocking
permission checks. They are functionally equivalent to their synchronous
counterparts but are designed to be used with Python's asyncio.

.. code-block:: Python

    from permission_manager import AsyncBasePermissionManager

    class AsyncManager(AsyncBasePermissionManager):
        async def has_create_permission(self) -> bool:
            # Some IO bound operations here
            return True

    async def main():
        manager = AsyncManager()
        result = await manager.has_permission('create')
        print(result)

    import asyncio
    asyncio.run(main())
