"""Domain models for the Customer Search feature."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Customer:
    """Represents a customer entity in the system.

    Adheres to Domain Model specification in SPEC.md.
    """
    id: str
    name: str
    email: str
    phone: str
    is_active: bool = True

    def __post_init__(self) -> None:
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Customer id must be a non-empty string.")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Customer name must be a non-empty string.")
        if not self.email or not isinstance(self.email, str):
            raise ValueError("Customer email must be a non-empty string.")
        if not isinstance(self.phone, str):
            raise ValueError("Customer phone must be a string.")
        if not isinstance(self.is_active, bool):
            raise ValueError("Customer is_active must be a boolean.")

    def to_dict(self) -> dict[str, Any]:
        """Convert customer entity to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Customer:
        """Create a Customer instance from a dictionary."""
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            email=str(data.get("email", "")),
            phone=str(data.get("phone", "")),
            is_active=bool(data.get("is_active", True)),
        )


@dataclass(frozen=True)
class SearchResult:
    """Represents the outcome of a customer search operation.

    Adheres to SearchResult specification in SPEC.md.
    """
    query: str
    field: str
    total_matches: int
    customers: list[Customer]

    def to_dict(self) -> dict[str, Any]:
        """Convert search result to dictionary."""
        return {
            "query": self.query,
            "field": self.field,
            "total_matches": self.total_matches,
            "customers": [c.to_dict() for c in self.customers],
        }
