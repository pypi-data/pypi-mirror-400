"""
Helpers to manage database sessions.

This module provides simple FastAPI dependencies to get database sessions (async and sync).

These functions are wrappers around the session makers created
by DatabaseFactory to easily integrate them into FastAPI.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker


def get_async_db(
    async_session_maker: async_sessionmaker[AsyncSession],
) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    """
    FastAPI dependency to get an asynchronous session.

    This function creates a FastAPI dependency that automatically manages
    the lifecycle of an asynchronous session (creation, use, closing).

    Args:
        async_session_maker: Session maker asynchronous (created by DatabaseFactory)

    Returns:
        Callable: FastAPI dependency function

    Example:
        >>> from app.crud.database import DatabaseFactory, get_async_db
        >>>
        >>> factory = DatabaseFactory("postgresql://...")
        >>> AsyncSessionLocal = factory.get_async_session_maker()
        >>>
        >>> @router.get("/items")
        >>> async def get_items(
        ...     db: AsyncSession = Depends(get_async_db(AsyncSessionLocal))
        ... ):
        ...     items = await crud_item.get_multi(db)
        ...     return items
    """

    async def _get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    return _get_db


def get_sync_db(
    sync_session_maker: sessionmaker[Session],
) -> Callable[[], Generator[Session, None, None]]:
    """
    FastAPI dependency to get a synchronous session.

    This function creates a FastAPI dependency that automatically manages
    the lifecycle of a synchronous session (creation, use, closing).

    Args:
        sync_session_maker: Session maker synchronous (created by DatabaseFactory)

    Returns:
        Callable: FastAPI dependency function

    Example:
        >>> from app.crud.database import DatabaseFactory, get_sync_db
        >>>
        >>> factory = DatabaseFactory("postgresql://...", use_async=False)
        >>> SessionLocal = factory.get_sync_session_maker()
        >>>
        >>> @router.get("/items")
        >>> def get_items(
        ...     db: Session = Depends(get_sync_db(SessionLocal))
        ... ):
        ...     items = crud_item.get_multi(db)
        ...     return items
    """

    def _get_db() -> Generator[Session, None, None]:
        db = sync_session_maker()
        try:
            yield db
        finally:
            db.close()

    return _get_db
