from typing import Literal, Optional


class AllowedSort:
    """
    Represents an allowed sort field configuration for query building.

    Similar to Spatie Query Builder's AllowedSort, this class defines
    which fields can be used for sorting.

    Can be instantiated with a single field or multiple fields:
    - AllowedSort("name")
    - AllowedSort("name", "created_at")
    - AllowedSort("name", direction="desc")
    """

    def __init__(
        self,
        *fields: str,
        direction: Literal["asc", "desc"] = "asc",
        alias: Optional[str] = None,
    ) -> None:
        """
        Initialize allowed sort fields.

        Args:
            *fields: One or more database field names to sort on
            direction: Default sort direction ("asc" or "desc")
            alias: Alternative name to use in URL (only for single field)
        """
        if not fields:
            raise ValueError("At least one field must be provided")

        self.fields = list(fields)
        self.direction = direction
        # For backward compatibility, keep field and alias for single field
        self.field = self.fields[0]
        self.alias = alias or self.field

    def __call__(
        self,
        *fields: str,
        direction: Optional[Literal["asc", "desc"]] = None,
    ) -> "AllowedSort":
        """
        Create a new AllowedSort instance with the same configuration.

        Args:
            *fields: One or more database field names
            direction: Sort direction ("asc" or "desc"), defaults to instance direction

        Returns:
            New AllowedSort instance
        """
        return AllowedSort(
            *fields,
            direction=direction or self.direction,
        )
