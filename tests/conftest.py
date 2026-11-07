"""Shared pytest fixtures for Customer Search feature tests."""
import pytest
from src.customer_search.models import Customer


@pytest.fixture
def sample_customers() -> list[Customer]:
    """Returns a representative list of customers for testing."""
    return [
        Customer(
            id="cust-001",
            name="Ana Garcia",
            email="ana.garcia@example.com",
            phone="+52-999-111-2233",
            is_active=True,
        ),
        Customer(
            id="cust-002",
            name="Carlos Ramirez Garcia",
            email="carlos.r@company.org",
            phone="+52-999-444-5566",
            is_active=True,
        ),
        Customer(
            id="cust-003",
            name="Beatriz Mendez",
            email="bmendez@garcia-associates.com",
            phone="+52-999-777-8899",
            is_active=False,
        ),
        Customer(
            id="cust-004",
            name="David Lopez",
            email="david.lopez@technology.io",
            phone="+52-999-000-1122",
            is_active=True,
        ),
    ]
