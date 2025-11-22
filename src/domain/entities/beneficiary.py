"""Beneficiary entity."""

from typing import Optional

from pydantic import BaseModel, Field


class Beneficiary(BaseModel):
    """Represents a money transfer beneficiary."""

    id: str = Field(..., description="Unique beneficiary identifier")
    name: str = Field(..., description="Full name of the beneficiary")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    account_number: Optional[str] = Field(None, description="Account number (for bank transfers)")

    def __str__(self) -> str:
        """String representation."""
        return self.name

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Beneficiary(id='{self.id}', name='{self.name}')"

