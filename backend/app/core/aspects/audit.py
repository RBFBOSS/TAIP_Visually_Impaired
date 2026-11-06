import logging
import time
from typing import Any, Optional
import aspectlib

logger = logging.getLogger("app.audit")
logger.setLevel(logging.INFO)


def audit_action(action_name: Optional[str] = None):
    """
    AOP Audit & Metrics Aspect using aspectlib.
    Acts as an 'around' advice: records execution, elapsed time, and exceptions.
    """
    @aspectlib.Aspect
    def aspect(*args: Any, **kwargs: Any):
        operation = action_name or "GenericOperation"
        entity_id = (
            kwargs.get("cardId")
            or kwargs.get("card_id")
            or kwargs.get("deckId")
            or kwargs.get("deck_id")
            or kwargs.get("id")
        )
        user_role = kwargs.get("user_role", "ANONYMOUS")
        target_info = f"targetId={entity_id}" if entity_id else "scope=general"

        logger.info(f"[AUDIT START] Op: {operation} | {target_info} | Role: {user_role}")
        start_time = time.perf_counter()

        try:
            # Yield passes control to the actual method execution
            result = yield
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"[AUDIT SUCCESS] Op: {operation} | {target_info} | Duration: {elapsed:.4f}s"
            )
            return result
        except Exception as exc:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"[AUDIT FAILURE] Op: {operation} | {target_info} | "
                f"Duration: {elapsed:.4f}s | Error: {type(exc).__name__}: {exc}"
            )
            raise exc

    return aspect