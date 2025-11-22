"""Country validator."""

from typing import List, Optional

from src.domain.value_objects.country import Country
from src.infrastructure.services.interfaces.icountry_service import ICountryService


class CountryValidator:
    """Validates and resolves countries."""

    def __init__(
        self,
        country_service: ICountryService,
    ):
        """
        Initialize country validator.

        Args:
            country_service: Service for country validation
        """
        self._service = country_service

    async def validate_country(self, country_input: str) -> List[Country]:
        """
        Validate and resolve country from input.

        Args:
            country_input: Country name or code

        Returns:
            List of matching countries (usually single match, but can be multiple for ambiguity)

        Note: Caching is handled by ADK memory service if needed.
        """
        # Query service directly - ADK may cache tool results automatically
        result = await self._service.validate_country(country_input)
        return result

