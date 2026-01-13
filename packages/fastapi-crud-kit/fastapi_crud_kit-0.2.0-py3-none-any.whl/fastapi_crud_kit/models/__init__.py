"""
Models module for fastapi-crud-kit.

Provides base model classes and mixins for SQLAlchemy models with:
- Primary keys (auto-increment integer or UUID)
- UUID fields (as external identifiers)
- Automatic timestamps
- Soft delete support
"""

from fastapi_crud_kit.models.base import BaseModel, BaseModelWithUUIDPK
from fastapi_crud_kit.models.mixins import (
    GUID,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)

__all__ = [
    "BaseModel",
    "BaseModelWithUUIDPK",
    "PrimaryKeyMixin",
    "UUIDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "GUID",
]
