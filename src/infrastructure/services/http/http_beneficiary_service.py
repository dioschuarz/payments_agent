"""HTTP client for beneficiary microservice."""

from typing import List

from src.domain.entities.beneficiary import Beneficiary
from src.infrastructure.services.http.base_http_service import BaseHttpService
from src.infrastructure.services.interfaces.ibeneficiary_service import IBeneficiaryService


class HttpBeneficiaryService(BaseHttpService):
    """HTTP service client for beneficiary lookups."""

    async def find_beneficiaries(self, name_fragment: str) -> List[Beneficiary]:
        """
        Find beneficiaries matching the name fragment.

        Args:
            name_fragment: Partial or full name to search for

        Returns:
            List of matching beneficiaries
        """
        response = await self.get("/beneficiaries/search", params={"q": name_fragment})
        
        # Convert response to Beneficiary entities
        beneficiaries = []
        for item in response.get("results", []):
            beneficiaries.append(Beneficiary(**item))
        
        return beneficiaries

