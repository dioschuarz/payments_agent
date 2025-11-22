"""HTTP client for country microservice."""

from typing import List

from src.domain.value_objects.country import Country
from src.infrastructure.services.http.base_http_service import BaseHttpService
from src.infrastructure.services.interfaces.icountry_service import ICountryService


class HttpCountryService(BaseHttpService):
    """HTTP service client for country validation."""

    async def validate_country(self, country_input: str) -> List[Country]:
        """
        Validate and resolve country from input.

        Args:
            country_input: Country name or ISO code

        Returns:
            List of matching countries
        """
        response = await self.get("/countries/validate", params={"q": country_input})
        
        # Convert response to Country entities
        countries = []
        for item in response.get("results", []):
            countries.append(Country(code=item["code"], name=item["name"]))
        
        return countries

    async def get_all_countries(self) -> List[Country]:
        """
        Get all available countries.

        Returns:
            List of all countries
        """
        response = await self.get("/countries")
        
        countries = []
        for item in response.get("results", []):
            countries.append(Country(code=item["code"], name=item["name"]))
        
        return countries

