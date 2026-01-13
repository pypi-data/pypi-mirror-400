"""
Retry context managers for async and sync operations.

This module provides context managers and decorators for retrying operations
on specific exceptions with configurable backoff strategies.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Callable

from sqlalchemy.exc import (
    DisconnectionError,
    OperationalError,
    StatementError,
)
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from fastapi_crud_kit.database.context.utils import is_async_function

# Common database exceptions that can be retried
RETRYABLE_EXCEPTIONS = (
    OperationalError,
    DisconnectionError,
    StatementError,
    SQLTimeoutError,
    ConnectionError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class _RetryBase:
    """Base class for retry context managers."""

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple[type[Exception], ...] = RETRYABLE_EXCEPTIONS,
        log: bool = False,
    ):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.log = log
        self._current_attempt = 0

    def _log_info(self, message: str) -> None:
        """Log an info message if logging is enabled."""
        if self.log:
            logger.info(message)

    def _log_warning(self, message: str) -> None:
        """Log a warning message if logging is enabled."""
        if self.log:
            logger.warning(message)


class RetryAsync(AbstractAsyncContextManager, _RetryBase):
    """
    Context manager and decorator for retrying async operations.

    This class can be used both as a context manager and as a decorator.
    It automatically retries operations on specific exceptions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)
        backoff: Multiplier for delay after each retry (default: 2.0)
        exceptions: Tuple of exception types to retry on (default: database exceptions)
        log: If True, log retry operations (default: False)

    Example:
        >>> # As context manager
        >>> async def fetch_data():
        ...     async with RetryAsync(max_attempts=3, delay=1.0):
        ...         result = await some_operation()
        ...         return result
        >>>
        >>> # As decorator
        >>> @RetryAsync(max_attempts=5, delay=0.5)
        ... async def fetch_data():
        ...     result = await some_operation()
        ...     return result
    """

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple[type[Exception], ...] = RETRYABLE_EXCEPTIONS,
        log: bool = False,
    ):
        super().__init__(max_attempts, delay, backoff, exceptions, log)

    async def __aenter__(self) -> RetryAsync:
        """Enter the async context manager."""
        self._current_attempt = 0
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """
        Exit the async context manager.

        Note: For retry to work as a context manager, you need to use it
        in a loop. The context manager will suppress retryable exceptions
        and wait before allowing retry.
        """
        if exc_type is None:
            return None  # Success, don't suppress

        # Check if the exception should be retried
        if not isinstance(exc_val, self.exceptions):
            return None  # Don't retry, let exception propagate

        self._current_attempt += 1

        if self._current_attempt < self.max_attempts:
            wait_time = self.delay * (self.backoff ** (self._current_attempt - 1))
            self._log_warning(
                f"Retry attempt {self._current_attempt}/{self.max_attempts} "
                f"after {wait_time}s for {exc_type.__name__}"
            )
            await asyncio.sleep(wait_time)
            return True  # Suppress exception to allow retry
        else:
            # Max attempts reached, let exception propagate
            self._log_warning(
                f"Max retry attempts ({self.max_attempts}) reached for {exc_type.__name__}"
            )
            return None

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allow RetryAsync to be used as a decorator.

        When used as a decorator, the function is automatically retried
        on specific exceptions.
        """
        if not is_async_function(func):
            raise TypeError(
                "RetryAsync can only be used with async functions. "
                "Use RetrySync for sync functions."
            )

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = self.delay
            last_exception: Exception | None = None

            for attempt in range(self.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    if attempt < self.max_attempts - 1:
                        self._log_warning(
                            f"Retry attempt {attempt + 1}/{self.max_attempts} "
                            f"after {current_delay}s for {type(e).__name__}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= self.backoff
                    else:
                        raise

            # This should never be reached, but type checker needs it
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected error in retry logic")

        return wrapper


class RetrySync(AbstractContextManager, _RetryBase):
    """
    Context manager and decorator for retrying sync operations.

    This class can be used both as a context manager and as a decorator.
    It automatically retries operations on specific exceptions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)
        backoff: Multiplier for delay after each retry (default: 2.0)
        exceptions: Tuple of exception types to retry on (default: database exceptions)
        log: If True, log retry operations (default: False)

    Example:
        >>> # As context manager
        >>> def connect_to_db():
        ...     with RetrySync(max_attempts=3, delay=1.0):
        ...         return create_connection()
        >>>
        >>> # As decorator
        >>> @RetrySync(max_attempts=5, delay=0.5)
        ... def connect_to_db():
        ...     return create_connection()
    """

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple[type[Exception], ...] = RETRYABLE_EXCEPTIONS,
        log: bool = False,
    ):
        super().__init__(max_attempts, delay, backoff, exceptions, log)

    def __enter__(self) -> RetrySync:
        """Enter the context manager."""
        self._current_attempt = 0
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """
        Exit the context manager.

        Note: For retry to work as a context manager, you need to use it
        in a loop. The context manager will suppress retryable exceptions
        and wait before allowing retry.
        """
        if exc_type is None:
            return None  # Success, don't suppress

        # Check if the exception should be retried
        if not isinstance(exc_val, self.exceptions):
            return None  # Don't retry, let exception propagate

        self._current_attempt += 1

        if self._current_attempt < self.max_attempts:
            wait_time = self.delay * (self.backoff ** (self._current_attempt - 1))
            self._log_warning(
                f"Retry attempt {self._current_attempt}/{self.max_attempts} "
                f"after {wait_time}s for {exc_type.__name__}"
            )
            time.sleep(wait_time)
            return True  # Suppress exception to allow retry
        else:
            # Max attempts reached, let exception propagate
            self._log_warning(
                f"Max retry attempts ({self.max_attempts}) reached for {exc_type.__name__}"
            )
            return None

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allow RetrySync to be used as a decorator.

        When used as a decorator, the function is automatically retried
        on specific exceptions.
        """
        if is_async_function(func):
            raise TypeError(
                "RetrySync can only be used with sync functions. "
                "Use RetryAsync for async functions."
            )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = self.delay
            last_exception: Exception | None = None

            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    if attempt < self.max_attempts - 1:
                        self._log_warning(
                            f"Retry attempt {attempt + 1}/{self.max_attempts} "
                            f"after {current_delay}s for {type(e).__name__}"
                        )
                        time.sleep(current_delay)
                        current_delay *= self.backoff
                    else:
                        raise

            # This should never be reached, but type checker needs it
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected error in retry logic")

        return wrapper
