from typing import List, Optional

from .fields.allowed import AllowedField
from .filters.allowed import AllowedFilters
from .include.allowed import AllowedInclude
from .sort.allowed import AllowedSort


class QueryBuilderConfig:
    """
    Configuration for QueryBuilder with validation for filters, sorts, fields, and includes.

    This class holds the configuration for query building, including which
    filters, sorts, fields, and includes are allowed and how to handle invalid ones.
    """

    def __init__(
        self,
        allowed_filters: Optional[List[AllowedFilters]] = None,
        allowed_sorts: Optional[List[AllowedSort]] = None,
        allowed_fields: Optional[List[AllowedField]] = None,
        allowed_includes: Optional[List[AllowedInclude]] = None,
        ignore_invalid_errors: bool = False,
    ) -> None:
        """
        Initialize QueryBuilder configuration.

        Args:
            allowed_filters: List of AllowedFilters that define which filters are allowed.
                            If None, all filters are allowed (no validation).
            allowed_sorts: List of AllowedSort that define which sort fields are allowed.
                          If None, all sorts are allowed (no validation).
            allowed_fields: List of AllowedField that define which fields can be selected.
                           If None, all fields are allowed (no validation).
            allowed_includes: List of AllowedInclude that define which relationships can be included.
                             If None, all includes are allowed (no validation).
            ignore_invalid_errors: If True, invalid filters/sorts/fields/includes are silently ignored.
                                   If False, raises exceptions for invalid values.
        """
        self.allowed_filters = allowed_filters or []
        self.allowed_sorts = allowed_sorts or []
        self.allowed_fields = allowed_fields or []
        self.allowed_includes = allowed_includes or []

        # Single parameter for all validation errors
        self.ignore_invalid_errors = ignore_invalid_errors

        # Build mappings from alias/field to Allowed* for quick lookup
        self._filter_map: dict[str, AllowedFilters] = {}
        for allowed_filter in self.allowed_filters:
            self._filter_map[allowed_filter.field] = allowed_filter
            if allowed_filter.alias != allowed_filter.field:
                self._filter_map[allowed_filter.alias] = allowed_filter

        self._sort_map: dict[str, AllowedSort] = {}
        for allowed_sort in self.allowed_sorts:
            # Map all fields in the sort
            for field in allowed_sort.fields:
                self._sort_map[field] = allowed_sort
            # Also map alias if different
            if allowed_sort.alias != allowed_sort.field:
                self._sort_map[allowed_sort.alias] = allowed_sort

        self._field_map: dict[str, AllowedField] = {}
        for allowed_field in self.allowed_fields:
            # Map all fields in the field selection
            for field in allowed_field.fields:
                self._field_map[field] = allowed_field
            # Also map alias if different
            if allowed_field.alias != allowed_field.field:
                self._field_map[allowed_field.alias] = allowed_field

        self._include_map: dict[str, AllowedInclude] = {}
        for allowed_include in self.allowed_includes:
            # Map all relationships in the include
            for relationship in allowed_include.relationships:
                self._include_map[relationship] = allowed_include
            # Also map alias if different
            if allowed_include.alias != allowed_include.relationship:
                self._include_map[allowed_include.alias] = allowed_include

    def get_allowed_filter(self, field_or_alias: str) -> Optional[AllowedFilters]:
        """
        Get the AllowedFilters instance for a given field or alias.

        Args:
            field_or_alias: Field name or alias from the URL

        Returns:
            AllowedFilters instance if found, None otherwise
        """
        return self._filter_map.get(field_or_alias)

    def is_filter_allowed(self, field_or_alias: str) -> bool:
        """
        Check if a filter is allowed.

        Args:
            field_or_alias: Field name or alias to check

        Returns:
            True if the filter is allowed, False otherwise.
            Returns True if no allowed_filters are configured (all filters allowed).
        """
        if not self.allowed_filters:
            return True  # No restrictions, all filters allowed
        return field_or_alias in self._filter_map

    def get_allowed_sort(self, field_or_alias: str) -> Optional[AllowedSort]:
        """
        Get the AllowedSort instance for a given field or alias.

        Args:
            field_or_alias: Field name or alias from the URL

        Returns:
            AllowedSort instance if found, None otherwise
        """
        return self._sort_map.get(field_or_alias)

    def is_sort_allowed(self, field_or_alias: str) -> bool:
        """
        Check if a sort field is allowed.

        Args:
            field_or_alias: Field name or alias to check

        Returns:
            True if the sort is allowed, False otherwise.
            Returns True if no allowed_sorts are configured (all sorts allowed).
        """
        if not self.allowed_sorts:
            return True  # No restrictions, all sorts allowed
        return field_or_alias in self._sort_map

    def get_allowed_field(self, field_or_alias: str) -> Optional[AllowedField]:
        """
        Get the AllowedField instance for a given field or alias.

        Args:
            field_or_alias: Field name or alias from the URL

        Returns:
            AllowedField instance if found, None otherwise
        """
        return self._field_map.get(field_or_alias)

    def is_field_allowed(self, field_or_alias: str) -> bool:
        """
        Check if a field selection is allowed.

        Args:
            field_or_alias: Field name or alias to check

        Returns:
            True if the field is allowed, False otherwise.
            Returns True if no allowed_fields are configured (all fields allowed).
        """
        if not self.allowed_fields:
            return True  # No restrictions, all fields allowed
        return field_or_alias in self._field_map

    def get_allowed_include(
        self, relationship_or_alias: str
    ) -> Optional[AllowedInclude]:
        """
        Get the AllowedInclude instance for a given relationship or alias.

        Args:
            relationship_or_alias: Relationship name or alias from the URL

        Returns:
            AllowedInclude instance if found, None otherwise
        """
        return self._include_map.get(relationship_or_alias)

    def is_include_allowed(self, relationship_or_alias: str) -> bool:
        """
        Check if a relationship include is allowed.

        Args:
            relationship_or_alias: Relationship name or alias to check

        Returns:
            True if the include is allowed, False otherwise.
            Returns True if no allowed_includes are configured (all includes allowed).
        """
        if not self.allowed_includes:
            return True  # No restrictions, all includes allowed
        return relationship_or_alias in self._include_map
