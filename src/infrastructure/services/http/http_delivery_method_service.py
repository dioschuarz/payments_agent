"""HTTP client for delivery method microservice."""

from typing import List

from src.domain.value_objects.delivery_method import DeliveryMethod, DeliveryMethodType
from src.infrastructure.services.http.base_http_service import BaseHttpService
from src.infrastructure.services.interfaces.idelivery_method_service import IDeliveryMethodService


class HttpDeliveryMethodService(BaseHttpService):
    """HTTP service client for delivery method validation."""

    async def validate_delivery_method(self, method_input: str) -> List[DeliveryMethod]:
        """
        Validate and parse delivery method from input.

        Args:
            method_input: Delivery method string

        Returns:
            List containing single valid DeliveryMethod, or empty list if invalid
        """
        response = await self.get("/delivery-methods/validate", params={"q": method_input})
        
        if response.get("valid"):
            result = response.get("result", {})
            method_type = DeliveryMethodType(result["method"])
            return [DeliveryMethod(method=method_type, provider=result.get("provider"))]
        
        return []

    async def get_available_methods(self) -> List[DeliveryMethod]:
        """
        Get list of available delivery methods.

        Returns:
            List of available delivery methods
        """
        response = await self.get("/delivery-methods")
        
        methods = []
        for item in response.get("results", []):
            method_type = DeliveryMethodType(item["method"])
            methods.append(DeliveryMethod(method=method_type, provider=item.get("provider")))
        
        return methods

