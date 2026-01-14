from functools import wraps
import inspect


def expose(method: str = "GET"):
    """
    Decorator to expose class methods as REST endpoints.
    Automatically derives the path from the method name and registers it on the router.
    """

    def decorator(func):

        # Attach HTTP method metadata directly to the original function
        func._http_method = method.upper()

        @wraps(func)
        async def wrapper(instance, *args, **kwargs):
            if inspect.iscoroutinefunction(func):
                # Await if it's an async function
                return await func(instance, *args, **kwargs)
            else:
                # Call directly if it's a sync function
                return func(instance, *args, **kwargs)

        return wrapper

    return decorator


# Convenient shortcuts for HTTP methods
expose.GET = expose("GET")
expose.POST = expose("POST")
expose.PUT = expose("PUT")
expose.DELETE = expose("DELETE")
