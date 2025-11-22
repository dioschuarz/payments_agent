"""Delivery method value object."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DeliveryMethodType(str, Enum):
    """Delivery method types."""

    BANK_TRANSFER = "bank_transfer"
    MOBILE_WALLET = "mobile_wallet"
    CASH_PICKUP = "cash_pickup"
    HOME_DELIVERY = "home_delivery"


class DeliveryMethod(BaseModel):
    """Represents a delivery method for money transfer."""

    method: DeliveryMethodType = Field(..., description="Delivery method type")
    provider: Optional[str] = Field(None, description="Provider name (e.g., 'Western Union')")

    @classmethod
    def from_string(cls, method_str: str) -> Optional["DeliveryMethod"]:
        """Create DeliveryMethod from string representation."""
        method_lower = method_str.lower().strip()

        # Mapping common terms to delivery methods
        method_map = {
            "bank": DeliveryMethodType.BANK_TRANSFER,
            "bank transfer": DeliveryMethodType.BANK_TRANSFER,
            "transfer": DeliveryMethodType.BANK_TRANSFER,
            "mobile": DeliveryMethodType.MOBILE_WALLET,
            "mobile wallet": DeliveryMethodType.MOBILE_WALLET,
            "wallet": DeliveryMethodType.MOBILE_WALLET,
            "cash": DeliveryMethodType.CASH_PICKUP,
            "cash pickup": DeliveryMethodType.CASH_PICKUP,
            "pickup": DeliveryMethodType.CASH_PICKUP,
            "home": DeliveryMethodType.HOME_DELIVERY,
            "home delivery": DeliveryMethodType.HOME_DELIVERY,
            "delivery": DeliveryMethodType.HOME_DELIVERY,
        }

        method_type = method_map.get(method_lower)
        if method_type:
            return cls(method=method_type)

        # Try direct enum match
        try:
            return cls(method=DeliveryMethodType(method_lower))
        except ValueError:
            return None

    def __str__(self) -> str:
        """String representation."""
        return self.method.value.replace("_", " ").title()

    def __repr__(self) -> str:
        """Developer representation."""
        return f"DeliveryMethod(method='{self.method.value}')"

