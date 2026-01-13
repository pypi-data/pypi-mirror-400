from typing import Any, Callable, Optional

from fastapi_crud_kit.query.filters.operators import FilterOperator


class AllowedFilters:
    """
    Represents an allowed filter configuration for query building.

    Similar to Spatie Query Builder's AllowedFilter, this class defines
    which fields can be filtered and with which operators.
    """

    allowed_operators: list[FilterOperator] | None

    def __init__(
        self,
        field: str,
        default_operator: FilterOperator | str = FilterOperator.EQUAL,
        allowed_operators: list[FilterOperator] | list[str] | None = None,
        alias: str | None = None,
        callback: Optional[Callable[[Any, Any], Any]] = None,
    ) -> None:
        """
        Initialize an allowed filter.

        Args:
            field: The database field name to filter on
            default_operator: The default operator to use if not specified in URL
            allowed_operators: List of allowed operators. If None, only default_operator is allowed.
                             If empty list, all operators are allowed.
            alias: Alternative name to use in URL (if different from field name)
            callback: Custom callback function for complex filtering logic
        """
        self.field = field
        self.alias = alias or field
        self.callback = callback

        # Normalize default_operator
        if isinstance(default_operator, str):
            try:
                self.default_operator = FilterOperator(default_operator)
            except ValueError:
                self.default_operator = FilterOperator.EQUAL
        else:
            self.default_operator = default_operator

        # Normalize allowed_operators
        if allowed_operators is None:
            # None means only default operator is allowed
            self.allowed_operators = [self.default_operator]
        elif len(allowed_operators) == 0:
            # Empty list means all operators are allowed
            self.allowed_operators = None
        else:
            # Convert strings to FilterOperator enum
            normalized = []
            for op in allowed_operators:
                if isinstance(op, str):
                    try:
                        normalized.append(FilterOperator(op))
                    except ValueError:
                        continue
                else:
                    normalized.append(op)
            self.allowed_operators = (
                normalized if normalized else [self.default_operator]
            )

    def is_operator_allowed(self, operator: FilterOperator | str) -> bool:
        """
        Check if an operator is allowed for this filter.

        Args:
            operator: The operator to check (can be string or enum)

        Returns:
            True if the operator is allowed, False otherwise
        """
        if self.allowed_operators is None:
            return True  # All operators allowed

        # Normalize operator
        if isinstance(operator, str):
            try:
                operator = FilterOperator(operator)
            except ValueError:
                return False

        return operator in self.allowed_operators

    def get_operator(self, operator: Optional[str] = None) -> FilterOperator:
        """
        Get the operator to use, falling back to default if not provided or not allowed.

        Args:
            operator: Optional operator from URL

        Returns:
            The FilterOperator to use
        """
        if operator is None:
            return self.default_operator

        try:
            requested_op = FilterOperator(operator)
            if self.is_operator_allowed(requested_op):
                return requested_op
        except ValueError:
            pass

        return self.default_operator

    @classmethod
    def exact(
        cls,
        field: str,
        alias: Optional[str] = None,
    ) -> "AllowedFilters":
        """
        Create an exact match filter (equals operator only).

        Args:
            field: The database field name
            alias: Alternative name to use in URL

        Returns:
            AllowedFilters instance configured for exact matching
        """
        return cls(
            field=field,
            default_operator=FilterOperator.EQUAL,
            allowed_operators=None,  # Only default operator
            alias=alias,
        )

    @classmethod
    def partial(
        cls,
        field: str,
        alias: Optional[str] = None,
    ) -> "AllowedFilters":
        """
        Create a partial match filter (LIKE operator).

        Args:
            field: The database field name
            alias: Alternative name to use in URL

        Returns:
            AllowedFilters instance configured for partial matching
        """
        return cls(
            field=field,
            default_operator=FilterOperator.LIKE,
            allowed_operators=None,  # Only default operator
            alias=alias,
        )

    @classmethod
    def custom(
        cls,
        field: str,
        callback: Callable[[Any, Any], Any],
        alias: Optional[str] = None,
    ) -> "AllowedFilters":
        """
        Create a custom filter with a callback function.

        Args:
            field: The database field name
            callback: Custom callback function for filtering logic
            alias: Alternative name to use in URL

        Returns:
            AllowedFilters instance with custom callback
        """
        return cls(
            field=field,
            default_operator=FilterOperator.EQUAL,
            allowed_operators=None,
            alias=alias,
            callback=callback,
        )
