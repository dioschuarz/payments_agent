"""Tests for TransferRequest entity."""

from src.domain.entities.beneficiary import Beneficiary
from src.domain.entities.transfer_request import TransferRequest
from src.domain.value_objects.amount import Amount
from src.domain.value_objects.country import Country
from src.domain.value_objects.delivery_method import DeliveryMethod, DeliveryMethodType


def test_transfer_request_is_complete():
    """Test is_complete() when all fields are filled."""
    request = TransferRequest(
        beneficiary=Beneficiary(id="1", name="John Doe"),
        amount=Amount(value=100, currency="USD"),
        country=Country(code="US", name="United States"),
        delivery_method=DeliveryMethod(method=DeliveryMethodType.BANK_TRANSFER),
    )

    assert request.is_complete() is True


def test_transfer_request_missing_fields():
    """Test get_missing_fields() returns correct fields."""
    request = TransferRequest(
        beneficiary=Beneficiary(id="1", name="John Doe"),
        # Missing amount, country, delivery_method
    )

    missing = request.get_missing_fields()
    assert "amount" in missing
    assert "country" in missing
    assert "delivery_method" in missing
    assert "beneficiary" not in missing


def test_transfer_request_to_dict():
    """Test to_dict() serialization."""
    request = TransferRequest(
        beneficiary=Beneficiary(id="1", name="John Doe"),
        amount=Amount(value=100, currency="USD"),
        country=Country(code="US", name="United States"),
        delivery_method=DeliveryMethod(method=DeliveryMethodType.BANK_TRANSFER),
    )

    data = request.to_dict()
    assert data["beneficiary"]["name"] == "John Doe"
    assert data["amount"]["value"] == "100"
    assert data["amount"]["currency"] == "USD"

