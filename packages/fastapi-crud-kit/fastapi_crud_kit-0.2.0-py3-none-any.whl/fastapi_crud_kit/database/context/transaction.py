"""
Transaction context managers for async and sync database operations.

This module provides ContextDecorator classes that can be used both
as context managers and as decorators for managing database transactions.
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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi_crud_kit.database.context.utils import (
    find_session_in_args,
    find_session_param_by_type,
    is_async_function,
)
from fastapi_crud_kit.database.exceptions import IsolationLevelError

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


# Valid isolation levels
ISOLATION_LEVELS = {
    "READ UNCOMMITTED",
    "READ COMMITTED",
    "REPEATABLE READ",
    "SERIALIZABLE",
}


class _TransactionBase:
    """Base class for transaction context managers."""

    def __init__(
        self,
        session: Session | AsyncSession | None,
        commit: bool = True,
        rollback_on_error: bool = True,
        retry: int = 0,
        log: bool = False,
        session_param: str | None = None,
        isolation_level: str | None = None,
    ):
        self.session = session
        self.commit = commit
        self.rollback_on_error = rollback_on_error
        self.retry = retry
        self.log = log
        self.session_param = session_param
        self.isolation_level = isolation_level
        self._decorator_mode = session is None

        # Validate isolation level if provided
        if isolation_level is not None:
            isolation_level_upper = isolation_level.upper()
            if isolation_level_upper not in ISOLATION_LEVELS:
                raise IsolationLevelError(
                    f"Invalid isolation level: {isolation_level}. "
                    f"Valid levels are: {', '.join(sorted(ISOLATION_LEVELS))}"
                )
            self.isolation_level = isolation_level_upper

    def _log_info(self, message: str) -> None:
        """Log an info message if logging is enabled."""
        if self.log:
            logger.info(message)

    def _log_warning(self, message: str) -> None:
        """Log a warning message if logging is enabled."""
        if self.log:
            logger.warning(message)


class TransactionAsync(AbstractAsyncContextManager, _TransactionBase):
    """
    Context manager and decorator for async database transactions.

    This class can be used both as a context manager and as a decorator.
    It automatically manages commit, rollback, retry logic, and logging.

    Args:
        session: AsyncSession instance (required for context manager mode)
        commit: If True, commit the transaction on success (default: True)
        rollback_on_error: If True, rollback on exception (default: True)
        retry: Number of retry attempts on failure (default: 0)
        log: If True, log transaction operations (default: False)
        session_param: Parameter name for session injection in decorator mode
            (default: None, auto-detects via type annotation)
        isolation_level: Transaction isolation level. Valid values:
            "READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"
            (default: None, uses database default)

    Example:
        >>> # As context manager
        >>> async def create_user(name: str, db: AsyncSession):
        ...     async with TransactionAsync(db, commit=True, retry=2) as session:
        ...         user = User(name=name)
        ...         session.add(user)
        ...         return user
        >>>
        >>> # As decorator
        >>> @TransactionAsync(commit=True, retry=2, log=True)
        ... async def create_user(db: AsyncSession, name: str):
        ...     user = User(name=name)
        ...     db.add(user)
        ...     return user
    """

    def __init__(
        self,
        session: AsyncSession | None = None,
        commit: bool = True,
        rollback_on_error: bool = True,
        retry: int = 0,
        log: bool = False,
        session_param: str | None = None,
        isolation_level: str | None = None,
    ):
        super().__init__(
            session,
            commit,
            rollback_on_error,
            retry,
            log,
            session_param,
            isolation_level,
        )

    async def __aenter__(self) -> AsyncSession:
        """Enter the async context manager."""
        if self.session is None:
            raise ValueError(
                "Session must be provided when using TransactionAsync as context manager"
            )

        self._log_info("Starting async transaction")

        # Set isolation level if specified
        if self.isolation_level:
            try:
                # For async, we need to use begin() to set isolation level
                # This is done at the connection level
                connection_result = self.session.connection()
                # connection() can return either Connection or Coroutine
                if hasattr(connection_result, "__await__"):
                    connection = await connection_result  # type: ignore[misc]
                else:
                    connection = connection_result  # type: ignore[assignment]
                await connection.execution_options(isolation_level=self.isolation_level)  # type: ignore[misc]
                self._log_info(f"Set isolation level to {self.isolation_level}")
            except Exception as e:
                raise IsolationLevelError(
                    f"Failed to set isolation level {self.isolation_level}: {e}"
                ) from e

        return self.session  # type: ignore[return-value]

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """Exit the async context manager."""
        if exc_type is None:
            # Success
            if self.commit:
                self._log_info("Committing async transaction")
                commit_result = self.session.commit()  # type: ignore[union-attr]
                if hasattr(commit_result, "__await__"):
                    await commit_result  # type: ignore[misc]
        else:
            # Exception occurred
            if self.rollback_on_error:
                self._log_warning(
                    f"Rolling back async transaction due to {exc_type.__name__}"
                )
                rollback_result = self.session.rollback()  # type: ignore[union-attr]
                if hasattr(rollback_result, "__await__"):
                    await rollback_result  # type: ignore[misc]

        return None  # Don't suppress exceptions

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allow TransactionAsync to be used as a decorator.

        When used as a decorator, the session is automatically extracted
        from the function arguments.
        """
        if not is_async_function(func):
            raise TypeError(
                "TransactionAsync can only be used with async functions. "
                "Use TransactionSync for sync functions."
            )

        # Auto-detect session parameter if not specified
        if self.session_param is None:
            self.session_param = find_session_param_by_type(func, AsyncSession)
            if self.session_param is None:
                raise ValueError(
                    "Could not find AsyncSession parameter in function signature. "
                    "Please specify session_param explicitly."
                )

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Find the session in the function arguments
            session = find_session_in_args(
                args, kwargs, func, self.session_param, AsyncSession
            )

            if session is None:
                raise ValueError(
                    f"Session parameter '{self.session_param}' not found in function call"
                )

            # Set isolation level if specified
            if self.isolation_level:
                try:
                    connection_result = session.connection()
                    # connection() can return either Connection or Coroutine
                    if hasattr(connection_result, "__await__"):
                        connection = await connection_result  # type: ignore[misc]
                    else:
                        connection = connection_result  # type: ignore[assignment]
                    await connection.execution_options(
                        isolation_level=self.isolation_level
                    )  # type: ignore[misc]
                    self._log_info(f"Set isolation level to {self.isolation_level}")
                except Exception as e:
                    raise IsolationLevelError(
                        f"Failed to set isolation level {self.isolation_level}: {e}"
                    ) from e

            # Retry logic
            last_exception: Exception | None = None
            for attempt in range(self.retry + 1):
                try:
                    # Execute function and manage transaction
                    self._log_info("Starting async transaction (decorator mode)")

                    result = await func(*args, **kwargs)

                    if self.commit:
                        self._log_info("Committing async transaction")
                        commit_result = session.commit()
                        if hasattr(commit_result, "__await__"):
                            await commit_result  # type: ignore[misc]

                    return result
                except RETRYABLE_EXCEPTIONS as e:
                    last_exception = e
                    if self.rollback_on_error:
                        self._log_warning(
                            f"Rolling back async transaction due to {type(e).__name__}"
                        )
                        rollback_result = session.rollback()
                        if hasattr(rollback_result, "__await__"):
                            await rollback_result  # type: ignore[misc]

                    if attempt < self.retry:
                        wait_time = 2**attempt  # Exponential backoff
                        self._log_warning(
                            f"Retry attempt {attempt + 1}/{self.retry + 1} "
                            f"after {wait_time}s"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                except Exception as e:
                    # Non-retryable exception
                    if self.rollback_on_error:
                        self._log_warning(
                            f"Rolling back async transaction due to {type(e).__name__}"
                        )
                        rollback_result = session.rollback()
                        if hasattr(rollback_result, "__await__"):
                            await rollback_result  # type: ignore[misc]
                    raise

            # This should never be reached, but type checker needs it
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected error in retry logic")

        return wrapper


class TransactionSync(AbstractContextManager, _TransactionBase):
    """
    Context manager and decorator for sync database transactions.

    This class can be used both as a context manager and as a decorator.
    It automatically manages commit, rollback, retry logic, and logging.

    Args:
        session: Session instance (required for context manager mode)
        commit: If True, commit the transaction on success (default: True)
        rollback_on_error: If True, rollback on exception (default: True)
        retry: Number of retry attempts on failure (default: 0)
        log: If True, log transaction operations (default: False)
        session_param: Parameter name for session injection in decorator mode
            (default: None, auto-detects via type annotation)
        isolation_level: Transaction isolation level. Valid values:
            "READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"
            (default: None, uses database default)

    Example:
        >>> # As context manager
        >>> def create_user(name: str, db: Session):
        ...     with TransactionSync(db, commit=True, retry=2) as session:
        ...         user = User(name=name)
        ...         session.add(user)
        ...         return user
        >>>
        >>> # As decorator
        >>> @TransactionSync(commit=True, retry=2, log=True)
        ... def create_user(db: Session, name: str):
        ...     user = User(name=name)
        ...     db.add(user)
        ...     return user
    """

    def __init__(
        self,
        session: Session | None = None,
        commit: bool = True,
        rollback_on_error: bool = True,
        retry: int = 0,
        log: bool = False,
        session_param: str | None = None,
        isolation_level: str | None = None,
    ):
        super().__init__(
            session,
            commit,
            rollback_on_error,
            retry,
            log,
            session_param,
            isolation_level,
        )

    def __enter__(self) -> Session:
        """Enter the context manager."""
        if self.session is None:
            raise ValueError(
                "Session must be provided when using TransactionSync as context manager"
            )

        self._log_info("Starting sync transaction")

        # Set isolation level if specified
        if self.isolation_level:
            try:
                connection = self.session.connection()
                # For sync, connection() always returns Connection directly
                connection = connection.execution_options(  # type: ignore[union-attr]
                    isolation_level=self.isolation_level
                )
                self._log_info(f"Set isolation level to {self.isolation_level}")
            except Exception as e:
                raise IsolationLevelError(
                    f"Failed to set isolation level {self.isolation_level}: {e}"
                ) from e

        return self.session  # type: ignore[return-value]

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """Exit the context manager."""
        if exc_type is None:
            # Success
            if self.commit:
                self._log_info("Committing sync transaction")
                self.session.commit()  # type: ignore[union-attr]
        else:
            # Exception occurred
            if self.rollback_on_error:
                self._log_warning(
                    f"Rolling back sync transaction due to {exc_type.__name__}"
                )
                self.session.rollback()  # type: ignore[union-attr]

        return None  # Don't suppress exceptions

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allow TransactionSync to be used as a decorator.

        When used as a decorator, the session is automatically extracted
        from the function arguments.
        """
        if is_async_function(func):
            raise TypeError(
                "TransactionSync can only be used with sync functions. "
                "Use TransactionAsync for async functions."
            )

        # Auto-detect session parameter if not specified
        if self.session_param is None:
            self.session_param = find_session_param_by_type(func, Session)
            if self.session_param is None:
                raise ValueError(
                    "Could not find Session parameter in function signature. "
                    "Please specify session_param explicitly."
                )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Find the session in the function arguments
            session = find_session_in_args(
                args, kwargs, func, self.session_param, Session
            )

            if session is None:
                raise ValueError(
                    f"Session parameter '{self.session_param}' not found in function call"
                )

            # Set isolation level if specified
            if self.isolation_level:
                try:
                    connection = session.connection()
                    # For sync, connection() always returns Connection directly
                    connection = connection.execution_options(  # type: ignore[union-attr]
                        isolation_level=self.isolation_level
                    )
                    self._log_info(f"Set isolation level to {self.isolation_level}")
                except Exception as e:
                    raise IsolationLevelError(
                        f"Failed to set isolation level {self.isolation_level}: {e}"
                    ) from e

            # Retry logic
            last_exception: Exception | None = None
            for attempt in range(self.retry + 1):
                try:
                    # Execute function and manage transaction
                    self._log_info("Starting sync transaction (decorator mode)")

                    result = func(*args, **kwargs)

                    if self.commit:
                        self._log_info("Committing sync transaction")
                        session.commit()

                    return result
                except RETRYABLE_EXCEPTIONS as e:
                    last_exception = e
                    if self.rollback_on_error:
                        self._log_warning(
                            f"Rolling back sync transaction due to {type(e).__name__}"
                        )
                        session.rollback()

                    if attempt < self.retry:
                        wait_time = 2**attempt  # Exponential backoff
                        self._log_warning(
                            f"Retry attempt {attempt + 1}/{self.retry + 1} "
                            f"after {wait_time}s"
                        )
                        time.sleep(wait_time)
                    else:
                        raise
                except Exception as e:
                    # Non-retryable exception
                    if self.rollback_on_error:
                        self._log_warning(
                            f"Rolling back sync transaction due to {type(e).__name__}"
                        )
                        session.rollback()
                    raise

            # This should never be reached, but type checker needs it
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected error in retry logic")

        return wrapper
