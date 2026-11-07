"""Service layer implementing Customer Search logic according to SPEC.md."""
from __future__ import annotations
from typing import TYPE_CHECKING
from src.customer_search.models import Customer, SearchResult
from src.customer_search.validator import SearchQueryValidator

if TYPE_CHECKING:
    from src.customer_search.repository import CustomerRepository


class CustomerSearchService:
    """Core service executing customer search based on SPEC.md rules."""

    def __init__(
        self,
        repository: CustomerRepository,
        validator: SearchQueryValidator | None = None,
    ) -> None:
        self._repository = repository
        self._validator = validator or SearchQueryValidator()

    def search(
        self,
        query: str,
        field: str = "all",
        active_only: bool = False,
        limit: int | None = None,
    ) -> SearchResult:
        """Search customers matching query on given field.

        Args:
            query: The search term.
            field: One of 'all', 'name', 'email'. Defaults to 'all'.
            active_only: If True, restricts matches to active customers.
            limit: Optional maximum number of customer records to return.

        Returns:
            SearchResult containing matching customers and match metrics.

        Raises:
            ValidationError: If query violates VR-01, VR-02, VR-03, or if limit is invalid.
        """
        # Validate and normalize query (VR-01, VR-02, VR-03) and optional limit
        normalized_query = self._validator.validate(query, field=field, limit=limit)
        field_target = field.lower().strip()
        search_term_lower = normalized_query.lower()

        all_customers = self._repository.get_all()
        matched: list[Customer] = []

        for customer in all_customers:
            if active_only and not customer.is_active:
                continue

            name_lower = customer.name.lower()
            email_lower = customer.email.lower()

            if field_target == "name":
                # SR-03 Substring match on name
                if search_term_lower in name_lower:
                    matched.append(customer)
            elif field_target == "email":
                # SR-03 Substring match on email
                if search_term_lower in email_lower:
                    matched.append(customer)
            elif field_target == "all":
                # SR-04 Unified search: name OR email, without duplicates
                if search_term_lower in name_lower or search_term_lower in email_lower:
                    matched.append(customer)

        # SR-05 Sort alphabetically by name ascending, then by id
        matched.sort(key=lambda c: (c.name.lower(), c.id))
        total_matches = len(matched)

        if limit is not None:
            matched = matched[:limit]

        return SearchResult(
            query=normalized_query,
            field=field_target,
            total_matches=total_matches,
            customers=matched,
        )
