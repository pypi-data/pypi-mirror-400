from typing import List


def split_comma_separated(value: str) -> List[str]:
    """
    Split a comma-separated string and return a list of trimmed, non-empty values.

    Args:
        value: A comma-separated string (e.g., "field1, field2, field3")

    Returns:
        A list of trimmed strings, excluding empty values

    Examples:
        >>> split_comma_separated("field1, field2, field3")
        ['field1', 'field2', 'field3']
        >>> split_comma_separated("field1,  , field2")
        ['field1', 'field2']
    """
    return [s.strip() for s in value.split(",") if s.strip()]
