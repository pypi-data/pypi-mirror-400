from __future__ import annotations

import asyncio
from typing import Any, List, Union

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi_crud_kit.database.context import TransactionSync

from .base import CRUDManager


class SyncCRUDManager(CRUDManager):
    """
    CRUD manager for synchronous SQLAlchemy sessions.

    Executes sync database operations in a thread pool to avoid blocking
    the event loop when used in async contexts.
    Uses context managers for read-only operations and transactions.
    """

    async def list(
        self, session: Union[AsyncSession, Session], query: Select[Any]
    ) -> List[Any]:
        """Execute sync query in thread pool with read-only context."""
        if not isinstance(session, Session):
            raise TypeError("SyncCRUDManager requires a Session, not AsyncSession")
        return await asyncio.to_thread(self._execute_sync, session, query)

    async def get(
        self, session: Union[AsyncSession, Session], query: Select[Any]
    ) -> Any | None:
        """Execute sync query and return single result in thread pool with read-only context."""
        if not isinstance(session, Session):
            raise TypeError("SyncCRUDManager requires a Session, not AsyncSession")
        return await asyncio.to_thread(self._get_sync, session, query)

    async def create(self, session: Union[AsyncSession, Session], obj: Any) -> Any:
        """Create sync in thread pool with transaction context."""
        if not isinstance(session, Session):
            raise TypeError("SyncCRUDManager requires a Session, not AsyncSession")
        return await asyncio.to_thread(self._create_sync, session, obj)

    async def update(self, session: Union[AsyncSession, Session], obj: Any) -> Any:
        """Update sync in thread pool with transaction context."""
        if not isinstance(session, Session):
            raise TypeError("SyncCRUDManager requires a Session, not AsyncSession")
        return await asyncio.to_thread(self._update_sync, session, obj)

    async def delete(self, session: Union[AsyncSession, Session], obj: Any) -> Any:
        """Delete sync in thread pool with transaction context."""
        if not isinstance(session, Session):
            raise TypeError("SyncCRUDManager requires a Session, not AsyncSession")
        return await asyncio.to_thread(self._delete_sync, session, obj)

    def _execute_sync(self, session: Session, query: Select[Any]) -> List[Any]:
        """
        Private method to execute a synchronous database query.

        Args:
            session: Synchronous SQLAlchemy session
            query: Select statement to execute

        Returns:
            List of results from the query
        """
        # No need for ReadOnlySync here - we're already using Select statements
        result = session.execute(query)
        return list(result.scalars().all())

    def _get_sync(self, session: Session, query: Select[Any]) -> Any:
        """Private method to get a single result."""
        # No need for ReadOnlySync here - we're already using Select statements
        result = session.execute(query)
        return result.scalar_one_or_none()

    async def count(
        self, session: Union[AsyncSession, Session], query: Select[Any]
    ) -> int:
        """Count results of sync query."""

        if not isinstance(session, Session):
            raise TypeError("SyncCRUDManager requires a Session, not AsyncSession")
        return await asyncio.to_thread(self._count_sync, session, query)

    def _count_sync(self, session: Session, query: Select[Any]) -> int:
        """
        Private method to count results.

        Creates a count query from the original query by wrapping it in a subquery.
        This preserves all filters and conditions while removing pagination and ordering.
        """
        from sqlalchemy import func, select

        # Create a count query from the original query
        # Use subquery to preserve WHERE clauses but remove ORDER BY, LIMIT, OFFSET
        # The query passed here should already be without options/fields for counting
        subquery = query.subquery()
        count_query = select(func.count()).select_from(subquery)
        result = session.execute(count_query)
        count_value = result.scalar_one()
        return int(count_value) if count_value is not None else 0

    def _flush_and_refresh(self, session: Session, obj: Any) -> None:
        """
        Flush changes to database and refresh object to get updated values.

        Args:
            session: Session instance
            obj: Model instance to flush and refresh
        """
        session.flush()
        session.refresh(obj)

    def _create_sync(self, session: Session, obj: Any) -> Any:
        """Private method to create a record with transaction context."""
        with TransactionSync(session, commit=True):
            session.add(obj)
            self._flush_and_refresh(session, obj)
            return obj

    def _update_sync(self, session: Session, obj: Any) -> Any:
        """Private method to update a record with transaction context."""
        with TransactionSync(session, commit=True):
            self._flush_and_refresh(session, obj)
            return obj

    def _delete_sync(self, session: Session, obj: Any) -> Any:
        """Private method to delete a record with transaction context."""
        with TransactionSync(session, commit=True):
            session.delete(obj)
            return obj
