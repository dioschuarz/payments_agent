"""Interface for beneficiary service."""

from typing import List, Protocol

from src.domain.entities.beneficiary import Beneficiary


class IBeneficiaryService(Protocol):
    """Protocol for beneficiary lookup service."""

    async def find_beneficiaries(self, name_fragment: str) -> List[Beneficiary]:
        """
        Find beneficiaries matching the name fragment.

        Args:
            name_fragment: Partial or full name to search for

        Returns:
            List of matching beneficiaries (can be empty, single, or multiple)
        """
        ...

