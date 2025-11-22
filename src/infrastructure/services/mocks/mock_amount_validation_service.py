"""Mock amount validation service using JSON data."""

from typing import List

from src.domain.value_objects.amount import Amount
from src.infrastructure.mocks.data_loader import DataLoader
from src.infrastructure.services.interfaces.iamount_validation_service import IAmountValidationService


class MockAmountValidationService:
    """Mock service for amount validation using JSON currency data."""

    def __init__(self, data_loader: DataLoader = None):
        """
        Initialize with mock data from JSON.

        Args:
            data_loader: Optional data loader (creates default if not provided)
        """
        if data_loader is None:
            data_loader = DataLoader()
        self._data_loader = data_loader
        self._load_currencies()

    def _load_currencies(self):
        """Load currencies from JSON file."""
        data = self._data_loader.load_currencies()
        self._supported_currencies = {item["code"]: item for item in data["supported_currencies"]}
        self._default_currency = data["default_currency"]

    async def validate_amount(self, amount_input: str, currency: str = "USD") -> List[Amount]:
        """
        Validate and parse amount from input.

        Args:
            amount_input: Amount string (can include currency name or symbol)
            currency: Default currency code (used if currency not detected in input)

        Returns:
            List containing single valid Amount, or empty list if invalid
        """
        # Use default currency if not provided
        if not currency or currency not in self._supported_currencies:
            currency = self._default_currency

        try:
            # Amount.from_string handles natural language parsing
            amount = Amount.from_string(amount_input, currency)
            
            # Validate currency is supported
            if amount.currency not in self._supported_currencies:
                return []
            
            return [amount]
        except Exception:
            return []

    async def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currency codes.

        Returns:
            List of ISO 4217 currency codes
        """
        return list(self._supported_currencies.keys())

