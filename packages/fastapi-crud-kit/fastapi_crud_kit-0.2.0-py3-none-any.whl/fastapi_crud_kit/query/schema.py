from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class FilterSchema(BaseModel):
    field: str
    operator: str = "eq"
    value: Any


class QueryParams(BaseModel):
    filters: List[FilterSchema] = []
    sort: List[str] = []
    include: List[str] = []
    fields: List[str] = []
    # Pagination parameters
    page: int | None = None
    per_page: int | None = None
    limit: int | None = None
    offset: int | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Response model for paginated queries with complete metadata."""

    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
