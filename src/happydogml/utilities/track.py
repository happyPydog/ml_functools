"""Utilities functions."""

import functools
import logging
import time
from typing import Callable, ParamSpec, TypeVar

from happydogml.logging import default_logger

P = ParamSpec("P")
R = TypeVar("R")


def track(
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator generator that logs the input parameters and the execution time of a function in JSON format.

    Args:
        logger (loguru.logger, optional): The logger to use for logging. If None, a default logger will be used.

    Returns:
        Callable[[Callable[P, R]], Callable[P, R]]: A decorator that logs input parameters and execution time.

    Example:
        @track()
        def example_function(x: int, y: int) -> int:
            return x + y

        result = example_function(5, 10)
    """
    logger = logger or default_logger

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time_ns = time.perf_counter_ns()
            log_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }
            try:
                result = func(*args, **kwargs)
                log_data.update({"status": "success", "result": result})
                return result
            except Exception as e:
                log_data.update({"status": "error", "error": str(e)})
                raise
            finally:
                delta_ns = time.perf_counter_ns() - start_time_ns
                delta_sec = delta_ns / 1_000_000_000
                log_data.update(
                    {
                        "execution_time_ns": delta_ns,
                        "execution_time_sec": delta_sec,
                    }
                )
                logger.info(log_data)

        return wrapper

    return decorator
