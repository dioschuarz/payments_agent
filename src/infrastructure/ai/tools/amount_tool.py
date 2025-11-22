"""ADK Tool for amount validation."""

from google.adk.tools import FunctionTool

from src.infrastructure.validators.amount_validator import AmountValidator


def create_amount_tool(validator: AmountValidator) -> FunctionTool:
    """
    Create ADK tool for amount validation.

    Args:
        validator: Amount validator instance

    Returns:
        FunctionTool for validating amounts
    """
    async def validate_amount(amount_input: str, currency: str = "USD") -> dict:
        """
        Validate amount from input string.

        Args:
            amount_input: Amount string (can include currency)
            currency: Default currency if not detected in input

        Returns:
            Dictionary with 'valid' (bool), 'amount' (dict with value/currency), and optional 'error' (str)
        """
        matches = await validator.validate_amount(amount_input, currency)
        
        if matches and len(matches) == 1:
            amount = matches[0]
            return {
                "valid": True,
                "amount": {
                    "value": str(amount.value),
                    "currency": amount.currency,
                },
            }
        
        return {
            "valid": False,
            "error": f"Could not parse amount from: {amount_input}",
        }
    
    return FunctionTool(validate_amount)

