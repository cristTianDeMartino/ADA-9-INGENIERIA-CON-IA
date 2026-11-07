"""Repository layer for customer data persistence and retrieval."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Protocol
from src.customer_search.models import Customer
from src.customer_search.exceptions import DataLoadError


class CustomerRepository(Protocol):
    """Abstract interface for customer persistence."""

    def get_all(self) -> list[Customer]:
        """Retrieve all customers in the repository."""
        ...

    def add(self, customer: Customer) -> None:
        """Add a single customer to the repository."""
        ...


class InMemoryCustomerRepository:
    """In-memory implementation of CustomerRepository with JSON loading support."""

    def __init__(self, customers: list[Customer] | None = None) -> None:
        self._customers: list[Customer] = list(customers) if customers else []

    def get_all(self) -> list[Customer]:
        """Return a copy of all customer entities."""
        return list(self._customers)

    def add(self, customer: Customer) -> None:
        """Add a customer entity to memory."""
        self._customers.append(customer)

    @classmethod
    def from_json_file(cls, file_path: str | Path) -> InMemoryCustomerRepository:
        """Load customer dataset from a JSON file.

        Args:
            file_path: Path to the JSON file.

        Returns:
            An initialized InMemoryCustomerRepository instance.

        Raises:
            DataLoadError: If file is not found, not valid JSON, or contains invalid customer data.
        """
        path = Path(file_path)
        if not path.is_file():
            raise DataLoadError(f"Customer data file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except Exception as e:
            raise DataLoadError(f"Failed to read or parse JSON file {path}: {e}") from e

        if not isinstance(raw_data, list):
            raise DataLoadError(f"Expected JSON root to be a list in {path}, got {type(raw_data).__name__}")

        customers: list[Customer] = []
        for idx, item in enumerate(raw_data):
            if not isinstance(item, dict):
                raise DataLoadError(f"Record at index {idx} is not a valid dictionary object.")
            try:
                customers.append(Customer.from_dict(item))
            except Exception as e:
                raise DataLoadError(f"Invalid customer record at index {idx}: {e}") from e

        return cls(customers=customers)
