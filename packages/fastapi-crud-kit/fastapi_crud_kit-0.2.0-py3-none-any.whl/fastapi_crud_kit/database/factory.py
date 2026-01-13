"""
Factory to create and configure SQLAlchemy components.

This factory allows creating engines, session makers and bases
in a database agnostic way (PostgreSQL, MySQL, SQLite, etc.).
"""

from __future__ import annotations

import re
from typing import Any, Optional, Union

from fastapi_crud_kit.database.base import Base
from fastapi_crud_kit.database.mode import AsyncModeHandler, SyncModeHandler


class DatabaseFactory:
    """
    Factory to create SQLAlchemy components according to the database type.

    This class automatically detects the database type from the URL
    and configures the appropriate drivers (asyncpg, aiomysql, aiosqlite, etc.).

    Attributes:
        database_url: Database connection URL
        database_type: Database type (postgresql, mysql, sqlite, etc.)
        use_async: If True (default), use asynchronous mode. If False, use synchronous mode
        base: Declarative base SQLAlchemy (optional). If None, use the default base from the package
        echo: If True, display SQL queries (default: False)
        pool_pre_ping: If True, check connections before use (default: True)

    Example:
        >>> # Asynchronous mode (default)
        >>> factory = DatabaseFactory("postgresql://user:pass@localhost/db")
        >>> engine = factory.get_engine()
        >>> SessionLocal = factory.get_session_maker()
        >>>
        >>> # Synchronous mode
        >>> factory = DatabaseFactory("postgresql://...", use_async=False)
        >>> engine = factory.get_engine()
        >>> SessionLocal = factory.get_session_maker()
    """

    def __init__(
        self,
        database_url: str,
        database_type: Optional[str] = None,
        use_async: bool = True,
        base: Optional[Any] = None,
        echo: bool = False,
        pool_pre_ping: bool = True,
    ):
        """
        Initialize the factory with the database URL.

        Args:
            database_url: Database connection URL (ex: "postgresql://user:pass@host/db")
            database_type: Database type. If None, it will be detected from the URL
            use_async: If True (default), use asynchronous mode. If False, use synchronous mode
            base: Declarative base SQLAlchemy custom. If None, use the default base from the package
            echo: If True, display SQL queries
            pool_pre_ping: If True, check connections before use
        """
        self.database_url = database_url
        self.use_async = use_async
        self.echo = echo
        self.pool_pre_ping = pool_pre_ping

        # Use the provided Base or the default one
        self.base = base if base is not None else Base

        # Detect the database type if not provided
        if database_type is None:
            self.database_type = self._detect_database_type(database_url)
        else:
            self.database_type = database_type.lower()

        # Initialize the handler according to the mode
        # The database type validation will be done by the handler when calling prepare_database_url()
        if self.use_async:
            self.handler: Union[AsyncModeHandler, SyncModeHandler] = AsyncModeHandler()
        else:
            self.handler = SyncModeHandler()

    @staticmethod
    def _detect_database_type(database_url: str) -> str:
        """
        Detect the database type from the URL.

        Args:
            database_url: Database connection URL

        Returns:
            str: Detected database type (postgresql, mysql, mariadb, sqlite)
        """
        # Extract the schema (postgresql://, mysql://, etc.)
        match = re.match(r"^([^:]+)://", database_url)
        if not match:
            raise ValueError(f"Invalid database URL: {database_url}")

        scheme = match.group(1).lower()

        # Clean the schema (remove +driver if present)
        db_type = scheme.split("+")[0]

        # Normalize the variants (postgres → postgresql)
        if db_type == "postgres":
            return "postgresql"

        return db_type

    def get_engine(self) -> Any:
        """
        Create an SQLAlchemy engine according to the configured mode (async or sync).

        Returns:
            AsyncEngine or Engine: SQLAlchemy engine according to use_async
        """
        database_url = self.handler.prepare_database_url(
            self.database_url, self.database_type
        )

        return self.handler.create_engine(
            database_url,
            echo=self.echo,
            pool_pre_ping=self.pool_pre_ping,
        )

    def get_session_maker(self, engine: Optional[Any] = None) -> Any:
        """
        Create a session maker according to the configured mode (async or sync).

        Args:
            engine: Engine (optional, will be created if not provided)

        Returns:
            async_sessionmaker or sessionmaker: Session maker according to use_async
        """
        if engine is None:
            engine = self.get_engine()

        return self.handler.create_session_maker(engine)

    def get_base(self) -> Any:
        """
        Return the declarative base SQLAlchemy.

        This base must be used by all models to ensure consistency and allow migrations.

        If a custom Base has been provided to the constructor, it will be returned.
        Otherwise, the default base from the package will be used.

        Returns:
            DeclarativeMeta: Declarative base SQLAlchemy
        """
        return self.base

    def create_all_tables(self, engine: Optional[Any] = None) -> None:
        """
        Create all tables defined in the models (sync mode only).

        Args:
            engine: Engine SQLAlchemy (optional, will be created if not provided)

        Raises:
            ValueError: If use_async=True, use create_all_tables_async() instead
        """
        if self.use_async:
            raise ValueError(
                "For async mode, use create_all_tables_async() instead. "
                "Or create the factory with use_async=False to use this method."
            )

        if engine is None:
            engine = self.get_engine()

        # Type narrowing: we know it's SyncModeHandler because use_async=False
        assert isinstance(self.handler, SyncModeHandler)
        self.handler.create_all_tables(engine, self.base)

    async def create_all_tables_async(self, engine: Optional[Any] = None) -> None:
        """
        Create all tables defined in the models (async mode only).

        Args:
            engine: Engine async (optional, will be created if not provided)

        Raises:
            ValueError: If use_async=False, use create_all_tables() instead
        """
        if not self.use_async:
            raise ValueError(
                "For sync mode, use create_all_tables() instead. "
                "Or create the factory with use_async=True to use this method."
            )

        if engine is None:
            engine = self.get_engine()

        # Type narrowing: we know it's AsyncModeHandler because use_async=True
        assert isinstance(self.handler, AsyncModeHandler)
        await self.handler.create_all_tables(engine, self.base)

    def drop_all_tables(self, engine: Optional[Any] = None) -> None:
        """
        Delete all tables (sync mode only).

        Args:
            engine: Engine SQLAlchemy (optional, will be created if not provided)

        Warning:
            This method deletes all data!

        Raises:
            ValueError: If use_async=True, use drop_all_tables_async() instead
        """
        if self.use_async:
            raise ValueError(
                "For async mode, use drop_all_tables_async() instead. "
                "Or create the factory with use_async=False to use this method."
            )

        if engine is None:
            engine = self.get_engine()

        # Type narrowing: we know it's SyncModeHandler because use_async=False
        assert isinstance(self.handler, SyncModeHandler)
        self.handler.drop_all_tables(engine, self.base)

    async def drop_all_tables_async(self, engine: Optional[Any] = None) -> None:
        """
        Delete all tables (async mode only).

        Args:
            engine: Engine async (optional, will be created if not provided)

        Warning:
            This method deletes all data!

        Raises:
            ValueError: If use_async=False, use drop_all_tables() instead
        """
        if not self.use_async:
            raise ValueError(
                "For sync mode, use drop_all_tables() instead. "
                "Or create the factory with use_async=True to use this method."
            )

        if engine is None:
            engine = self.get_engine()

        # Type narrowing: we know it's AsyncModeHandler because use_async=True
        assert isinstance(self.handler, AsyncModeHandler)
        await self.handler.drop_all_tables(engine, self.base)

    @classmethod
    def from_settings(
        cls,
        settings: Any,
        use_async: bool = True,
        base: Optional[Any] = None,
        echo: bool = False,
        pool_pre_ping: bool = True,
    ) -> DatabaseFactory:
        """
        Create a factory from a settings object.

        The settings object must have the attributes:
        - DATABASE_URL: Database connection URL
        - DATABASE_TYPE: Database type (optional)

        Args:
            settings: Settings object with DATABASE_URL and optionally DATABASE_TYPE
            use_async: If True (default), use asynchronous mode. If False, use synchronous mode
            base: Declarative base SQLAlchemy custom (optional)
            echo: If True, display SQL queries
            pool_pre_ping: If True, check connections before use

        Returns:
            DatabaseFactory: Configured factory instance

        Example:
            >>> from app.core.config import settings
            >>> # Async mode (default)
            >>> factory = DatabaseFactory.from_settings(settings)
            >>>
            >>> # Mode sync
            >>> factory = DatabaseFactory.from_settings(settings, use_async=False)
            >>>
            >>> # With a custom Base
            >>> from sqlalchemy.ext.declarative import declarative_base
            >>> my_base = declarative_base()
            >>> factory = DatabaseFactory.from_settings(settings, base=my_base)
        """
        database_url = getattr(settings, "DATABASE_URL", None)
        if not database_url:
            raise ValueError("settings must have a DATABASE_URL attribute")

        database_type = getattr(settings, "DATABASE_TYPE", None)

        return cls(
            database_url=database_url,
            database_type=database_type,
            use_async=use_async,
            base=base,
            echo=echo,
            pool_pre_ping=pool_pre_ping,
        )
