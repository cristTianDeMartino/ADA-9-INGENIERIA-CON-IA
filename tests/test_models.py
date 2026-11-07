"""Unit tests for Customer and SearchResult domain models."""
import pytest
from src.customer_search.models import Customer, SearchResult


def test_customer_creation_valid():
    customer = Customer(
        id="c-1",
        name="Carlos Santana",
        email="carlos@music.org",
        phone="+52-999-1234567",
        is_active=True,
    )
    assert customer.id == "c-1"
    assert customer.name == "Carlos Santana"
    assert customer.email == "carlos@music.org"
    assert customer.phone == "+52-999-1234567"
    assert customer.is_active is True


def test_customer_immutability():
    customer = Customer(
        id="c-1",
        name="Carlos Santana",
        email="carlos@music.org",
        phone="+52-999-1234567",
    )
    with pytest.raises(Exception):
        customer.name = "Carlos Updated"  # type: ignore


@pytest.mark.parametrize(
    "invalid_kwargs,expected_msg",
    [
        ({"id": "", "name": "A", "email": "a@a.com", "phone": "123"}, "Customer id must be a non-empty string"),
        ({"id": "1", "name": "", "email": "a@a.com", "phone": "123"}, "Customer name must be a non-empty string"),
        ({"id": "1", "name": "A", "email": "", "phone": "123"}, "Customer email must be a non-empty string"),
    ],
)
def test_customer_validation_errors(invalid_kwargs, expected_msg):
    with pytest.raises(ValueError, match=expected_msg):
        Customer(**invalid_kwargs)


def test_customer_dict_serialization():
    data = {
        "id": "c-100",
        "name": "Maria Lopez",
        "email": "mlopez@tech.io",
        "phone": "+52-999-0001122",
        "is_active": True,
    }
    customer = Customer.from_dict(data)
    assert customer.to_dict() == data


def test_search_result_serialization(sample_customers):
    result = SearchResult(
        query="garcia",
        field="name",
        total_matches=len(sample_customers),
        customers=sample_customers,
    )
    res_dict = result.to_dict()
    assert res_dict["query"] == "garcia"
    assert res_dict["field"] == "name"
    assert res_dict["total_matches"] == 4
    assert len(res_dict["customers"]) == 4
    assert res_dict["customers"][0]["id"] == "cust-001"
