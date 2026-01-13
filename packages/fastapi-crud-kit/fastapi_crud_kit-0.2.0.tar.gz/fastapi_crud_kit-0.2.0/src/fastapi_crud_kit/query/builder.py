from typing import Any, Optional, Type

from sqlalchemy import Select, inspect, select
from sqlalchemy.orm import selectinload

from .config import QueryBuilderConfig
from .fields.validator import FieldValidator
from .filters.validator import FilterValidator
from .include.validator import IncludeValidator
from .schema import FilterSchema, QueryParams
from .sort.validator import SortValidator


class QueryBuilder:
    OPERATOR_MAP = {
        "eq": lambda col, val: col == val,
        "ne": lambda col, val: col != val,
        "lt": lambda col, val: col < val,
        "lte": lambda col, val: col <= val,
        "gt": lambda col, val: col > val,
        "gte": lambda col, val: col >= val,
        "like": lambda col, val: col.like(val),
        "ilike": lambda col, val: col.ilike(val),
        "in": lambda col, val: col.in_(val if isinstance(val, list) else [val]),
    }

    def __init__(
        self, model: Type[Any], config: Optional[QueryBuilderConfig] = None
    ) -> None:
        """
        Initialize QueryBuilder.

        Args:
            model: SQLAlchemy model class
            config: Optional QueryBuilderConfig for filter validation
        """
        self.model = model
        self.config = config
        self.query: Select[Any] = select(model)

    def apply_filters(self, filters: list[FilterSchema]) -> "QueryBuilder":
        """
        Apply filters to the query.

        If a QueryBuilderConfig is provided, filters are validated before application.
        Custom callbacks from AllowedFilters are used if available.

        Args:
            filters: List of FilterSchema to apply

        Returns:
            Self for method chaining
        """
        # Validate filters if config is provided
        if self.config:
            validator = FilterValidator(self.config)
            filters = validator.validate(filters)

        for f in filters:
            # Check if there's a custom callback for this filter
            if self.config:
                allowed_filter = self.config.get_allowed_filter(f.field)
                if allowed_filter and allowed_filter.callback:
                    # Use custom callback: callback(query, value) -> query
                    self.query = allowed_filter.callback(self.query, f.value)
                    continue

            # Use standard operator-based filtering
            col = getattr(self.model, f.field, None)
            if col is None:
                continue

            op = self.OPERATOR_MAP.get(f.operator)
            if not op:
                continue

            self.query = self.query.where(op(col, f.value))
        return self

    def apply_sort(self, sort: list[str]) -> "QueryBuilder":
        """
        Apply sorting to the query.

        If a QueryBuilderConfig is provided, sort fields are validated before application.

        Args:
            sort: List of sort field strings (can include "-" prefix for descending)

        Returns:
            Self for method chaining
        """
        # Validate sorts if config is provided
        if self.config:
            validator = SortValidator(self.config)
            sort = validator.validate(sort)

        for s in sort:
            desc = s.startswith("-")
            field = s[1:] if desc else s

            col = getattr(self.model, field, None)
            if col is None:
                continue

            self.query = self.query.order_by(col.desc() if desc else col.asc())
        return self

    def apply_fields(self, fields: list[str]) -> "QueryBuilder":
        """
        Apply field selection to the query.

        If a QueryBuilderConfig is provided, fields are validated before application.

        Args:
            fields: List of field names to select

        Returns:
            Self for method chaining
        """
        if not fields:
            return self

        # Validate fields if config is provided
        if self.config:
            validator = FieldValidator(self.config)
            fields = validator.validate(fields)

        columns = [getattr(self.model, f) for f in fields if hasattr(self.model, f)]
        if columns:
            self.query = self.query.with_only_columns(*columns)

        return self

    def apply_includes(self, includes: list[str]) -> "QueryBuilder":
        """
        Apply relationship includes to the query.

        If a QueryBuilderConfig is provided, includes are validated before application.

        Args:
            includes: List of relationship names to include

        Returns:
            Self for method chaining
        """
        if not includes:
            return self

        # Validate includes if config is provided
        if self.config:
            validator = IncludeValidator(self.config)
            includes = validator.validate(includes)

        inspector = inspect(self.model)
        relationships = {rel.key: rel for rel in inspector.relationships}

        options = []
        for include in includes:
            if include in relationships:
                options.append(selectinload(getattr(self.model, include)))

        if options:
            self.query = self.query.options(*options)

        return self

    def apply_pagination(
        self, limit: int | None = None, offset: int | None = None
    ) -> "QueryBuilder":
        """
        Apply pagination (limit and offset) to the query.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            Self for method chaining
        """
        if limit is not None:
            self.query = self.query.limit(limit)
        if offset is not None:
            self.query = self.query.offset(offset)
        return self

    def apply(self, params: QueryParams) -> Select[Any]:
        # Calculate limit and offset from page/per_page or use direct limit/offset
        limit = None
        offset = None

        if params.page is not None and params.per_page is not None:
            # Page-based pagination
            offset = (params.page - 1) * params.per_page
            limit = params.per_page
        elif params.limit is not None:
            # Direct limit/offset pagination
            limit = params.limit
            offset = params.offset

        return (
            self.apply_filters(params.filters)
            .apply_sort(params.sort)
            .apply_fields(params.fields)
            .apply_includes(params.include)
            .apply_pagination(limit=limit, offset=offset)
            .query
        )
