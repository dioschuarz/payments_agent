"""Transfer request entity."""

from typing import Optional

from pydantic import BaseModel, Field

from src.domain.entities.beneficiary import Beneficiary
from src.domain.value_objects.amount import Amount
from src.domain.value_objects.country import Country
from src.domain.value_objects.delivery_method import DeliveryMethod


class TransferRequest(BaseModel):
    """Represents a money transfer request."""

    beneficiary: Optional[Beneficiary] = Field(None, description="Transfer beneficiary")
    amount: Optional[Amount] = Field(None, description="Transfer amount")
    country: Optional[Country] = Field(None, description="Destination country")
    delivery_method: Optional[DeliveryMethod] = Field(None, description="Delivery method")

    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        return all(
            [
                self.beneficiary is not None,
                self.amount is not None,
                self.country is not None,
                self.delivery_method is not None,
            ]
        )

    def get_missing_fields(self) -> list[str]:
        """Get list of missing required fields."""
        missing = []
        if self.beneficiary is None:
            missing.append("beneficiary")
        if self.amount is None:
            missing.append("amount")
        if self.country is None:
            missing.append("country")
        if self.delivery_method is None:
            missing.append("delivery_method")
        return missing

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "beneficiary": self.beneficiary.model_dump() if self.beneficiary else None,
            "amount": {
                "value": str(self.amount.value),
                "currency": self.amount.currency,
            }
            if self.amount
            else None,
            "country": self.country.model_dump() if self.country else None,
            "delivery_method": self.delivery_method.model_dump() if self.delivery_method else None,
        }

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"TransferRequest(beneficiary={self.beneficiary}, "
            f"amount={self.amount}, country={self.country}, "
            f"delivery_method={self.delivery_method})"
        )

