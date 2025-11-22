"""Amount value object."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Amount(BaseModel):
    """Represents a monetary amount."""

    value: Decimal = Field(..., gt=0, description="Amount value must be positive")
    currency: str = Field(default="USD", description="Currency code (ISO 4217)")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if not v or len(v) != 3:
            raise ValueError("Currency must be a 3-letter ISO 4217 code")
        return v.upper()

    @classmethod
    def from_string(cls, amount_str: str, currency: str = "USD") -> "Amount":
        """
        Create Amount from string representation.
        
        Handles various formats:
        - "100", "$100", "100 USD", "100 dollars", "100 reais", "R$ 100", etc.
        """
        import re
        
        # Currency name to code mapping
        currency_map = {
            "dollar": "USD", "dollars": "USD", "usd": "USD",
            "real": "BRL", "reais": "BRL", "brl": "BRL",
            "euro": "EUR", "euros": "EUR", "eur": "EUR",
            "pound": "GBP", "pounds": "GBP", "gbp": "GBP",
            "peso": "MXN", "pesos": "MXN", "mxn": "MXN",
        }
        
        text = amount_str.strip()
        original_text = text
        text_lower = text.lower()
        
        # Check for currency symbols first (before removing them)
        detected_currency = currency
        if "r$" in text_lower or text.startswith("R$"):
            detected_currency = "BRL"
            text = re.sub(r"r\$\s*", "", text, flags=re.IGNORECASE)
        elif "$" in text and "r$" not in text_lower:
            detected_currency = "USD"
        elif "€" in text:
            detected_currency = "EUR"
        elif "£" in text:
            detected_currency = "GBP"
        
        # Check for currency names
        for currency_name, currency_code in currency_map.items():
            if currency_name in text_lower:
                detected_currency = currency_code
                # Remove currency name from text
                text = re.sub(rf"\b{re.escape(currency_name)}\b", "", text, flags=re.IGNORECASE)
                break
        
        # Remove remaining currency symbols
        text = re.sub(r"[$€£]", "", text, flags=re.IGNORECASE)
        
        # Extract number (handles decimals, commas, spaces)
        number_match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
        if not number_match:
            raise ValueError(f"Could not extract number from: {amount_str}")
        
        try:
            # Remove commas and convert to Decimal
            number_str = number_match.group(0).replace(",", "")
            value = Decimal(number_str)
            
            if value <= 0:
                raise ValueError(f"Amount must be positive: {value}")
            
            return cls(value=value, currency=detected_currency)
        except (ValueError, Exception) as e:
            raise ValueError(f"Invalid amount format: {amount_str}") from e

    def __str__(self) -> str:
        """String representation."""
        return f"{self.currency} {self.value}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Amount(value={self.value}, currency='{self.currency}')"

