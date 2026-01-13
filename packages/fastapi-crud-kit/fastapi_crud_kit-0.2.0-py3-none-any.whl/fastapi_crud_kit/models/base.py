"""
Base model with UUID, timestamps, and soft delete support.

Provides ready-to-use base model classes that include:
- UUID field (as external identifier or primary key)
- Automatic timestamps (created_at, updated_at)
- Soft delete support (deleted_at)
"""

from uuid import uuid4

from sqlalchemy import Column

from fastapi_crud_kit.database.base import Base
from fastapi_crud_kit.models.mixins import (
    GUID,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class BaseModel(PrimaryKeyMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Base model class with UUID (as external ID), timestamps, and soft delete.

    This class combines all the common mixins to provide a complete
    base model that can be used for most database models.

    Features:
    - Auto-increment integer primary key (id) - internal identifier
    - UUID field (uuid) - external/public identifier, NOT primary key
    - Automatic timestamps (created_at, updated_at)
    - Soft delete support (deleted_at)

    All models inheriting from this class will automatically have:
    - An auto-increment integer primary key (id)
    - A UUID field (uuid) for external/public use
    - created_at and updated_at timestamps that are automatically managed
    - deleted_at column for soft delete functionality

    Example:
        >>> from fastapi_crud_kit.models import BaseModel
        >>> from sqlalchemy import Column, String
        >>>
        >>> class User(BaseModel):
        ...     __tablename__ = "users"
        ...     email = Column(String, unique=True, nullable=False)
        ...     name = Column(String, nullable=False)
        >>>
        >>> # User now has:
        >>> # - id (Integer, primary key, auto-increment)
        >>> # - uuid (UUID, unique, for external use)
        >>> # - created_at, updated_at, deleted_at

    Note:
        If you need a model without one of these features, you can:
        1. Inherit directly from Base and use only the mixins you need
        2. Create a custom base class with selected mixins
        3. Use BaseModelWithUUIDPK if you want UUID as primary key instead
    """

    __abstract__ = True


class BaseModelWithUUIDPK(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Base model class with UUID as primary key, timestamps, and soft delete.

    This is an alternative to BaseModel where the UUID is used as the primary key
    instead of an auto-increment integer. Use this when you want UUID as your
    primary identifier.

    Features:
    - UUID primary key (uuid)
    - Automatic timestamps (created_at, updated_at)
    - Soft delete support (deleted_at)

    All models inheriting from this class will automatically have:
    - A UUID primary key (uuid) that is auto-generated
    - created_at and updated_at timestamps that are automatically managed
    - deleted_at column for soft delete functionality

    Example:
        >>> from fastapi_crud_kit.models import BaseModelWithUUIDPK
        >>> from sqlalchemy import Column, String
        >>>
        >>> class User(BaseModelWithUUIDPK):
        ...     __tablename__ = "users"
        ...     email = Column(String, unique=True, nullable=False)
        ...     name = Column(String, nullable=False)
        >>>
        >>> # User now has:
        >>> # - uuid (UUID, primary key)
        >>> # - created_at, updated_at, deleted_at
    """

    __abstract__ = True

    # Override uuid to be primary key
    uuid = Column(
        GUID(),
        primary_key=True,
        default=uuid4,
        nullable=False,
        index=True,
    )
