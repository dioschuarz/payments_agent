"""Mock beneficiary service for development."""

from typing import List

from src.domain.entities.beneficiary import Beneficiary
from src.infrastructure.mocks.data_loader import DataLoader
from src.infrastructure.services.interfaces.ibeneficiary_service import IBeneficiaryService


class MockBeneficiaryService:
    """Mock service for beneficiary lookups using JSON data."""

    def __init__(self, data_loader: DataLoader = None):
        """
        Initialize with mock data from JSON.

        Args:
            data_loader: Optional data loader (creates default if not provided)
        """
        if data_loader is None:
            data_loader = DataLoader()
        self._data_loader = data_loader
        self._load_beneficiaries()

    def _load_beneficiaries(self):
        """Load beneficiaries from JSON file."""
        data = self._data_loader.load_beneficiaries()
        self._beneficiaries = [
            Beneficiary(**item) for item in data
        ]

    async def find_beneficiaries(self, name_fragment: str) -> List[Beneficiary]:
        """
        Find beneficiaries matching the name fragment.

        Args:
            name_fragment: Partial or full name to search for

        Returns:
            List of matching beneficiaries (can be empty, single, or multiple)
        """
        name_lower = name_fragment.lower().strip()

        # Exact match first
        exact_matches = [
            b for b in self._beneficiaries if b.name.lower() == name_lower
        ]

        if exact_matches:
            return exact_matches

        # Partial match
        matches = [
            b
            for b in self._beneficiaries
            if name_lower in b.name.lower() or b.name.lower().startswith(name_lower)
        ]

        return matches

