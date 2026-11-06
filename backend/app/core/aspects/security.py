import inspect
from typing import Any, Callable
import aspectlib


class AccessDeniedError(Exception):
    """Raised when an operation is executed without the required role."""
    pass


def require_role(required_role: str) -> Callable:
    """
    AOP Security Aspect using aspectlib.
    Intercepts execution and validates role constraints before running the target function.
    """
    @aspectlib.Aspect
    def aspect(*args: Any, **kwargs: Any):
        # We need to inspect the target function's arguments
        # In aspectlib, yielding calls the wrapped function
        # We check before yield (equivalent to a 'before' advice)
        
        # Check explicit keyword argument or search in kwargs
        user_role = kwargs.get("user_role") or kwargs.get("role")
        
        # If passed as positional argument, check common conventions or inspect
        if not user_role and len(args) > 1:
            # First arg in a method is 'self', subsequent might be arguments
            # Look for matching role string
            for arg in args[1:]:
                if arg == required_role:
                    user_role = arg
                    break

        if user_role != required_role:
            raise AccessDeniedError(
                f"Access denied: Required role '{required_role}', but received '{user_role}'."
            )

        # Proceed to target execution
        result = yield
        return result

    return aspect