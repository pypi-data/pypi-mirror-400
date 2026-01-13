from typing import Optional


class AllowedField:
    """
    Represents an allowed field selection configuration for query building.

    Similar to Spatie Query Builder's AllowedField, this class defines
    which fields can be selected in the response.

    Can be instantiated with a single field or multiple fields:
    - AllowedField("id")
    - AllowedField("id", "name", "email")
    """

    def __init__(
        self,
        *fields: str,
        alias: Optional[str] = None,
    ) -> None:
        """
        Initialize allowed fields.

        Args:
            *fields: One or more database field names to select
            alias: Alternative name to use in URL (only for single field)
        """
        if not fields:
            raise ValueError("At least one field must be provided")

        self.fields = list(fields)
        # For backward compatibility, keep field and alias for single field
        self.field = self.fields[0]
        self.alias = alias or self.field
