from typing import TYPE_CHECKING, Any, List, Optional

from ..exceptions import FilterValidationError, FilterValueTypeError
from ..schema import FilterSchema
from .operators import FilterOperator

if TYPE_CHECKING:
    pass


class FilterValidator:
    """
    Validates and normalizes filters based on QueryBuilderConfig.

    This class ensures that only allowed filters with allowed operators
    are applied to queries, and validates that value types match operator requirements.
    """

    def __init__(self, config: Optional[Any] = None) -> None:
        """
        Initialize the filter validator.

        Args:
            config: QueryBuilderConfig with allowed filters configuration.
                   If None, no validation is performed (all filters allowed).
        """
        # Import here to avoid circular import
        from ..config import QueryBuilderConfig as _QueryBuilderConfig

        self.config: Optional[_QueryBuilderConfig] = config

    def validate(self, filters: List[FilterSchema]) -> List[FilterSchema]:
        """
        Validate and normalize a list of filters.

        Args:
            filters: List of FilterSchema to validate

        Returns:
            List of validated and normalized FilterSchema

        Raises:
            FilterValidationError: If a filter is invalid and ignore_invalid_errors is False
            FilterValueTypeError: If a filter value type is invalid for the operator
        """
        if not self.config or not self.config.allowed_filters:
            # No validation needed, return filters as-is
            return filters

        validated_filters: List[FilterSchema] = []

        for filter_schema in filters:
            try:
                validated = self._validate_single_filter(filter_schema)
                if validated is not None:
                    validated_filters.append(validated)
            except (FilterValidationError, FilterValueTypeError):
                if not self.config.ignore_invalid_errors:
                    raise
                # Silently ignore invalid filter

        return validated_filters

    def _validate_single_filter(
        self, filter_schema: FilterSchema
    ) -> Optional[FilterSchema]:
        """
        Validate and normalize a single filter.

        Args:
            filter_schema: FilterSchema to validate

        Returns:
            Validated FilterSchema or None if filter should be ignored

        Raises:
            FilterValidationError: If filter is invalid
            FilterValueTypeError: If filter value type is invalid
        """
        if not self.config:
            return filter_schema

        # Check if filter is allowed
        if not self.config.is_filter_allowed(filter_schema.field):
            raise FilterValidationError(
                f"Filter '{filter_schema.field}' is not allowed",
                filter_schema.field,
            )

        # Get the AllowedFilters configuration
        allowed_filter = self.config.get_allowed_filter(filter_schema.field)
        if not allowed_filter:
            # Should not happen if is_filter_allowed returned True, but handle it anyway
            raise FilterValidationError(
                f"Filter '{filter_schema.field}' configuration not found",
                filter_schema.field,
            )

        # Resolve alias to actual field name
        actual_field = allowed_filter.field

        # Normalize operator using AllowedFilters.get_operator()
        # This handles default_operator and operator validation
        normalized_operator = allowed_filter.get_operator(filter_schema.operator)

        # Validate value type according to operator
        self._validate_value_type(
            field=actual_field,
            operator=normalized_operator,
            value=filter_schema.value,
        )

        # Create validated filter schema with resolved field and normalized operator
        return FilterSchema(
            field=actual_field,
            operator=str(normalized_operator),
            value=filter_schema.value,
        )

    def _validate_value_type(
        self, field: str, operator: FilterOperator, value: Any
    ) -> None:
        """
        Validate that the value type is appropriate for the operator.

        Args:
            field: Field name
            operator: FilterOperator to validate against
            value: Value to validate

        Raises:
            FilterValueTypeError: If value type is invalid for the operator
        """
        # Check if operator requires a list
        if operator in FilterOperator.requires_list():
            if not isinstance(value, (list, tuple)):
                raise FilterValueTypeError(
                    f"Operator '{operator}' requires a list/array value, got {type(value).__name__}",
                    field=field,
                    operator=str(operator),
                    value=value,
                )

        # Check if operator requires comparable values (for comparison operators)
        # We do a basic check - actual type validation would require model metadata
        if operator in FilterOperator.requires_comparable():
            # Basic validation: should be numeric or date-like
            # More strict validation can be added later with model metadata
            if isinstance(value, (list, tuple, dict)):
                raise FilterValueTypeError(
                    f"Operator '{operator}' requires a comparable value (number or date), got {type(value).__name__}",
                    field=field,
                    operator=str(operator),
                    value=value,
                )
