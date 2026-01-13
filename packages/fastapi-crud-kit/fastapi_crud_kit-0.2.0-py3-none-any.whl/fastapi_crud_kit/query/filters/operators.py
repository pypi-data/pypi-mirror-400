from enum import Enum
from typing import Tuple


class FilterOperator(str, Enum):
    """Enumeration of available filter operators."""

    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    LIKE = "like"
    ILIKE = "ilike"
    IN = "in"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def get_all(cls) -> list[str]:
        """Return all operators."""
        return [op.value for op in cls]

    @classmethod
    def from_string(cls, value: str) -> "FilterOperator":
        """Return the operator from a string."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid operator: {value}")

    @classmethod
    def comparison_operators(cls) -> Tuple["FilterOperator", ...]:
        """Return all comparison operators."""
        return (
            cls.EQUAL,
            cls.NOT_EQUAL,
            cls.GREATER_THAN,
            cls.GREATER_THAN_OR_EQUAL,
            cls.LESS_THAN,
            cls.LESS_THAN_OR_EQUAL,
        )

    @classmethod
    def requires_list(cls) -> Tuple["FilterOperator", ...]:
        """Return operators that require a list/array value."""
        return (cls.IN,)

    @classmethod
    def requires_comparable(cls) -> Tuple["FilterOperator", ...]:
        """Return operators that require comparable values (numbers, dates)."""
        return (
            cls.GREATER_THAN,
            cls.GREATER_THAN_OR_EQUAL,
            cls.LESS_THAN,
            cls.LESS_THAN_OR_EQUAL,
        )
