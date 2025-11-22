"""Beneficiary validator."""

from typing import List

from src.domain.entities.beneficiary import Beneficiary
from src.infrastructure.services.interfaces.ibeneficiary_service import IBeneficiaryService


class BeneficiaryValidator:
    """Validates and finds beneficiaries."""

    def __init__(
        self,
        beneficiary_service: IBeneficiaryService,
    ):
        """
        Initialize beneficiary validator.

        Args:
            beneficiary_service: Service for beneficiary lookups
        """
        self._service = beneficiary_service

    async def find_beneficiaries(self, name: str) -> List[Beneficiary]:
        """
        Find beneficiaries by name.

        Args:
            name: Beneficiary name or fragment

        Returns:
            List of matching beneficiaries

        Note: Caching is handled by ADK memory service if needed.
        """
        # Query service directly - ADK may cache tool results automatically
        matches = await self._service.find_beneficiaries(name)
        return matches

