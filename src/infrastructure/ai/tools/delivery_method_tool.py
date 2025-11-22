"""ADK Tool for delivery method validation."""

from google.adk.tools import FunctionTool

from src.infrastructure.validators.delivery_method_validator import DeliveryMethodValidator


def create_delivery_method_tool(validator: DeliveryMethodValidator) -> FunctionTool:
    """
    Create ADK tool for delivery method validation.

    Args:
        validator: Delivery method validator instance

    Returns:
        FunctionTool for validating delivery methods
    """
    async def validate_delivery_method(method_input: str) -> dict:
        """
        Validate delivery method from input.

        Args:
            method_input: Delivery method string (e.g., 'bank transfer', 'mobile wallet', 'cash pickup', 'home delivery')

        Returns:
            Dictionary with 'valid' (bool), 'method' (dict with method/provider), and optional 'error' (str)
        """
        matches = await validator.validate_delivery_method(method_input)
        
        if matches and len(matches) == 1:
            method = matches[0]
            return {
                "valid": True,
                "method": {
                    "method": method.method.value,
                    "provider": method.provider,
                },
            }
        
        return {
            "valid": False,
            "error": f"Invalid delivery method: {method_input}",
        }
    
    return FunctionTool(validate_delivery_method)

