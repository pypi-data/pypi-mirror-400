"""
Base class for CRUD operations.
"""

import asyncio
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID as UUIDType

from sqlalchemy import Select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi_crud_kit.crud.manager import AsyncCRUDManager, SyncCRUDManager
from fastapi_crud_kit.database.exceptions import NotFoundError, ValidationError
from fastapi_crud_kit.query import (
    FilterSchema,
    PaginatedResponse,
    QueryBuilder,
    QueryBuilderConfig,
    QueryParams,
)

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    def __init__(
        self,
        model: Type[ModelType],
        use_async: bool | None = None,
        query_config: Optional[QueryBuilderConfig] = None,
        default_limit: int = 100,
    ) -> None:
        """
        Initialize CRUD base class.

        Args:
            model: SQLAlchemy model class
            use_async: Whether to use async operations (defaults to True)
            query_config: Optional QueryBuilderConfig for filter validation
            default_limit: Default limit for list() when no pagination is specified
        """
        self.model = model

        if use_async is None:
            use_async = getattr(self, "use_async", True)
        self.use_async = use_async

        self.manager: AsyncCRUDManager | SyncCRUDManager = (
            AsyncCRUDManager() if use_async else SyncCRUDManager()
        )

        # Store query config for filter validation
        self.query_config = query_config

        # Default limit for list() to prevent loading entire database
        self.default_limit = default_limit

        # Detect if model supports soft delete
        self.supports_soft_delete = hasattr(model, "deleted_at")

    def _build_query(
        self,
        query_params: QueryParams,
        include_deleted: bool = False,
        apply_default_limit: bool = False,
    ) -> Select[Any]:
        """
        Build a query from query parameters.

        Filters are validated if a QueryBuilderConfig is provided.

        Args:
            query_params: Query parameters (filters, sort, include, fields)
            include_deleted: If True, include soft-deleted records (only if soft delete is supported)
            apply_default_limit: If True, apply default_limit when no pagination is specified

        Returns:
            Select statement ready to execute
        """
        # Create QueryBuilder with config (validation happens in apply_filters)
        builder = QueryBuilder(self.model, config=self.query_config)
        query = builder.apply(query_params)

        # Add soft delete filter if model supports it and we don't want to include deleted
        if self.supports_soft_delete and not include_deleted:
            # Check if deleted_at filter already exists in the query params
            has_deleted_at_filter = any(
                f.field == "deleted_at" for f in query_params.filters
            )
            if not has_deleted_at_filter:
                # Add filter to exclude soft-deleted records using SQLAlchemy's is_() method
                deleted_at_col = getattr(self.model, "deleted_at", None)
                if deleted_at_col is not None:
                    query = query.where(deleted_at_col.is_(None))

        # Apply default limit if no pagination is specified and apply_default_limit is True
        if apply_default_limit:
            has_pagination = (
                query_params.page is not None
                or query_params.per_page is not None
                or query_params.limit is not None
            )
            if not has_pagination:
                query = query.limit(self.default_limit)

        return query

    def _build_count_query(
        self, query_params: QueryParams, include_deleted: bool = False
    ) -> Select[Any]:
        """
        Build a count query from query parameters (without pagination).

        Args:
            query_params: Query parameters (filters, sort, include, fields)
            include_deleted: If True, include soft-deleted records (only if soft delete is supported)

        Returns:
            Select statement for counting (without limit/offset/pagination)
        """
        # Create a copy of query_params without pagination
        count_params = QueryParams(
            filters=query_params.filters,
            sort=[],  # No need to sort for counting
            include=[],  # No need to include relations for counting
            fields=[],  # No need to select specific fields for counting
            page=None,
            per_page=None,
            limit=None,
            offset=None,
        )

        return self._build_query(count_params, include_deleted=include_deleted)

    async def list(
        self,
        session: Union[AsyncSession, Session],
        query_params: QueryParams,
        include_deleted: bool = False,
    ) -> List[Any]:
        """
        List items matching the query parameters.

        If no pagination is specified, applies a default limit to prevent loading
        the entire database.

        Args:
            session: SQLAlchemy session (AsyncSession or Session)
            query_params: Query parameters (filters, sort, include, fields)
            include_deleted: If True, include soft-deleted records (only if soft delete is supported)

        Returns:
            List of results from the query
        """
        query = self._build_query(
            query_params, include_deleted=include_deleted, apply_default_limit=True
        )
        # Type narrowing: manager methods accept Union[AsyncSession, Session]
        return await self.manager.list(session, query)

    async def list_paginated(
        self,
        session: Union[AsyncSession, Session],
        query_params: QueryParams,
        include_deleted: bool = False,
        default_per_page: int = 20,
    ) -> PaginatedResponse[ModelType]:
        """
        List items with pagination and complete metadata.

        Args:
            session: SQLAlchemy session (AsyncSession or Session)
            query_params: Query parameters (filters, sort, include, fields, pagination)
            include_deleted: If True, include soft-deleted records (only if soft delete is supported)
            default_per_page: Default items per page if not specified

        Returns:
            PaginatedResponse with items and complete pagination metadata

        Raises:
            ValueError: If page is specified without per_page
        """
        # Determine pagination parameters
        if query_params.page is not None:
            # Page-based pagination
            if query_params.per_page is None:
                query_params.per_page = default_per_page
            page = query_params.page
            per_page = query_params.per_page
        elif query_params.limit is not None:
            # Limit/offset pagination - convert to page-based for metadata
            per_page = query_params.limit
            offset = query_params.offset or 0
            page = (offset // per_page) + 1
            # Update query_params to use page-based for consistency
            query_params.page = page
            query_params.per_page = per_page
        else:
            # No pagination specified - use defaults
            page = 1
            per_page = default_per_page
            query_params.page = page
            query_params.per_page = per_page

        # Validate page number
        if page < 1:
            raise ValueError("Page number must be >= 1")

        # Build query with pagination
        query = self._build_query(query_params, include_deleted=include_deleted)

        # Build count query (without pagination)
        count_query = self._build_count_query(
            query_params, include_deleted=include_deleted
        )

        # Execute queries in parallel
        items, total = await asyncio.gather(
            self.manager.list(session, query),
            self.manager.count(session, count_query),
        )

        # Calculate pagination metadata
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )

    def _get_primary_key_field(self, identifier: Any) -> str:
        """
        Determine the primary key field name based on the identifier type and model structure.

        Args:
            identifier: The identifier value (can be int, UUID, or string)

        Returns:
            Field name to use for filtering ('id' or 'uuid')
        """
        # If identifier is a UUID (or UUID string), use 'uuid' field
        if isinstance(identifier, UUIDType) or (
            isinstance(identifier, str)
            and len(identifier) == 36
            and identifier.count("-") == 4
        ):
            # Check if model has uuid field
            if hasattr(self.model, "uuid"):
                return "uuid"

        # Use SQLAlchemy inspector to get the actual primary key
        mapper = inspect(self.model)
        if mapper is not None:
            pk_columns = mapper.primary_key
            if pk_columns is not None and len(pk_columns) > 0:
                # Get the first primary key column name
                return pk_columns[0].name

        # Fallback: try 'id' first, then 'uuid'
        if hasattr(self.model, "id"):
            return "id"
        elif hasattr(self.model, "uuid"):
            return "uuid"

        raise ValueError(
            f"Could not determine primary key field for model {self.model.__name__}"
        )

    async def get(
        self,
        session: Union[AsyncSession, Session],
        id: Any,
        query_params: QueryParams | None = None,
        include_deleted: bool = False,
    ) -> ModelType | None:
        """
        Get a single item by ID.

        Args:
            session: SQLAlchemy session (AsyncSession or Session)
            id: Primary key value (id or uuid depending on model and identifier type)
            query_params: Optional query parameters (for includes, fields)
            include_deleted: If True, include soft-deleted records (only if soft delete is supported)

        Returns:
            Model instance or None if not found
        """
        # Determine the primary key field name based on identifier type
        pk_field = self._get_primary_key_field(id)

        # Build query with id filter
        filters = [FilterSchema(field=pk_field, operator="eq", value=id)]
        if query_params:
            # Merge with existing filters if provided
            filters = filters + query_params.filters
            query_params = QueryParams(
                filters=filters,
                sort=query_params.sort,
                include=query_params.include,
                fields=query_params.fields,
            )
        else:
            query_params = QueryParams(filters=filters)

        query = self._build_query(query_params, include_deleted=include_deleted)
        # Type narrowing: manager methods accept Union[AsyncSession, Session]
        return await self.manager.get(session, query)

    async def create(
        self, session: Union[AsyncSession, Session], obj_in: Dict[str, Any] | Any
    ) -> ModelType:
        """
        Create a new item.

        Args:
            session: SQLAlchemy session (AsyncSession or Session)
            obj_in: Dictionary with data or model instance

        Returns:
            Created model instance

        Raises:
            ValidationError: If the creation data is invalid
        """
        try:
            if isinstance(obj_in, dict):
                obj = self.model(**obj_in)
            else:
                obj = obj_in
        except Exception as e:
            model_name = self.model.__name__
            raise ValidationError(
                f"Failed to create {model_name}: {str(e)}", field=None
            ) from e

        # Type narrowing: manager methods accept Union[AsyncSession, Session]
        return await self.manager.create(session, obj)

    async def update(
        self,
        session: Union[AsyncSession, Session],
        id: Any,
        obj_in: Dict[str, Any] | Any,
    ) -> ModelType:
        """
        Update an existing item.

        Args:
            session: SQLAlchemy session (AsyncSession or Session)
            id: Primary key value (id or uuid depending on model)
            obj_in: Dictionary with data to update or model instance

        Returns:
            Updated model instance

        Raises:
            NotFoundError: If the object with the given id is not found
            ValidationError: If the update data is invalid
        """
        # Get existing object
        db_obj = await self.get(session, id)
        if db_obj is None:
            model_name = self.model.__name__
            raise NotFoundError(model_name, id)

        # Update object
        try:
            if isinstance(obj_in, dict):
                for key, value in obj_in.items():
                    if hasattr(db_obj, key):
                        setattr(db_obj, key, value)
            else:
                # If obj_in is a model instance, copy its attributes
                for key in dir(obj_in):
                    if not key.startswith("_") and hasattr(db_obj, key):
                        value = getattr(obj_in, key)
                        if value is not None:
                            setattr(db_obj, key, value)
        except Exception as e:
            raise ValidationError(f"Failed to update object: {str(e)}") from e

        # Type narrowing: manager methods accept Union[AsyncSession, Session]
        return await self.manager.update(session, db_obj)

    async def delete(
        self, session: Union[AsyncSession, Session], id: Any, hard: bool = False
    ) -> ModelType:
        """
        Delete an item.

        If the model supports soft delete and hard=False (default), performs a soft delete.
        Otherwise, performs a hard delete (permanent removal from database).

        Args:
            session: SQLAlchemy session (AsyncSession or Session)
            id: Primary key value (id or uuid depending on model)
            hard: If True, perform hard delete even if soft delete is supported

        Returns:
            Deleted model instance

        Raises:
            NotFoundError: If the object with the given id is not found
        """
        db_obj = await self.get(session, id)
        if db_obj is None:
            model_name = self.model.__name__
            raise NotFoundError(model_name, id)

        # Perform soft delete if supported and hard=False
        if self.supports_soft_delete and not hard:
            # Use the model's soft_delete method if available
            if hasattr(db_obj, "soft_delete"):
                db_obj.soft_delete()  # type: ignore[attr-defined]
            else:
                # Fallback: set deleted_at directly
                from fastapi_crud_kit.models.mixins import utcnow

                db_obj.deleted_at = utcnow()  # type: ignore[attr-defined,assignment]

            # Type narrowing: manager methods accept Union[AsyncSession, Session]
            return await self.manager.update(session, db_obj)
        else:
            # Hard delete
            # Type narrowing: manager methods accept Union[AsyncSession, Session]
            return await self.manager.delete(session, db_obj)

    async def restore(
        self, session: Union[AsyncSession, Session], id: Any
    ) -> ModelType:
        """
        Restore a soft-deleted item.

        Args:
            session: SQLAlchemy session (AsyncSession or Session)
            id: Primary key value (id or uuid depending on model)

        Returns:
            Restored model instance

        Raises:
            NotFoundError: If the object with the given id is not found
            ValueError: If the model does not support soft delete
        """
        if not self.supports_soft_delete:
            raise ValueError(
                f"Model {self.model.__name__} does not support soft delete"
            )

        # Get object including soft-deleted ones
        db_obj = await self.get(session, id, include_deleted=True)
        if db_obj is None:
            model_name = self.model.__name__
            raise NotFoundError(model_name, id)

        # Use the model's restore method if available
        if hasattr(db_obj, "restore"):
            db_obj.restore()  # type: ignore[attr-defined]
        else:
            # Fallback: set deleted_at to None directly
            db_obj.deleted_at = None  # type: ignore[attr-defined,assignment]

        # Type narrowing: manager methods accept Union[AsyncSession, Session]
        return await self.manager.update(session, db_obj)
