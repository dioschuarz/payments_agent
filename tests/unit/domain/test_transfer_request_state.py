"""Phase 1: Domain Logic Unit Tests - TransferRequest State Management.

Tests the brain of the system in total isolation.
No ADK, no LLM, no Network. Fast execution (<1s).
"""

import pytest

from src.domain.entities.beneficiary import Beneficiary
from src.domain.entities.transfer_request import TransferRequest
from src.domain.value_objects.amount import Amount
from src.domain.value_objects.country import Country
from src.domain.value_objects.delivery_method import DeliveryMethod, DeliveryMethodType


class TestTransferRequestState:
    """TC-UNIT-01: Test initial state is empty."""

    def test_initial_state_empty(self):
        """
        TC-UNIT-01: test_initial_state_empty
        
        Given: a new TransferRequest
        Then: all slots (amount, country, beneficiary, delivery_method) should be None
        And: missing_fields should return all 4 required fields
        """
        request = TransferRequest()
        
        assert request.beneficiary is None
        assert request.amount is None
        assert request.country is None
        assert request.delivery_method is None
        
        missing = request.get_missing_fields()
        assert len(missing) == 4
        assert "beneficiary" in missing
        assert "amount" in missing
        assert "country" in missing
        assert "delivery_method" in missing
        assert request.is_complete() is False

    def test_slot_filling_partial(self):
        """
        TC-UNIT-02: test_slot_filling_partial
        
        Given: input "Send to Brazil"
        When: country is set
        Then: country is "Brazil", but amount remains None
        """
        request = TransferRequest()
        country = Country.from_name("Brazil")
        
        request.country = country
        
        assert request.country is not None
        assert request.country.name == "Brazil"
        assert request.amount is None
        assert request.beneficiary is None
        assert request.delivery_method is None
        
        missing = request.get_missing_fields()
        assert "country" not in missing
        assert "amount" in missing
        assert "beneficiary" in missing
        assert "delivery_method" in missing

    def test_overwrite_slot_correction(self):
        """
        TC-UNIT-03: test_overwrite_slot_correction
        
        Given: state has country="Brazil"
        When: country is updated to "France"
        Then: country updates to "France" (Overwrite logic)
        """
        request = TransferRequest()
        brazil = Country.from_name("Brazil")
        france = Country.from_name("France")
        
        request.country = brazil
        assert request.country.name == "Brazil"
        
        # Overwrite with correction
        request.country = france
        assert request.country.name == "France"
        assert request.country.code == "FR"

    def test_ready_to_confirm(self):
        """
        TC-UNIT-07: test_ready_to_confirm
        
        Given: all 4 slots are filled and valid
        Then: is_complete() returns True
        """
        request = TransferRequest()
        
        request.beneficiary = Beneficiary(id="1", name="John Doe")
        request.amount = Amount(value=100, currency="USD")
        request.country = Country.from_name("Brazil")
        request.delivery_method = DeliveryMethod(method=DeliveryMethodType.BANK_TRANSFER)
        
        assert request.is_complete() is True
        assert len(request.get_missing_fields()) == 0
        
        # Verify to_dict() works correctly
        result = request.to_dict()
        assert result["beneficiary"] is not None
        assert result["amount"] is not None
        assert result["country"] is not None
        assert result["delivery_method"] is not None

