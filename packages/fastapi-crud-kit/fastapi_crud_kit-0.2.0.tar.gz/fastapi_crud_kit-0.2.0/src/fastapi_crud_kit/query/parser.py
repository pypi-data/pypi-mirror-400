from typing import List, Mapping, Union

from .filters.parser import parse_filters
from .schema import QueryParams
from .utils import split_comma_separated


def parse_sort(query_params: Mapping[str, Union[str, List[str]]]) -> List[str]:
    sort = query_params.get("sort")
    if not sort:
        return []
    if isinstance(sort, list):
        return sort
    return split_comma_separated(sort)


def parse_include(query_params: Mapping[str, Union[str, List[str]]]) -> List[str]:
    include = query_params.get("include")
    if not include:
        return []
    if isinstance(include, list):
        return include
    return split_comma_separated(include)


def parse_fields(query_params: Mapping[str, Union[str, List[str]]]) -> List[str]:
    fields = query_params.get("fields")
    if not fields:
        return []
    if isinstance(fields, list):
        return fields
    return split_comma_separated(fields)


def _parse_int_param(
    query_params: Mapping[str, Union[str, List[str]]],
    key: str,
    default: int | None = None,
) -> int | None:
    """Parse an integer query parameter."""
    value = query_params.get(key)
    if value is None:
        return default
    if isinstance(value, list) and value:
        value = value[0]
    if not isinstance(value, str):
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def parse_query_params(
    query_params: Mapping[str, Union[str, List[str]]],
) -> QueryParams:
    return QueryParams(
        filters=parse_filters(query_params),
        sort=parse_sort(query_params),
        include=parse_include(query_params),
        fields=parse_fields(query_params),
        page=_parse_int_param(query_params, "page"),
        per_page=_parse_int_param(query_params, "per_page"),
        limit=_parse_int_param(query_params, "limit"),
        offset=_parse_int_param(query_params, "offset"),
    )
