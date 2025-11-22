"""Country value object."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.domain.value_objects.countries_data import (
    get_country_code,
    get_country_name,
)


class Country(BaseModel):
    """Represents a country."""

    code: str = Field(..., description="ISO 3166-1 alpha-2 country code")
    name: str = Field(..., description="Country name")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate country code."""
        if not v or len(v) != 2:
            raise ValueError("Country code must be a 2-letter ISO 3166-1 alpha-2 code")
        return v.upper()

    @classmethod
    def from_name(cls, name: str) -> Optional["Country"]:
        """Create Country from name (with fuzzy matching)."""
        # Use shared country data
        result = get_country_code(name)
        if result:
            code, official_name = result
            return cls(code=code, name=official_name)

        # If input is a 2-letter code, try to create country directly
        if len(name.strip()) == 2:
            try:
                return cls._from_code(name.upper())
            except Exception:
                pass

        return None

    @classmethod
    def _from_code(cls, code: str) -> Optional["Country"]:
        """Create Country from ISO 3166-1 alpha-2 code."""
        # Use shared country data
        name = get_country_name(code)
        if name:
            return cls(code=code.upper(), name=name)
        
        # If code not in our list, create with code as name (fallback)
        try:
            return cls(code=code.upper(), name=code.upper())
        except Exception:
            return None

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name} ({self.code})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Country(code='{self.code}', name='{self.name}')"

