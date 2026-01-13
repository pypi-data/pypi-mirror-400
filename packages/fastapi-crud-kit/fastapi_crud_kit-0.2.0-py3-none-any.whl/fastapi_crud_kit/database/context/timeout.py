"""
Timeout context managers for async and sync operations.

This module provides context managers and decorators for adding timeouts
to operations to prevent them from running indefinitely.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import functools
import logging
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Callable

from fastapi_crud_kit.database.context.utils import is_async_function

logger = logging.getLogger(__name__)


class _TimeoutBase:
    """Base class for timeout context managers."""

    def __init__(
        self,
        seconds: float,
        timeout_exception: type[Exception] = TimeoutError,
        log: bool = False,
    ):
        self.seconds = seconds
        self.timeout_exception = timeout_exception
        self.log = log

    def _log_info(self, message: str) -> None:
        """Log an info message if logging is enabled."""
        if self.log:
            logger.info(message)

    def _log_warning(self, message: str) -> None:
        """Log a warning message if logging is enabled."""
        if self.log:
            logger.warning(message)


class TimeoutAsync(AbstractAsyncContextManager, _TimeoutBase):
    """
    Context manager and decorator for adding timeouts to async operations.

    This class can be used both as a context manager and as a decorator.
    It automatically raises a timeout exception if the operation exceeds the time limit.

    Args:
        seconds: Maximum execution time in seconds
        timeout_exception: Exception to raise on timeout (default: TimeoutError)
        log: If True, log timeout operations (default: False)

    Example:
        >>> # As context manager
        >>> async def slow_operation():
        ...     async with TimeoutAsync(seconds=5.0):
        ...         result = await long_running_task()
        ...         return result
        >>>
        >>> # As decorator
        >>> @TimeoutAsync(seconds=5.0)
        ... async def slow_operation():
        ...     result = await long_running_task()
        ...     return result
    """

    def __init__(
        self,
        seconds: float,
        timeout_exception: type[Exception] = TimeoutError,
        log: bool = False,
    ):
        super().__init__(seconds, timeout_exception, log)

    async def __aenter__(self) -> TimeoutAsync:
        """Enter the async context manager."""
        self._log_info(f"Starting timeout context (max {self.seconds}s)")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """Exit the async context manager."""
        # Timeout is handled by asyncio.wait_for in the wrapper
        return None

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allow TimeoutAsync to be used as a decorator.

        When used as a decorator, the function execution is automatically
        limited by the timeout.
        """
        if not is_async_function(func):
            raise TypeError(
                "TimeoutAsync can only be used with async functions. "
                "Use TimeoutSync for sync functions."
            )

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs), timeout=self.seconds
                )
            except asyncio.TimeoutError:
                self._log_warning(
                    f"Function {func.__name__} exceeded timeout of {self.seconds} seconds"
                )
                raise self.timeout_exception(
                    f"Function {func.__name__} exceeded timeout of {self.seconds} seconds"
                )

        return wrapper


class TimeoutSync(AbstractContextManager, _TimeoutBase):
    """
    Context manager and decorator for adding timeouts to sync operations.

    This class can be used both as a context manager and as a decorator.
    It automatically raises a timeout exception if the operation exceeds the time limit.

    Note: For sync functions, this uses ThreadPoolExecutor which has limitations.
    It cannot interrupt blocking operations that are already in progress.

    Args:
        seconds: Maximum execution time in seconds
        timeout_exception: Exception to raise on timeout (default: TimeoutError)
        log: If True, log timeout operations (default: False)

    Example:
        >>> # As context manager
        >>> def long_operation():
        ...     with TimeoutSync(seconds=10.0):
        ...         result = blocking_operation()
        ...         return result
        >>>
        >>> # As decorator
        >>> @TimeoutSync(seconds=10.0, timeout_exception=RuntimeError)
        ... def long_operation():
        ...     result = blocking_operation()
        ...     return result
    """

    def __init__(
        self,
        seconds: float,
        timeout_exception: type[Exception] = TimeoutError,
        log: bool = False,
    ):
        super().__init__(seconds, timeout_exception, log)

    def __enter__(self) -> TimeoutSync:
        """Enter the context manager."""
        self._log_info(f"Starting timeout context (max {self.seconds}s)")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """Exit the context manager."""
        # Timeout is handled by ThreadPoolExecutor in the wrapper
        return None

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allow TimeoutSync to be used as a decorator.

        When used as a decorator, the function execution is automatically
        limited by the timeout.

        Note: This uses ThreadPoolExecutor which cannot interrupt blocking
        operations that are already in progress.
        """
        if is_async_function(func):
            raise TypeError(
                "TimeoutSync can only be used with sync functions. "
                "Use TimeoutAsync for async functions."
            )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=self.seconds)
                except concurrent.futures.TimeoutError:
                    self._log_warning(
                        f"Function {func.__name__} exceeded timeout of {self.seconds} seconds"
                    )
                    raise self.timeout_exception(
                        f"Function {func.__name__} exceeded timeout of {self.seconds} seconds"
                    )

        return wrapper
