"""Performance test verifying NFR-01 / AC-07 (< 100ms for 1000 records)."""
import time
import pytest
from src.customer_search.models import Customer
from src.customer_search.repository import InMemoryCustomerRepository
from src.customer_search.service import CustomerSearchService


def test_performance_1000_customers():
    # Generate 1,000 synthetic customer records
    synthetic_customers = [
        Customer(
            id=f"cust-{i:04d}",
            name=f"Customer Name {i}",
            email=f"customer{i}@domain{i % 10}.com",
            phone=f"+52-999-{i:03d}-0000",
            is_active=(i % 2 == 0),
        )
        for i in range(1000)
    ]

    repository = InMemoryCustomerRepository(synthetic_customers)
    service = CustomerSearchService(repository=repository)

    # Benchmark search
    start_time = time.perf_counter()
    result = service.search("Name 99", field="all")
    elapsed_time_ms = (time.perf_counter() - start_time) * 1000

    assert result.total_matches >= 1
    # AC-07: Search on 1,000 records must take less than 100 ms
    assert elapsed_time_ms < 100.0, f"Search took {elapsed_time_ms:.2f} ms (threshold: 100 ms)"
