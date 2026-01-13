import re
from typing import Any, List, Mapping, Union

from ..schema import FilterSchema
from ..utils import split_comma_separated
from .operators import FilterOperator

FILTER_REGEX = re.compile(r"^filter\[(?P<field>[^\]]+)\](?:\[(?P<operator>[^\]]+)\])?$")


def parse_filters(
    query_params: Mapping[str, Union[str, List[str]]],
) -> List[FilterSchema]:
    """
    Parse filter parameters from query string.

    Supports multiple formats:
    - filter[field]=value (defaults to eq operator)
    - filter[field][operator]=value
    - filter[field]=value1&filter[field]=value2 (repeated keys, becomes list)
    - filter[field][]=value1&filter[field][]=value2 (array format)
    - filter[field][in]=value1,value2 (comma-separated for IN operator)

    Args:
        query_params: Query parameters mapping (can contain strings or lists)

    Returns:
        List of FilterSchema objects
    """
    filters: list[FilterSchema] = []
    processed_keys: set[str] = set()

    for key, value in query_params.items():
        # Skip if already processed (for array format)
        if key in processed_keys:
            continue

        match = FILTER_REGEX.match(key)
        if not match:
            continue

        field = match.group("field")
        operator = match.group("operator") or "eq"

        # Handle list values (from repeated keys or array format)
        # Examples:
        # - filter[tags]=tag1&filter[tags]=tag2 → {"filter[tags]": ["tag1", "tag2"]}
        # - filter[tags][]=tag1&filter[tags][]=tag2 → {"filter[tags][]": ["tag1", "tag2"]}
        if isinstance(value, list):
            # If operator not specified and we have a list, default to "in" operator
            if not match.group("operator") and len(value) > 1:
                operator = FilterOperator.IN.value
            # FastAPI/Starlette can parse arrays automatically
            normalized_value = _normalize_value(value, operator)
            filters.append(
                FilterSchema(
                    field=field,
                    operator=operator,
                    value=normalized_value,
                )
            )
            processed_keys.add(key)
            continue

        # Handle string values
        if not isinstance(value, str):
            continue

        # Normalize value (trim, handle null, etc.)
        normalized_value = _normalize_value(value, operator)

        # Skip empty values after normalization
        if normalized_value is None or (
            isinstance(normalized_value, str) and not normalized_value.strip()
        ):
            continue

        filters.append(
            FilterSchema(
                field=field,
                operator=operator,
                value=normalized_value,
            )
        )

    return filters


def _normalize_value(value: Union[str, List[str]], operator: str) -> Any:
    """
    Normalize a filter value based on the operator and value type.

    Args:
        value: Raw value from query params (string or list)
        operator: Filter operator

    Returns:
        Normalized value (string, list, None, etc.)
    """
    # Handle list values (from array format)
    if isinstance(value, list):
        # Trim and filter empty values
        normalized = [v.strip() if isinstance(v, str) else v for v in value if v]
        # Convert "null" strings to None
        normalized = [_parse_null(v) for v in normalized]
        return normalized if normalized else None

    # Handle string values
    if not isinstance(value, str):
        return value

    # Trim the value
    value = value.strip()

    # Handle null values
    if value.lower() in ("null", "none", ""):
        return None

    # Handle IN operator: split comma-separated values
    if operator == FilterOperator.IN.value or operator == "in":
        # Split by comma and normalize each value
        parts = split_comma_separated(value)
        # Convert "null" strings to None
        normalized = [_parse_null(part) for part in parts]
        return normalized if normalized else None

    # For other operators, return the trimmed string
    return value


def _parse_null(value: Any) -> Any:
    """
    Parse null-like values to None.

    Args:
        value: Value to check

    Returns:
        None if value represents null, otherwise the original value
    """
    if isinstance(value, str) and value.lower() in ("null", "none"):
        return None
    return value
