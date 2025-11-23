"""Interface for delivery method service."""

from typing import List, Protocol

from src.domain.value_objects.delivery_method import DeliveryMethod


class IDeliveryMethodService(Protocol):
    """Protocol for delivery method validation service."""

    async def validate_delivery_method(self, method_input: str) -> List[DeliveryMethod]:
        """
        Validate and parse delivery method from input.

        Args:
            method_input: Delivery method string

        Returns:
            List containing single valid DeliveryMethod, or empty list if invalid
        """
        ...

    async def get_available_methods(self) -> List[DeliveryMethod]:
        """
        Get list of available delivery methods.

        Returns:
            List of available delivery methods
        """
        ...

