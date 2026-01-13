from typing import Optional


class AllowedInclude:
    """
    Represents an allowed relationship include configuration for query building.

    Similar to Spatie Query Builder's AllowedInclude, this class defines
    which relationships can be eagerly loaded.

    Can be instantiated with a single relationship or multiple relationships:
    - AllowedInclude("article")
    - AllowedInclude("article", "tag")
    """

    def __init__(
        self,
        *relationships: str,
        alias: Optional[str] = None,
    ) -> None:
        """
        Initialize allowed includes.

        Args:
            *relationships: One or more relationship names to include
            alias: Alternative name to use in URL (only for single relationship)
        """
        if not relationships:
            raise ValueError("At least one relationship must be provided")

        self.relationships = list(relationships)
        # For backward compatibility, keep relationship and alias for single relationship
        self.relationship = self.relationships[0]
        self.alias = alias or self.relationship
