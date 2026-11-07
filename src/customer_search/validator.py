"""Validation logic for customer search queries."""
from src.customer_search.exceptions import ValidationError

ALLOWED_FIELDS = {"all", "name", "email"}


class SearchQueryValidator:
    """Validates search queries and target field parameters.

    Enforces rules VR-01, VR-02, and VR-03 from SPEC.md.
    """

    @staticmethod
    def validate(query: str, field: str = "all", limit: int | None = None) -> str:
        """Validate search query, target field, and optional result limit.

        Args:
            query: The search term to validate.
            field: Target field ('all', 'name', 'email').
            limit: Optional maximum number of customer records to return (>= 1).

        Returns:
            The normalized search query (stripped of surrounding whitespace).

        Raises:
            ValidationError: If query is empty, shorter than 2 chars, field is invalid,
                or limit is not a positive integer >= 1.
        """
        if not isinstance(query, str):
            raise ValidationError("Search query must contain at least 2 non-whitespace characters.")

        normalized_query = query.strip()

        # VR-01 & VR-02
        if len(normalized_query) < 2:
            raise ValidationError(
                "Search query must contain at least 2 non-whitespace characters."
            )

        # VR-03
        if not isinstance(field, str) or field.lower().strip() not in ALLOWED_FIELDS:
            raise ValidationError(
                f"Invalid search field '{field}'. Allowed fields are: all, name, email."
            )

        if limit is not None:
            if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
                raise ValidationError(
                    "Result limit must be a positive integer greater than or equal to 1."
                )

        return normalized_query
