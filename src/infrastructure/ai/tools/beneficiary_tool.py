"""ADK Tool for beneficiary validation."""

from typing import List

from google.adk.tools import FunctionTool

from src.domain.entities.beneficiary import Beneficiary
from src.infrastructure.validators.beneficiary_validator import BeneficiaryValidator


def create_beneficiary_tool(validator: BeneficiaryValidator) -> FunctionTool:
    """
    Create ADK tool for beneficiary validation.

    Args:
        validator: Beneficiary validator instance

    Returns:
        FunctionTool for finding beneficiaries
    """
    async def find_beneficiaries(name: str) -> dict:
        """
        Find beneficiaries matching the given name.

        Args:
            name: Beneficiary name or fragment to search for

        Returns:
            Dictionary with 'matches' (list of beneficiary dicts) and 'is_ambiguous' (bool)
        """
        matches = await validator.find_beneficiaries(name)
        
        # Convert Beneficiary entities to dicts for output
        matches_dict = [
            {
                "id": b.id,
                "name": b.name,
                "phone": b.phone,
                "email": b.email,
            }
            for b in matches
        ]
        
        return {
            "matches": matches_dict,
            "is_ambiguous": len(matches) > 1,
        }
    
    # Create FunctionTool from the async function
    return FunctionTool(find_beneficiaries)

