"""Mock delivery method service using JSON data."""

from typing import List

from src.domain.value_objects.delivery_method import DeliveryMethod, DeliveryMethodType
from src.infrastructure.mocks.data_loader import DataLoader
from src.infrastructure.services.interfaces.idelivery_method_service import IDeliveryMethodService


class MockDeliveryMethodService:
    """Mock service for delivery method validation using JSON data."""

    def __init__(self, data_loader: DataLoader = None):
        """
        Initialize with mock data from JSON.

        Args:
            data_loader: Optional data loader (creates default if not provided)
        """
        if data_loader is None:
            data_loader = DataLoader()
        self._data_loader = data_loader
        self._load_delivery_methods()

    def _load_delivery_methods(self):
        """Load delivery methods from JSON file."""
        data = self._data_loader.load_delivery_methods()
        self._methods = {}
        self._aliases = {}
        
        for item in data:
            code = item["code"]
            aliases = item.get("aliases", [])
            
            # Map code to DeliveryMethodType
            try:
                method_type = DeliveryMethodType(code)
                self._methods[code] = DeliveryMethod(method=method_type)
                
                # Store aliases
                for alias in aliases:
                    self._aliases[alias.lower()] = code
                # Also store code and name as aliases
                self._aliases[code.lower()] = code
            except ValueError:
                # Skip invalid method types
                pass

    async def validate_delivery_method(self, method_input: str) -> List[DeliveryMethod]:
        """
        Validate and parse delivery method from input.

        Args:
            method_input: Delivery method string

        Returns:
            List containing single valid DeliveryMethod, or empty list if invalid
        """
        method_lower = method_input.lower().strip()
        
        # Check aliases first
        code = self._aliases.get(method_lower)
        if code and code in self._methods:
            return [self._methods[code]]
        
        # Try direct code lookup
        if method_lower in self._methods:
            return [self._methods[method_lower]]
        
        # Try DeliveryMethod.from_string as fallback
        method = DeliveryMethod.from_string(method_input)
        if method:
            return [method]
        
        return []

    async def get_available_methods(self) -> List[DeliveryMethod]:
        """
        Get list of available delivery methods.

        Returns:
            List of available delivery methods
        """
        return list(self._methods.values())

