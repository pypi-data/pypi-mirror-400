from typing import TYPE_CHECKING, Any, List, Optional

from ..exceptions import FieldValidationError

if TYPE_CHECKING:
    pass


class FieldValidator:
    """
    Validates field selections based on QueryBuilderConfig.

    This class ensures that only allowed fields are selected in queries.
    """

    def __init__(self, config: Optional[Any] = None) -> None:
        """
        Initialize the field validator.

        Args:
            config: QueryBuilderConfig with allowed fields configuration.
                   If None, no validation is performed (all fields allowed).
        """
        # Import here to avoid circular import
        from ..config import QueryBuilderConfig as _QueryBuilderConfig

        self.config: Optional[_QueryBuilderConfig] = config

    def validate(self, fields: List[str]) -> List[str]:
        """
        Validate and normalize a list of field selections.

        Args:
            fields: List of field names to select

        Returns:
            List of validated field names

        Raises:
            FieldValidationError: If a field is invalid and ignore_invalid_errors is False
        """
        if not self.config or not self.config.allowed_fields:
            # No validation needed, return fields as-is
            return fields

        validated_fields: List[str] = []

        for field in fields:
            try:
                validated = self._validate_single_field(field)
                if validated is not None:
                    validated_fields.append(validated)
            except FieldValidationError:
                if not self.config.ignore_invalid_errors:
                    raise
                # Silently ignore invalid field

        return validated_fields

    def _validate_single_field(self, field: str) -> Optional[str]:
        """
        Validate and normalize a single field selection.

        Args:
            field: Field name to validate

        Returns:
            Validated field name or None if field should be ignored

        Raises:
            FieldValidationError: If field is invalid
        """
        if not self.config:
            return field

        # Check if field is allowed
        if not self.config.is_field_allowed(field):
            raise FieldValidationError(
                f"Field '{field}' is not allowed",
                field,
            )

        # Get the AllowedField configuration
        allowed_field = self.config.get_allowed_field(field)
        if not allowed_field:
            # Should not happen if is_field_allowed returned True, but handle it anyway
            raise FieldValidationError(
                f"Field '{field}' configuration not found",
                field,
            )

        # Resolve alias to actual field name
        # If field is in the allowed_field.fields list, use it; otherwise use the first field
        if field in allowed_field.fields:
            actual_field = field
        else:
            actual_field = allowed_field.field

        return actual_field
