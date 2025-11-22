"""Interface for amount validation service."""

from typing import List, Protocol

from src.domain.value_objects.amount import Amount


class IAmountValidationService(Protocol):
    """Protocol for amount validation service."""

    async def validate_amount(self, amount_input: str, currency: str = "USD") -> List[Amount]:
        """
        Validate and parse amount from input.

        Args:
            amount_input: Amount string (can include currency name or symbol)
            currency: Default currency code (used if currency not detected in input)

        Returns:
            List containing single valid Amount, or empty list if invalid
        """
        ...

    async def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currency codes.

        Returns:
            List of ISO 4217 currency codes
        """
        ...

