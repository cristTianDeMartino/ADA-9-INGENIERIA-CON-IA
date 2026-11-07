"""Validation logic for customer search queries."""
from src.customer_search.exceptions import ValidationError

ALLOWED_FIELDS = {"all", "name", "email"}


class SearchQueryValidator:
    """Validates search queries and target field parameters.

    Enforces rules VR-01, VR-02, and VR-03 from SPEC.md.
    """

    @staticmethod
    def validate(query: str, field: str = "all") -> str:
        """Validate search query and field.

        Args:
            query: The search term to validate.
            field: Target field ('all', 'name', 'email').

        Returns:
            The normalized search query (stripped of surrounding whitespace).

        Raises:
            ValidationError: If query is empty, shorter than 2 chars, or field is invalid.
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

        return normalized_query
