"""HTTP client for amount validation microservice."""

from typing import List

from src.domain.value_objects.amount import Amount
from src.infrastructure.services.http.base_http_service import BaseHttpService
from src.infrastructure.services.interfaces.iamount_validation_service import IAmountValidationService


class HttpAmountValidationService(BaseHttpService):
    """HTTP service client for amount validation."""

    async def validate_amount(self, amount_input: str, currency: str = "USD") -> List[Amount]:
        """
        Validate and parse amount from input.

        Args:
            amount_input: Amount string (can include currency name or symbol)
            currency: Default currency code (used if currency not detected in input)

        Returns:
            List containing single valid Amount, or empty list if invalid
        """
        response = await self.post(
            "/validation/amount",
            json_data={"amount": amount_input, "currency": currency},
        )
        
        if response.get("valid"):
            result = response.get("result", {})
            return [Amount(value=result["value"], currency=result["currency"])]
        
        return []

    async def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currency codes.

        Returns:
            List of ISO 4217 currency codes
        """
        response = await self.get("/currencies")
        return response.get("currencies", [])

