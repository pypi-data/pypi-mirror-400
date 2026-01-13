"""
Utility decorators for ublkit.

Provides decorators for logging function execution and memory management.
"""

from __future__ import annotations

import gc
from functools import wraps
from time import perf_counter
from typing import Any, Callable, TypeVar

from py_logex import logger

F = TypeVar("F", bound=Callable[..., Any])


def log_execution(func: F) -> F:
    """
    Decorator to log function entry, exit, and execution time.

    Logs:
    - Function entry with full qualified name
    - Execution time on successful completion
    - Error details if function raises an exception

    Optimized: Pre-computes qualified name in closure, uses perf_counter for timing.

    Example:
        @log_execution
        def process_file(path: str) -> dict:
            return {"data": "..."}
    """
    if hasattr(func, "__self__"):
        full_name = f"{func.__self__.__class__.__name__}.{func.__name__}"
    else:
        full_name = func.__name__

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f"Entering: {full_name}")
        start_time = perf_counter()

        try:
            result = func(*args, **kwargs)
            elapsed = perf_counter() - start_time
            logger.debug(f"Exiting: {full_name} (took {elapsed:.4f}s)")
            return result
        except Exception as e:
            elapsed = perf_counter() - start_time
            logger.error(
                f"Failed: {full_name} (took {elapsed:.4f}s) - {type(e).__name__}: {e}"
            )
            raise

    return wrapper  # type: ignore


def memory_cleanup(func: F) -> F:
    """
    Decorator to perform garbage collection after function execution.

    Collects only young generation (fast) after single file processing.
    For production batch processing, use with care - sampling recommended.

    Example:
        @memory_cleanup
        def process_large_batch(files: list) -> dict:
            return {"results": "..."}
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            gc.collect(generation=0)

    return wrapper  # type: ignore
