"""Integration tests for CustomerSearchService covering AC-01 to AC-03, AC-05, and AC-08."""
import pytest
from src.customer_search.models import Customer
from src.customer_search.repository import InMemoryCustomerRepository
from src.customer_search.service import CustomerSearchService
from src.customer_search.exceptions import ValidationError


@pytest.fixture
def search_service(sample_customers):
    repo = InMemoryCustomerRepository(sample_customers)
    return CustomerSearchService(repository=repo)


def test_search_by_name_partial_and_case_insensitive(search_service):
    # AC-01 / FR-01: 'garcia' in lowercase should match 'Ana Garcia' and 'Carlos Ramirez Garcia'
    result = search_service.search("garcia", field="name")
    assert result.total_matches == 2
    matched_ids = [c.id for c in result.customers]
    assert matched_ids == ["cust-001", "cust-002"]

    # Upper case test
    result_upper = search_service.search("GARCIA", field="name")
    assert result_upper.total_matches == 2


def test_search_by_email_partial_and_case_insensitive(search_service):
    # AC-02 / FR-02: 'garcia' in email matches 'ana.garcia@example.com' and 'bmendez@garcia-associates.com'
    result = search_service.search("garcia", field="email")
    assert result.total_matches == 2
    matched_ids = [c.id for c in result.customers]
    assert matched_ids == ["cust-001", "cust-003"]

    # Domain match specific to cust-003
    res_domain_assoc = search_service.search("garcia-associates.com", field="email")
    assert res_domain_assoc.total_matches == 1
    assert res_domain_assoc.customers[0].id == "cust-003"
    assert res_domain_assoc.customers[0].name == "Beatriz Mendez"

    # Domain match specific to cust-002
    res_domain = search_service.search("company.org", field="email")
    assert res_domain.total_matches == 1
    assert res_domain.customers[0].id == "cust-002"


def test_unified_search_all_fields(search_service):
    # AC-03 / FR-03: 'garcia' in all fields matches name in cust-001, cust-002 and email in cust-003
    result = search_service.search("garcia", field="all")
    assert result.total_matches == 3
    # Check deduplication and ordering by name
    names = [c.name for c in result.customers]
    assert names == ["Ana Garcia", "Beatriz Mendez", "Carlos Ramirez Garcia"]


def test_search_with_whitespace_stripping(search_service):
    # SR-01: Query with leading/trailing whitespace
    result = search_service.search("   lopez   ", field="name")
    assert result.query == "lopez"
    assert result.total_matches == 1
    assert result.customers[0].id == "cust-004"


def test_search_no_matches(search_service):
    # AC-05 / FR-05: Returns empty list when no matches found
    result = search_service.search("nonexistent_term_99", field="all")
    assert result.total_matches == 0
    assert result.customers == []


def test_search_validates_query(search_service):
    # AC-04 / FR-04: Should raise ValidationError through service
    with pytest.raises(ValidationError):
        search_service.search("a", field="name")

    with pytest.raises(ValidationError):
        search_service.search("valid", field="unsupported_field")


def test_service_decoupling_with_custom_repo():
    # AC-08 / NFR-02: Service works independently with any repository
    custom_repo = InMemoryCustomerRepository([
        Customer("1", "Zack Taylor", "zack@ranger.net", "111"),
        Customer("2", "Adam Park", "adam@ranger.net", "222"),
    ])
    service = CustomerSearchService(custom_repo)
    result = service.search("ranger", field="email")
    assert result.total_matches == 2
    assert [c.name for c in result.customers] == ["Adam Park", "Zack Taylor"]


def test_service_active_only_filter():
    # CR-01: active_only flag returns only active customers
    custom_repo = InMemoryCustomerRepository([
        Customer("1", "Alice Active", "alice@example.com", "111", is_active=True),
        Customer("2", "Bob Inactive", "bob@example.com", "222", is_active=False),
    ])
    service = CustomerSearchService(custom_repo)

    # By default, both are returned
    all_res = service.search("example", field="email")
    assert all_res.total_matches == 2

    # With active_only=True, only Alice is returned
    active_res = service.search("example", field="email", active_only=True)
    assert active_res.total_matches == 1
    assert active_res.customers[0].id == "1"
    assert active_res.customers[0].is_active is True


def test_service_search_with_limit(search_service):
    # CR-02: limit parameter restricts returned customers
    res = search_service.search("garcia", field="all", limit=2)
    assert len(res.customers) == 2
    assert [c.name for c in res.customers] == ["Ana Garcia", "Beatriz Mendez"]


