"""Delivery method validator."""

from typing import List

from src.domain.value_objects.delivery_method import DeliveryMethod
from src.infrastructure.services.interfaces.idelivery_method_service import IDeliveryMethodService


class DeliveryMethodValidator:
    """Validates delivery methods."""

    def __init__(
        self,
        delivery_method_service: IDeliveryMethodService,
    ):
        """
        Initialize delivery method validator.

        Args:
            delivery_method_service: Service for delivery method validation
        """
        self._service = delivery_method_service

    async def validate_delivery_method(self, method_input: str) -> List[DeliveryMethod]:
        """
        Validate and parse delivery method from input.

        Args:
            method_input: Delivery method string

        Returns:
            List containing single valid DeliveryMethod, or empty list if invalid

        Note: Caching is handled by ADK memory service if needed.
        """
        # Query service directly - ADK may cache tool results automatically
        result = await self._service.validate_delivery_method(method_input)
        return result

