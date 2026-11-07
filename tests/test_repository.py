"""Unit tests for CustomerRepository (InMemoryCustomerRepository and JSON loading)."""
from pathlib import Path
import pytest
from src.customer_search.models import Customer
from src.customer_search.repository import InMemoryCustomerRepository
from src.customer_search.exceptions import DataLoadError


def test_in_memory_repository_initialization(sample_customers):
    repo = InMemoryCustomerRepository(sample_customers)
    assert len(repo.get_all()) == 4
    
    # Verify copy is returned (immutability of internal list)
    retrieved = repo.get_all()
    retrieved.pop()
    assert len(repo.get_all()) == 4


def test_in_memory_repository_add():
    repo = InMemoryCustomerRepository()
    assert len(repo.get_all()) == 0
    customer = Customer(
        id="c-new",
        name="New Customer",
        email="new@example.com",
        phone="+52-999-1111111",
    )
    repo.add(customer)
    assert len(repo.get_all()) == 1
    assert repo.get_all()[0].id == "c-new"


def test_load_from_valid_json_file(tmp_path: Path):
    json_file = tmp_path / "valid_customers.json"
    json_file.write_text(
        """[
            {"id": "1", "name": "Alice", "email": "alice@corp.com", "phone": "123", "is_active": true},
            {"id": "2", "name": "Bob", "email": "bob@corp.com", "phone": "456", "is_active": false}
        ]""",
        encoding="utf-8",
    )
    repo = InMemoryCustomerRepository.from_json_file(json_file)
    customers = repo.get_all()
    assert len(customers) == 2
    assert customers[0].name == "Alice"
    assert customers[1].is_active is False


def test_load_from_nonexistent_json_file():
    with pytest.raises(DataLoadError, match="Customer data file not found"):
        InMemoryCustomerRepository.from_json_file("nonexistent_path_xyz.json")


def test_load_from_malformed_json_file(tmp_path: Path):
    bad_json = tmp_path / "malformed.json"
    bad_json.write_text("{this is not valid json}", encoding="utf-8")
    with pytest.raises(DataLoadError, match="Failed to read or parse JSON file"):
        InMemoryCustomerRepository.from_json_file(bad_json)


def test_load_from_invalid_schema_json(tmp_path: Path):
    invalid_schema = tmp_path / "invalid_schema.json"
    invalid_schema.write_text('[{"id": "", "name": "No ID"}]', encoding="utf-8")
    with pytest.raises(DataLoadError, match="Invalid customer record at index 0"):
        InMemoryCustomerRepository.from_json_file(invalid_schema)
