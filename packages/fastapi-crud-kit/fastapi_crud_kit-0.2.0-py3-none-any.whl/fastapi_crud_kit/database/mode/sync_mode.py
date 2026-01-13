"""
Sync implementation of the ModeHandler interface.
"""

import re
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi_crud_kit.database.mode.base import ModeHandler


class SyncModeHandler(ModeHandler):
    """
    Handler to create sync engines and session makers.

    Uses sync drivers (psycopg2, pymysql, sqlite3) and
    sync components of SQLAlchemy.
    """

    # Mapping of database types to their sync drivers
    SYNC_DRIVERS = {
        "postgresql": "psycopg2",
        "mysql": "pymysql",
        "mariadb": "pymysql",
        "sqlite": None,  # SQLite doesn't need an external driver
    }

    def create_engine(
        self, database_url: str, echo: bool = False, pool_pre_ping: bool = True
    ) -> Any:
        """
        Create a sync SQLAlchemy engine.

        Args:
            database_url: Connection URL with sync driver
            echo: If True, display SQL queries
            pool_pre_ping: If True, check connections before use

        Returns:
            Engine: Sync SQLAlchemy engine
        """
        return create_engine(
            database_url,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
        )

    def create_session_maker(self, engine: Any) -> Any:
        """
        Create a sync session maker.

        Args:
            engine: Sync SQLAlchemy engine

        Returns:
            sessionmaker: Sync session maker
        """
        return sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )

    def prepare_database_url(self, base_url: str, database_type: str) -> str:
        """
        Prepare the connection URL with the appropriate sync driver.

        Args:
            base_url: Base URL (ex: "postgresql://user:pass@host/db")
            database_type: Database type (postgresql, mysql, etc.)

        Returns:
            str: URL with the appropriate sync driver

        Raises:
            ValueError: If the sync driver is not available for this database type
        """
        driver = self.SYNC_DRIVERS.get(database_type)

        # SQLite doesn't need a driver
        if database_type == "sqlite":
            return base_url

        if not driver:
            raise ValueError(f"Sync driver not available for {database_type}")

        # If the URL contains a driver, replace it
        if "+" in base_url:
            # Replace the existing driver
            base_url = re.sub(r"^[^:]+://", f"{database_type}://", base_url)
            base_url = re.sub(r"^[^+]+", database_type, base_url)
            return f"{database_type}+{driver}://" + base_url.split("://", 1)[1]
        else:
            # Add the driver
            return base_url.replace(
                f"{database_type}://", f"{database_type}+{driver}://", 1
            )

    def create_all_tables(self, engine: Any, base: Any) -> None:
        """
        Create all tables defined in the models (sync version).

        Args:
            engine: Sync SQLAlchemy engine
            base: Declarative base SQLAlchemy
        """
        base.metadata.create_all(bind=engine)

    def drop_all_tables(self, engine: Any, base: Any) -> None:
        """
        Delete all tables (sync version).

        Args:
            engine: Sync SQLAlchemy engine
            base: Declarative base SQLAlchemy

        Warning:
            This method deletes all data!
        """
        base.metadata.drop_all(bind=engine)
