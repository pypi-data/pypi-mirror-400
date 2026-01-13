"""
Read-only context managers for async and sync operations.

This module provides context managers and decorators for enforcing read-only
operations and detecting accidental write operations.
"""

from __future__ import annotations

import functools
import logging
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi_crud_kit.database.context.utils import (
    find_session_in_args,
    find_session_param_by_type,
    is_async_function,
)
from fastapi_crud_kit.database.exceptions import ReadOnlyViolationError

logger = logging.getLogger(__name__)

# Methods that indicate write operations
WRITE_METHODS = {
    "add",
    "add_all",
    "delete",
    "merge",
    "bulk_insert_mappings",
    "bulk_update_mappings",
    "bulk_save_objects",
    "execute",  # Can be used for INSERT/UPDATE/DELETE
    "commit",
    "flush",
}


class _ReadOnlyBase:
    """Base class for read-only context managers."""

    def __init__(
        self,
        session: Session | AsyncSession | None = None,
        strict: bool = True,
        log: bool = False,
        session_param: str | None = None,
    ):
        self.session = session
        self.strict = strict
        self.log = log
        self.session_param = session_param
        self._decorator_mode = session is None
        self._original_methods: dict[str, Any] = {}

    def _log_warning(self, message: str) -> None:
        """Log a warning message if logging is enabled."""
        if self.log:
            logger.warning(message)

    def _check_write_operation(self, method_name: str) -> None:
        """Check if a method is a write operation and raise if strict mode."""
        if method_name in WRITE_METHODS:
            error_msg = (
                f"Write operation '{method_name}' detected in read-only mode. "
                f"Read-only operations should only perform SELECT queries."
            )
            self._log_warning(error_msg)
            if self.strict:
                raise ReadOnlyViolationError(error_msg)

    def _wrap_session_methods(self, session: Session | AsyncSession) -> None:
        """Wrap session methods to detect write operations."""
        for method_name in WRITE_METHODS:
            if hasattr(session, method_name):
                original_method = getattr(session, method_name)
                self._original_methods[method_name] = original_method

                # Create closure to capture method_name and original_method
                def make_wrapper(name: str, original: Any) -> Any:
                    if is_async_function(original):

                        @functools.wraps(original)
                        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                            self._check_write_operation(name)
                            return await original(*args, **kwargs)

                        return async_wrapper
                    else:

                        @functools.wraps(original)
                        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                            self._check_write_operation(name)
                            return original(*args, **kwargs)

                        return sync_wrapper

                setattr(
                    session, method_name, make_wrapper(method_name, original_method)
                )

    def _restore_session_methods(self, session: Session | AsyncSession) -> None:
        """Restore original session methods."""
        for method_name, original_method in self._original_methods.items():
            if hasattr(session, method_name):
                setattr(session, method_name, original_method)
        self._original_methods.clear()


class ReadOnlyAsync(AbstractAsyncContextManager, _ReadOnlyBase):
    """
    Context manager and decorator for enforcing read-only async operations.

    This class can be used both as a context manager and as a decorator.
    It detects and prevents write operations (INSERT, UPDATE, DELETE, etc.)
    in read-only contexts.

    Args:
        session: AsyncSession instance (required for context manager mode)
        strict: If True, raise exception on write operations (default: True)
        log: If True, log write operation attempts (default: False)
        session_param: Parameter name for session injection in decorator mode
            (default: None, auto-detects via type annotation)

    Example:
        >>> # As context manager
        >>> async def get_user(db: AsyncSession, user_id: int):
        ...     async with ReadOnlyAsync(db):
        ...         result = await db.execute(select(User).filter(User.id == user_id))
        ...         return result.scalar_one_or_none()
        >>>
        >>> # As decorator
        >>> @ReadOnlyAsync(strict=True, log=True)
        ... async def get_user(db: AsyncSession, user_id: int):
        ...     result = await db.execute(select(User).filter(User.id == user_id))
        ...     return result.scalar_one_or_none()
    """

    def __init__(
        self,
        session: AsyncSession | None = None,
        strict: bool = True,
        log: bool = False,
        session_param: str | None = None,
    ):
        super().__init__(session, strict, log, session_param)

    async def __aenter__(self) -> AsyncSession:
        """Enter the async context manager."""
        if self.session is None:
            raise ValueError(
                "Session must be provided when using ReadOnlyAsync as context manager"
            )

        self._wrap_session_methods(self.session)
        return self.session  # type: ignore[return-value]

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """Exit the async context manager."""
        if self.session:
            self._restore_session_methods(self.session)
        return None  # Don't suppress exceptions

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allow ReadOnlyAsync to be used as a decorator.

        When used as a decorator, the session is automatically extracted
        from the function arguments and write operations are monitored.
        """
        if not is_async_function(func):
            raise TypeError(
                "ReadOnlyAsync can only be used with async functions. "
                "Use ReadOnlySync for sync functions."
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

            # Wrap session methods to detect write operations
            self._wrap_session_methods(session)

            try:
                return await func(*args, **kwargs)
            finally:
                # Restore original methods
                self._restore_session_methods(session)

        return wrapper


class ReadOnlySync(AbstractContextManager, _ReadOnlyBase):
    """
    Context manager and decorator for enforcing read-only sync operations.

    This class can be used both as a context manager and as a decorator.
    It detects and prevents write operations (INSERT, UPDATE, DELETE, etc.)
    in read-only contexts.

    Args:
        session: Session instance (required for context manager mode)
        strict: If True, raise exception on write operations (default: True)
        log: If True, log write operation attempts (default: False)
        session_param: Parameter name for session injection in decorator mode
            (default: None, auto-detects via type annotation)

    Example:
        >>> # As context manager
        >>> def get_user(db: Session, user_id: int):
        ...     with ReadOnlySync(db):
        ...         return db.query(User).filter(User.id == user_id).first()
        >>>
        >>> # As decorator
        >>> @ReadOnlySync(strict=True, log=True)
        ... def get_user(db: Session, user_id: int):
        ...     return db.query(User).filter(User.id == user_id).first()
    """

    def __init__(
        self,
        session: Session | None = None,
        strict: bool = True,
        log: bool = False,
        session_param: str | None = None,
    ):
        super().__init__(session, strict, log, session_param)

    def __enter__(self) -> Session:
        """Enter the context manager."""
        if self.session is None:
            raise ValueError(
                "Session must be provided when using ReadOnlySync as context manager"
            )

        self._wrap_session_methods(self.session)
        return self.session  # type: ignore[return-value]

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """Exit the context manager."""
        if self.session:
            self._restore_session_methods(self.session)
        return None  # Don't suppress exceptions

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allow ReadOnlySync to be used as a decorator.

        When used as a decorator, the session is automatically extracted
        from the function arguments and write operations are monitored.
        """
        if is_async_function(func):
            raise TypeError(
                "ReadOnlySync can only be used with sync functions. "
                "Use ReadOnlyAsync for async functions."
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

            # Wrap session methods to detect write operations
            self._wrap_session_methods(session)

            try:
                return func(*args, **kwargs)
            finally:
                # Restore original methods
                self._restore_session_methods(session)

        return wrapper
