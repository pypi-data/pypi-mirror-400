"""
Async implementation of the ModeHandler interface.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fastapi_crud_kit.database.mode.base import ModeHandler


class AsyncModeHandler(ModeHandler):
    """
    Handler to create async engines and session makers.

    Uses async drivers (asyncpg, aiomysql, aiosqlite) and
    async components of SQLAlchemy.
    """

    # Mapping of database types to their async drivers
    ASYNC_DRIVERS = {
        "postgresql": "asyncpg",
        "mysql": "aiomysql",
        "mariadb": "aiomysql",
        "sqlite": "aiosqlite",
    }

    def create_engine(
        self, database_url: str, echo: bool = False, pool_pre_ping: bool = True
    ) -> Any:
        """
        Create an async SQLAlchemy engine.

        Args:
            database_url: Connection URL with async driver
            echo: If True, display SQL queries
            pool_pre_ping: If True, check connections before use

        Returns:
            AsyncEngine: Async SQLAlchemy engine
        """
        return create_async_engine(
            database_url,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
        )

    def create_session_maker(self, engine: Any) -> Any:
        """
        Create an async session maker.

        Args:
            engine: Async SQLAlchemy engine

        Returns:
            async_sessionmaker: Async session maker
        """
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    def prepare_database_url(self, base_url: str, database_type: str) -> str:
        """
        Prepare the connection URL with the appropriate async driver.

        Args:
            base_url: Base URL (ex: "postgresql://user:pass@host/db" or "sqlite+aiosqlite:///./db")
            database_type: Database type (postgresql, mysql, etc.)

        Returns:
            str: URL with the appropriate async driver

        Raises:
            ValueError: If the async driver is not available for this database type
        """
        driver = self.ASYNC_DRIVERS.get(database_type)
        if not driver:
            raise ValueError(f"Async driver not available for {database_type}")

        # Check if URL already has the correct async driver
        expected_prefix = f"{database_type}+{driver}://"
        if base_url.startswith(expected_prefix):
            return base_url

        # If the URL contains a driver (but not the correct one), replace it
        if "+" in base_url:
            # Extract the part after "://"
            parts = base_url.split("://", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid database URL format: {base_url}")
            return f"{database_type}+{driver}://{parts[1]}"
        else:
            # Add the driver
            return base_url.replace(
                f"{database_type}://", f"{database_type}+{driver}://", 1
            )

    async def create_all_tables(self, engine: Any, base: Any) -> None:
        """
        Create all tables defined in the models (async version).

        Args:
            engine: AsyncEngine SQLAlchemy
            base: Declarative base SQLAlchemy
        """
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    async def drop_all_tables(self, engine: Any, base: Any) -> None:
        """
        Delete all tables (async version).

        Args:
            engine: AsyncEngine SQLAlchemy
            base: Declarative base SQLAlchemy

        Warning:
            This method deletes all data!
        """
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)
