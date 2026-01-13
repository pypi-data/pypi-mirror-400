"""
Handlers for creating engines and session makers (Strategy Pattern).

This module implements the Strategy Pattern to manage the differences between
synchronous and asynchronous operations at the level of engines and sessions.
"""

from .async_mode import AsyncModeHandler
from .base import ModeHandler
from .sync_mode import SyncModeHandler

__all__ = [
    "ModeHandler",
    "AsyncModeHandler",
    "SyncModeHandler",
]
