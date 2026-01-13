"""Custom exceptions for query building and filtering."""

from typing import Any


class QueryBuilderError(Exception):
    """Base exception for query builder errors."""

    pass


class FilterValidationError(QueryBuilderError):
    """Exception raised when a filter validation fails."""

    def __init__(self, message: str, field: str) -> None:
        """
        Initialize filter validation error.

        Args:
            message: Error message
            field: Field name that caused the error
        """
        self.field = field
        super().__init__(message)


class FilterValueTypeError(QueryBuilderError):
    """Exception raised when a filter value type is invalid for the operator."""

    def __init__(self, message: str, field: str, operator: str, value: Any) -> None:
        """
        Initialize filter value type error.

        Args:
            message: Error message
            field: Field name
            operator: Operator that was used
            value: Invalid value
        """
        self.field = field
        self.operator = operator
        self.value = value
        super().__init__(message)


class SortValidationError(QueryBuilderError):
    """Exception raised when a sort field validation fails."""

    def __init__(self, message: str, field: str) -> None:
        """
        Initialize sort validation error.

        Args:
            message: Error message
            field: Field name that caused the error
        """
        self.field = field
        super().__init__(message)


class FieldValidationError(QueryBuilderError):
    """Exception raised when a field selection validation fails."""

    def __init__(self, message: str, field: str) -> None:
        """
        Initialize field validation error.

        Args:
            message: Error message
            field: Field name that caused the error
        """
        self.field = field
        super().__init__(message)


class IncludeValidationError(QueryBuilderError):
    """Exception raised when a relationship include validation fails."""

    def __init__(self, message: str, relationship: str) -> None:
        """
        Initialize include validation error.

        Args:
            message: Error message
            relationship: Relationship name that caused the error
        """
        self.relationship = relationship
        super().__init__(message)
