"""ADK Tool for country validation."""

from google.adk.tools import FunctionTool

from src.infrastructure.validators.country_validator import CountryValidator


def create_country_tool(validator: CountryValidator) -> FunctionTool:
    """
    Create ADK tool for country validation.

    Args:
        validator: Country validator instance

    Returns:
        FunctionTool for validating countries
    """
    async def validate_country(country_input: str) -> dict:
        """
        Validate country from input.

        Args:
            country_input: Country name or ISO code (e.g., 'USA', 'United States', 'Nigeria', 'BR')

        Returns:
            Dictionary with 'valid' (bool), 'country' (dict with code/name), and optional 'error' (str)
        """
        matches = await validator.validate_country(country_input)
        
        if matches and len(matches) == 1:
            country = matches[0]
            return {
                "valid": True,
                "country": {
                    "code": country.code,
                    "name": country.name,
                },
            }
        
        return {
            "valid": False,
            "error": f"Country not found: {country_input}",
        }
    
    return FunctionTool(validate_country)

