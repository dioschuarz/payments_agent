"""Mock country service using JSON data."""

from typing import List

from src.domain.value_objects.country import Country
from src.infrastructure.mocks.data_loader import DataLoader
from src.infrastructure.services.interfaces.icountry_service import ICountryService


class MockCountryService:
    """Mock service for country validation using JSON data."""

    def __init__(self, data_loader: DataLoader = None):
        """
        Initialize with mock data from JSON.

        Args:
            data_loader: Optional data loader (creates default if not provided)
        """
        if data_loader is None:
            data_loader = DataLoader()
        self._data_loader = data_loader
        self._load_countries()

    def _load_countries(self):
        """Load countries from JSON file."""
        data = self._data_loader.load_countries()
        self._countries = {}
        self._aliases = {}
        
        for item in data:
            code = item["code"]
            name = item["name"]
            aliases = item.get("aliases", [])
            
            # Store by code
            self._countries[code] = Country(code=code, name=name)
            
            # Store aliases
            for alias in aliases:
                self._aliases[alias.lower()] = code
            # Also store official name and code as aliases
            self._aliases[name.lower()] = code
            self._aliases[code.lower()] = code

    async def validate_country(self, country_input: str) -> List[Country]:
        """
        Validate and resolve country from input.

        Args:
            country_input: Country name or ISO code

        Returns:
            List of matching countries (usually single match)
        """
        country_lower = country_input.lower().strip()
        
        # Check aliases first
        code = self._aliases.get(country_lower)
        if code:
            return [self._countries[code]]
        
        # Try direct code lookup
        if country_lower.upper() in self._countries:
            return [self._countries[country_lower.upper()]]
        
        # Try Country.from_name as fallback (uses countries_data.py)
        country = Country.from_name(country_input)
        if country:
            return [country]
        
        return []

    async def get_all_countries(self) -> List[Country]:
        """
        Get all available countries.

        Returns:
            List of all countries
        """
        return list(self._countries.values())

