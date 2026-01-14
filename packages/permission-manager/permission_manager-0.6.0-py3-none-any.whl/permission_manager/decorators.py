import inspect
from collections.abc import Callable
from functools import wraps

from .exceptions import PermissionManagerDenied
from .result import PermissionResult


def wrap_permission(fn: Callable) -> Callable:
    """Wrap a permission method with caching and error handling.

    This decorator-like function detects if the wrapped method is
    synchronous or asynchronous and applies the appropriate logic
    for caching results and catching `PermissionManagerDenied`
    exceptions.

    Args:
        fn: The permission method to be wrapped.

    Returns:
        A wrapped version of the input function (sync or async).
    """
    if inspect.iscoroutinefunction(fn):

        @wraps(fn)
        async def async_wrapper(
            self,
            *args,
            **kwargs,
        ) -> bool | PermissionResult:
            if self.cache and fn.__name__ in self._cache:
                return self._cache[fn.__name__]

            try:
                result = await fn(self, *args, **kwargs)
            except PermissionManagerDenied as e:
                result = PermissionResult(str(e) or None)

            if self.cache:
                self._cache[fn.__name__] = result
            return result

        return async_wrapper

    @wraps(fn)
    def sync_wrapper(self, *args, **kwargs) -> bool | PermissionResult:
        if self.cache and fn.__name__ in self._cache:
            return self._cache[fn.__name__]

        try:
            result = fn(self, *args, **kwargs)
        except PermissionManagerDenied as e:
            result = PermissionResult(str(e) or None)

        if self.cache:
            self._cache[fn.__name__] = result
        return result

    return sync_wrapper


def alias(*names: str) -> Callable:
    """Decorator that adds aliases to a permission function.

    This decorator allows you to define alternative names (aliases) for the
    decorated permission function.

    Args:
        *names (str): The alias name(s) to be added to the permission function.

    Returns:
        Callable: The decorated function.
    """

    def decorator(fn) -> Callable:
        fn.aliases = getattr(fn, 'aliases', set()) | set(names)
        return fn

    return decorator
