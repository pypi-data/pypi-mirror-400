from typing import TYPE_CHECKING, Any, List, Optional

from ..exceptions import SortValidationError

if TYPE_CHECKING:
    pass


class SortValidator:
    """
    Validates sort fields based on QueryBuilderConfig.

    This class ensures that only allowed sort fields are applied to queries.
    """

    def __init__(self, config: Optional[Any] = None) -> None:
        """
        Initialize the sort validator.

        Args:
            config: QueryBuilderConfig with allowed sorts configuration.
                   If None, no validation is performed (all sorts allowed).
        """
        # Import here to avoid circular import
        from ..config import QueryBuilderConfig as _QueryBuilderConfig

        self.config: Optional[_QueryBuilderConfig] = config

    def validate(self, sort_fields: List[str]) -> List[str]:
        """
        Validate and normalize a list of sort fields.

        Args:
            sort_fields: List of sort field strings (can include "-" prefix for descending)

        Returns:
            List of validated sort field strings

        Raises:
            SortValidationError: If a sort field is invalid and ignore_invalid_errors is False
        """
        if not self.config or not self.config.allowed_sorts:
            # No validation needed, return sorts as-is
            return sort_fields

        validated_sorts: List[str] = []

        for sort_field in sort_fields:
            try:
                validated = self._validate_single_sort(sort_field)
                if validated is not None:
                    validated_sorts.append(validated)
            except SortValidationError:
                if not self.config.ignore_invalid_errors:
                    raise
                # Silently ignore invalid sort

        return validated_sorts

    def _validate_single_sort(self, sort_field: str) -> Optional[str]:
        """
        Validate and normalize a single sort field.

        Args:
            sort_field: Sort field string (can include "-" prefix for descending)

        Returns:
            Validated sort field string or None if sort should be ignored

        Raises:
            SortValidationError: If sort field is invalid
        """
        if not self.config:
            return sort_field

        # Extract field name (remove "-" prefix if present)
        desc = sort_field.startswith("-")
        field_name = sort_field[1:] if desc else sort_field

        # Check if sort is allowed
        if not self.config.is_sort_allowed(field_name):
            raise SortValidationError(
                f"Sort field '{field_name}' is not allowed",
                field_name,
            )

        # Get the AllowedSort configuration
        allowed_sort = self.config.get_allowed_sort(field_name)
        if not allowed_sort:
            # Should not happen if is_sort_allowed returned True, but handle it anyway
            raise SortValidationError(
                f"Sort field '{field_name}' configuration not found",
                field_name,
            )

        # Resolve alias to actual field name
        # If field is in the allowed_sort.fields list, use it; otherwise use the first field
        if field_name in allowed_sort.fields:
            actual_field = field_name
        else:
            actual_field = allowed_sort.field

        # Preserve user's direction (desc prefix) or use default from AllowedSort
        # If user specified direction, use it; otherwise use AllowedSort default
        if desc:
            # User specified descending
            return f"-{actual_field}"
        elif allowed_sort.direction == "desc":
            # User didn't specify, but default is desc
            return f"-{actual_field}"
        else:
            # User didn't specify and default is asc
            return actual_field
