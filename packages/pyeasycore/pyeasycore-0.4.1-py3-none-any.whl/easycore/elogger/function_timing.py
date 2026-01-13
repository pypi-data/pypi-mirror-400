# -*- coding: utf-8 -*-
# author: NhanDD3 <hp.duongducnhan@gmail.com>
import functools
import inspect
import logging
import time
from typing import Callable

from .utils import calculate_elapsed_ms


def timing_decorator(func: Callable, logger_name: str = "root") -> Callable:
    """A decorator to measure the execution time of a function."""

    @functools.wraps(func)
    def _decorator(func):
        is_coroutine = inspect.iscoroutinefunction(func)
        logger = logging.getLogger(logger_name)
        func_name = func.__name__
        log_extra = {
            "func_name": func_name,
            "loc": "core1000",
        }

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time_ns()
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed_ms = calculate_elapsed_ms(start_time)
                logger.info(
                    f"Function {func_name} executed in {elapsed_ms}ms",
                    extra={
                        **log_extra,
                        "duration_ms": elapsed_ms,
                    },
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time_ns()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_ms = calculate_elapsed_ms(start_time)
                logger.info(
                    f"Function {func_name} executed in {elapsed_ms}ms",
                    extra={
                        **log_extra,
                        "duration_ms": elapsed_ms,
                    },
                )

        return async_wrapper if is_coroutine else sync_wrapper

    return _decorator
