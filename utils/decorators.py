"""
Decorators for cross-cutting concerns: logging, timing, error handling.

Usage:
    @log_etl
    def run_pipeline(...):
        ...

    @measure_time
    def expensive_query(...):
        ...
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

from utils.logger import get_logger

F = TypeVar("F", bound=Callable[..., Any])


def log_etl(func: F) -> F:
    """Log entry, exit, and errors for ETL pipeline stages."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        logger.info("START  %s", func.__qualname__)
        try:
            result = func(*args, **kwargs)
            logger.info("FINISH %s (OK)", func.__qualname__)
            return result
        except Exception as exc:
            logger.exception("FAIL   %s — %s", func.__qualname__, exc)
            raise

    return wrapper  # type: ignore[return-value]


def measure_time(func: F) -> F:
    """Log execution time of the decorated function."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start
            logger.debug("%s took %.3f s", func.__qualname__, elapsed)

    return wrapper  # type: ignore[return-value]


def handle_errors(default_return: Any = None) -> Callable[[F], F]:
    """Catch exceptions and return *default_return* instead of raising."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.exception(
                    "Handled error in %s — %s", func.__qualname__, exc
                )
                return default_return

        return wrapper  # type: ignore[return-value]

    return decorator
