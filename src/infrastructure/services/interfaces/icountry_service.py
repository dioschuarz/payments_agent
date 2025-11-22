"""Interface for country service."""

from typing import List, Protocol

from src.domain.value_objects.country import Country


class ICountryService(Protocol):
    """Protocol for country validation and lookup service."""

    async def validate_country(self, country_input: str) -> List[Country]:
        """
        Validate and resolve country from input.

        Args:
            country_input: Country name or ISO code

        Returns:
            List of matching countries (usually single match, but can be multiple for ambiguity)
        """
        ...

    async def get_all_countries(self) -> List[Country]:
        """
        Get all available countries.

        Returns:
            List of all countries
        """
        ...

