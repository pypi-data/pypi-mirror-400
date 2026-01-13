from typing import TYPE_CHECKING, Any, List, Optional

from ..exceptions import IncludeValidationError

if TYPE_CHECKING:
    pass


class IncludeValidator:
    """
    Validates relationship includes based on QueryBuilderConfig.

    This class ensures that only allowed relationships are included in queries.
    """

    def __init__(self, config: Optional[Any] = None) -> None:
        """
        Initialize the include validator.

        Args:
            config: QueryBuilderConfig with allowed includes configuration.
                   If None, no validation is performed (all includes allowed).
        """
        # Import here to avoid circular import
        from ..config import QueryBuilderConfig as _QueryBuilderConfig

        self.config: Optional[_QueryBuilderConfig] = config

    def validate(self, includes: List[str]) -> List[str]:
        """
        Validate and normalize a list of relationship includes.

        Args:
            includes: List of relationship names to include

        Returns:
            List of validated relationship names

        Raises:
            IncludeValidationError: If an include is invalid and ignore_invalid_errors is False
        """
        if not self.config or not self.config.allowed_includes:
            # No validation needed, return includes as-is
            return includes

        validated_includes: List[str] = []

        for include in includes:
            try:
                validated = self._validate_single_include(include)
                if validated is not None:
                    validated_includes.append(validated)
            except IncludeValidationError:
                if not self.config.ignore_invalid_errors:
                    raise
                # Silently ignore invalid include

        return validated_includes

    def _validate_single_include(self, include: str) -> Optional[str]:
        """
        Validate and normalize a single relationship include.

        Args:
            include: Relationship name to validate

        Returns:
            Validated relationship name or None if include should be ignored

        Raises:
            IncludeValidationError: If include is invalid
        """
        if not self.config:
            return include

        # Check if include is allowed
        if not self.config.is_include_allowed(include):
            raise IncludeValidationError(
                f"Include '{include}' is not allowed",
                include,
            )

        # Get the AllowedInclude configuration
        allowed_include = self.config.get_allowed_include(include)
        if not allowed_include:
            # Should not happen if is_include_allowed returned True, but handle it anyway
            raise IncludeValidationError(
                f"Include '{include}' configuration not found",
                include,
            )

        # Resolve alias to actual relationship name
        # If include is in the allowed_include.relationships list, use it; otherwise use the first relationship
        if include in allowed_include.relationships:
            actual_relationship = include
        else:
            actual_relationship = allowed_include.relationship

        return actual_relationship
