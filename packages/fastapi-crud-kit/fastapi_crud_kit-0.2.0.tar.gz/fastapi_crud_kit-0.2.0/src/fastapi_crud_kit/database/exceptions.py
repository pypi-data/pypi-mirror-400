"""
Custom exceptions for database operations.

This module provides a hierarchy of exceptions for database-related errors
including connections, transactions, isolation levels, and CRUD operations.
"""


class DatabaseError(Exception):
    """Base exception for database-related errors."""

    pass


class TransactionError(DatabaseError):
    """Exception raised for transaction-related errors."""

    pass


class ReadOnlyViolationError(DatabaseError):
    """Exception raised when a write operation is attempted in read-only mode."""

    pass


class IsolationLevelError(DatabaseError):
    """Exception raised for isolation level configuration errors."""

    pass


class ConnectionError(DatabaseError):
    """Exception raised for connection-related errors."""

    pass


class NotFoundError(DatabaseError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: str | int | None = None):
        """
        Initialize NotFoundError.

        Args:
            resource: Name of the resource type (e.g., "User", "Category")
            identifier: Optional identifier that was not found
        """
        self.resource = resource
        self.identifier = identifier
        if identifier is not None:
            message = f"{resource} with id {identifier} not found"
        else:
            message = f"{resource} not found"
        super().__init__(message)


class ValidationError(DatabaseError):
    """Exception raised when data validation fails."""

    def __init__(self, message: str, field: str | None = None):
        """
        Initialize ValidationError.

        Args:
            message: Error message
            field: Optional field name that failed validation
        """
        self.field = field
        super().__init__(message)
