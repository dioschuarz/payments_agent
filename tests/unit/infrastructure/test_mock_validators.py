"""Mock Validators for Testing.

Provides MockCountryValidator and MockBeneficiaryService
as specified in the test plan.
"""

from typing import List

from src.domain.entities.beneficiary import Beneficiary
from src.domain.value_objects.country import Country
from src.infrastructure.services.interfaces.ibeneficiary_service import IBeneficiaryService
from src.infrastructure.services.interfaces.icountry_service import ICountryService


class MockCountryValidator:
    """
    Mock Country Validator for testing.
    
    validate("US") -> True
    validate("Narnia") -> False
    """
    
    VALID_COUNTRIES = {"US", "BR", "FR", "GB", "CA", "MX"}
    
    @staticmethod
    def validate(country_input: str) -> bool:
        """Validate country input."""
        country = Country.from_name(country_input)
        if country is None:
            return False
        return country.code in MockCountryValidator.VALID_COUNTRIES


class MockBeneficiaryService(IBeneficiaryService):
    """
    Mock Beneficiary Service for testing ambiguity scenarios.
    
    lookup("John") -> ["John Doe", "John Smith"] (Ambiguous)
    lookup("John Doe") -> ["John Doe"] (Exact)
    lookup("Unknown") -> [] (Empty)
    """
    
    _beneficiaries = [
        Beneficiary(id="1", name="John Doe", phone="+1234567890"),
        Beneficiary(id="2", name="John Smith", phone="+1234567891"),
        Beneficiary(id="3", name="Jane Doe", phone="+1234567892"),
    ]
    
    async def find_beneficiaries(self, name: str) -> List[Beneficiary]:
        """
        Find beneficiaries by name.
        
        Args:
            name: Name to search for
            
        Returns:
            List of matching beneficiaries
        """
        name_lower = name.lower()
        matches = [
            b for b in self._beneficiaries
            if name_lower in b.name.lower()
        ]
        return matches

