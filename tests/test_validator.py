"""Unit tests for SearchQueryValidator (T-04 / VR-01, VR-02, VR-03)."""
import pytest
from src.customer_search.validator import SearchQueryValidator
from src.customer_search.exceptions import ValidationError


def test_validator_valid_queries():
    assert SearchQueryValidator.validate("ana") == "ana"
    assert SearchQueryValidator.validate("  garcia  ") == "garcia"
    assert SearchQueryValidator.validate("acme.com", field="email") == "acme.com"
    assert SearchQueryValidator.validate("john", field="all") == "john"


@pytest.mark.parametrize(
    "invalid_query",
    ["", "   ", "a", " b ", "  x  ", None],
)
def test_validator_invalid_query_length_or_empty(invalid_query):
    with pytest.raises(ValidationError, match="Search query must contain at least 2 non-whitespace characters"):
        SearchQueryValidator.validate(invalid_query)  # type: ignore


@pytest.mark.parametrize("invalid_field", ["phone", "address", "id", "role", ""])
def test_validator_invalid_field(invalid_field):
    with pytest.raises(ValidationError, match="Invalid search field"):
        SearchQueryValidator.validate("valid_query", field=invalid_field)
