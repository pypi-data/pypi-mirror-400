"""
Abstract interface for engine handlers (Strategy Pattern).

Defines the contract that all implementations must follow
to create engines and session makers (async and sync).
"""

from abc import ABC, abstractmethod
from typing import Any


class ModeHandler(ABC):
    @abstractmethod
    def create_engine(
        self, database_url: str, echo: bool = False, pool_pre_ping: bool = True
    ) -> Any:
        """
        Create a SQLAlchemy engine.

        Args:
            database_url: Connection URL with the appropriate driver
            echo: If True, display SQL queries
            pool_pre_ping: If True, check connections before use

        Returns:
            Engine or AsyncEngine depending on the handler
        """
        raise NotImplementedError

    @abstractmethod
    def create_session_maker(self, engine: Any) -> Any:
        """
        Create a SQLAlchemy session maker.

        Args:
            engine: Engine SQLAlchemy (created by create_engine)

        Returns:
            sessionmaker or async_sessionmaker depending on the handler
        """
        raise NotImplementedError

    @abstractmethod
    def prepare_database_url(self, base_url: str, database_type: str) -> str:
        """
        Prepare the connection URL with the appropriate driver.

        Args:
            base_url: Base URL (ex: "postgresql://user:pass@host/db")
            database_type: Database type (postgresql, mysql, etc.)

        Returns:
            str: URL with the appropriate driver
        """
        raise NotImplementedError
