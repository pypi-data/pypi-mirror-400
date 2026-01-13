"""
FastAPI CRUD Kit

A powerful CRUD toolkit for FastAPI with SQLAlchemy, featuring query building,
filtering, sorting, and field selection with async/sync support.
"""

__version__ = "0.2.0"

# CRUD Operations
from fastapi_crud_kit.crud.base import CRUDBase

# Database
from fastapi_crud_kit.database import (
    ConnectionError,
    DatabaseError,
    DatabaseFactory,
    IsolationLevelError,
    NotFoundError,
    ReadOnlyAsync,
    ReadOnlySync,
    ReadOnlyViolationError,
    RetryAsync,
    RetrySync,
    TimeoutAsync,
    TimeoutSync,
    TransactionAsync,
    TransactionError,
    TransactionSync,
    ValidationError,
    get_async_db,
    get_sync_db,
)

# Models
from fastapi_crud_kit.models import (
    GUID,
    BaseModel,
    BaseModelWithUUIDPK,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)

# Query Building
from fastapi_crud_kit.query import (
    AllowedField,
    AllowedFilters,
    AllowedInclude,
    AllowedSort,
    FieldValidationError,
    FilterOperator,
    FilterSchema,
    FilterValidationError,
    FilterValueTypeError,
    IncludeValidationError,
    PaginatedResponse,
    QueryBuilder,
    QueryBuilderConfig,
    QueryBuilderError,
    QueryParams,
    SortValidationError,
    parse_query_params,
)

__all__ = [
    # Version
    "__version__",
    # CRUD
    "CRUDBase",
    # Models
    "BaseModel",
    "BaseModelWithUUIDPK",
    "PrimaryKeyMixin",
    "UUIDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "GUID",
    # Query Building
    "parse_query_params",
    "QueryParams",
    "FilterSchema",
    "PaginatedResponse",
    "QueryBuilder",
    "QueryBuilderConfig",
    "QueryBuilderError",
    "AllowedFilters",
    "FilterOperator",
    "FilterValidationError",
    "FilterValueTypeError",
    "AllowedSort",
    "SortValidationError",
    "AllowedField",
    "FieldValidationError",
    "AllowedInclude",
    "IncludeValidationError",
    # Database
    "DatabaseFactory",
    "get_async_db",
    "get_sync_db",
    "DatabaseError",
    "ConnectionError",
    "TransactionError",
    "ReadOnlyViolationError",
    "IsolationLevelError",
    "NotFoundError",
    "ValidationError",
    "ReadOnlyAsync",
    "ReadOnlySync",
    "RetryAsync",
    "RetrySync",
    "TimeoutAsync",
    "TimeoutSync",
    "TransactionAsync",
    "TransactionSync",
]
