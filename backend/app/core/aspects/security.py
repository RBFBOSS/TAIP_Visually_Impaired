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
        user_role = kwargs.get("user_role") or kwargs.get("role")
        
        if not user_role and len(args) > 1:
            for arg in args[1:]:
                if arg == required_role:
                    user_role = arg
                    break

        if user_role != required_role:
            raise AccessDeniedError(
                f"Access denied: Required role '{required_role}', but received '{user_role}'."
            )

        result = yield
        return result

    return aspect