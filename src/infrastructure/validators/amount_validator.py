"""Amount validator."""

from typing import List

from src.domain.value_objects.amount import Amount
from src.infrastructure.services.interfaces.iamount_validation_service import IAmountValidationService


class AmountValidator:
    """Validates amounts."""

    def __init__(
        self,
        amount_service: IAmountValidationService,
    ):
        """
        Initialize amount validator.

        Args:
            amount_service: Service for amount validation
        """
        self._service = amount_service

    async def validate_amount(self, amount_input: str, currency: str = "USD") -> List[Amount]:
        """
        Validate and parse amount from input.
        
        Handles natural language formats:
        - "10 dollars", "10 reais", "$10", "R$ 10", "10 USD", etc.

        Args:
            amount_input: Amount string (can include currency name or symbol)
            currency: Default currency code (used if currency not detected in input)

        Returns:
            List containing single valid Amount, or empty list if invalid

        Note: Caching is handled by ADK memory service if needed.
        """
        # Query service directly - ADK may cache tool results automatically
        result = await self._service.validate_amount(amount_input, currency)
        return result

