from typing import Any, List, Union

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi_crud_kit.database.context import TransactionAsync

from .base import CRUDManager


class AsyncCRUDManager(CRUDManager):
    """
    CRUD manager for asynchronous SQLAlchemy sessions.

    Executes async database operations directly without blocking the event loop.
    Uses context managers for read-only operations and transactions.
    """

    def _validate_session(self, session: Union[AsyncSession, Session]) -> AsyncSession:
        """Validate that session is an AsyncSession."""
        if not isinstance(session, AsyncSession):
            raise TypeError("AsyncCRUDManager requires an AsyncSession, not Session")
        return session

    async def list(
        self, session: Union[AsyncSession, Session], query: Select[Any]
    ) -> List[Any]:
        """Execute async query."""
        session = self._validate_session(session)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get(
        self, session: Union[AsyncSession, Session], query: Select[Any]
    ) -> Any | None:
        """Execute async query and return single result."""
        session = self._validate_session(session)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def count(
        self, session: Union[AsyncSession, Session], query: Select[Any]
    ) -> int:
        """
        Count results of async query.

        Creates a count query from the original query by wrapping it in a subquery.
        This preserves all filters and conditions while removing pagination and ordering.
        """
        from sqlalchemy import func, select

        session = self._validate_session(session)
        # Create a count query from the original query
        # Use subquery to preserve WHERE clauses but remove ORDER BY, LIMIT, OFFSET
        # The query passed here should already be without options/fields for counting
        subquery = query.subquery()
        count_query = select(func.count()).select_from(subquery)
        result = await session.execute(count_query)
        count_value = result.scalar_one()
        return int(count_value) if count_value is not None else 0

    async def _flush_and_refresh(self, session: AsyncSession, obj: Any) -> None:
        """
        Flush changes to database and refresh object to get updated values.

        Args:
            session: AsyncSession instance
            obj: Model instance to flush and refresh
        """
        await session.flush()
        await session.refresh(obj)

    async def create(self, session: Union[AsyncSession, Session], obj: Any) -> Any:
        """Create async with transaction context."""
        session = self._validate_session(session)
        async with TransactionAsync(session, commit=True):
            session.add(obj)
            await self._flush_and_refresh(session, obj)
            return obj

    async def update(self, session: Union[AsyncSession, Session], obj: Any) -> Any:
        """Update async with transaction context."""
        session = self._validate_session(session)
        async with TransactionAsync(session, commit=True):
            await self._flush_and_refresh(session, obj)
            return obj

    async def delete(self, session: Union[AsyncSession, Session], obj: Any) -> Any:
        """Delete async with transaction context."""
        session = self._validate_session(session)
        async with TransactionAsync(session, commit=True):
            await session.delete(obj)
            return obj
