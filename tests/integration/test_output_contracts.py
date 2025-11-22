"""Phase 3: Output Contract Tests.

Ensures the system integrates with downstream systems
by validating output JSON schema.
"""

import pytest
import json

from src.domain.entities.beneficiary import Beneficiary
from src.domain.entities.transfer_request import TransferRequest
from src.domain.value_objects.amount import Amount
from src.domain.value_objects.country import Country
from src.domain.value_objects.delivery_method import DeliveryMethod, DeliveryMethodType


class TestOutputContracts:
    """TC-OUT-01 to TC-OUT-02: Output contract tests."""

    def test_json_schema_validity(self):
        """
        TC-OUT-01: test_json_schema_validity
        
        Given: a completed TransferRequest
        When: to_dict() is called
        Then: it must be valid JSON containing amount (dict), currency (str), country (dict)
        """
        request = TransferRequest()
        request.beneficiary = Beneficiary(id="1", name="John Doe")
        request.amount = Amount(value=500, currency="USD")
        request.country = Country.from_name("Brazil")
        request.delivery_method = DeliveryMethod(method=DeliveryMethodType.BANK_TRANSFER)
        
        # Convert to dict
        result = request.to_dict()
        
        # Verify it's JSON serializable
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        
        # Verify structure
        assert "beneficiary" in parsed
        assert "amount" in parsed
        assert "country" in parsed
        assert "delivery_method" in parsed
        
        # Verify amount structure
        assert isinstance(parsed["amount"], dict)
        assert "value" in parsed["amount"]
        assert "currency" in parsed["amount"]
        assert isinstance(parsed["amount"]["value"], str)  # Decimal serialized as string
        assert isinstance(parsed["amount"]["currency"], str)
        
        # Verify country structure
        assert isinstance(parsed["country"], dict)
        assert "code" in parsed["country"]
        assert "name" in parsed["country"]
        assert len(parsed["country"]["code"]) == 2  # ISO code

    def test_currency_normalization(self):
        """
        TC-OUT-02: test_currency_normalization
        
        Given: input "500 bucks" or "500 USD"
        Then: output JSON must strictly use "currency": "USD"
        """
        # Test with explicit currency
        amount1 = Amount(value=500, currency="USD")
        request1 = TransferRequest()
        request1.amount = amount1
        
        result1 = request1.to_dict()
        assert result1["amount"]["currency"] == "USD"
        assert result1["amount"]["value"] == "500"
        
        # Test with different currency
        amount2 = Amount(value=500, currency="BRL")
        request2 = TransferRequest()
        request2.amount = amount2
        
        result2 = request2.to_dict()
        assert result2["amount"]["currency"] == "BRL"
        
        # Test currency is always uppercase (from Amount validation)
        amount3 = Amount(value=100, currency="usd")
        assert amount3.currency == "USD"  # Validator uppercases it

    def test_complete_output_structure(self):
        """Test complete output structure matches expected schema."""
        request = TransferRequest()
        request.beneficiary = Beneficiary(
            id="1",
            name="John Doe",
            phone="+1234567890",
            email="john@example.com"
        )
        request.amount = Amount(value=1000, currency="USD")
        request.country = Country.from_name("United States")
        request.delivery_method = DeliveryMethod(method=DeliveryMethodType.MOBILE_WALLET)
        
        result = request.to_dict()
        
        # Verify all required fields
        assert result["beneficiary"]["id"] == "1"
        assert result["beneficiary"]["name"] == "John Doe"
        assert result["amount"]["value"] == "1000"
        assert result["amount"]["currency"] == "USD"
        assert result["country"]["code"] == "US"
        assert result["country"]["name"] == "United States"
        assert result["delivery_method"]["method"] == "mobile_wallet"

