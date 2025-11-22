"""Service factory for creating service instances based on configuration."""

from src.domain.entities.beneficiary import Beneficiary
from src.infrastructure.config.service_config import ServiceConfig
from src.infrastructure.mocks.data_loader import DataLoader
from src.infrastructure.services.http.base_http_service import BaseHttpService
from src.infrastructure.services.http.http_amount_validation_service import HttpAmountValidationService
from src.infrastructure.services.http.http_beneficiary_service import HttpBeneficiaryService
from src.infrastructure.services.http.http_country_service import HttpCountryService
from src.infrastructure.services.http.http_delivery_method_service import HttpDeliveryMethodService
from src.infrastructure.services.interfaces.iamount_validation_service import IAmountValidationService
from src.infrastructure.services.interfaces.ibeneficiary_service import IBeneficiaryService
from src.infrastructure.services.interfaces.icountry_service import ICountryService
from src.infrastructure.services.interfaces.idelivery_method_service import IDeliveryMethodService
from src.infrastructure.services.mocks.mock_amount_validation_service import MockAmountValidationService
from src.infrastructure.mocks.mock_beneficiary_service import MockBeneficiaryService
from src.infrastructure.services.mocks.mock_country_service import MockCountryService
from src.infrastructure.services.mocks.mock_delivery_method_service import MockDeliveryMethodService


class ServiceFactory:
    """Factory for creating service instances based on configuration."""

    def __init__(self, config: ServiceConfig = None):
        """
        Initialize service factory.

        Args:
            config: Service configuration (creates default if not provided)
        """
        if config is None:
            config = ServiceConfig()
        self._config = config
        self._data_loader = DataLoader()

    def create_beneficiary_service(self) -> IBeneficiaryService:
        """
        Create beneficiary service (mock or HTTP).

        Returns:
            Beneficiary service instance
        """
        service_type = self._config.get_service_type("beneficiary")
        
        if service_type == "http":
            return HttpBeneficiaryService(
                base_url=self._config.get_base_url("beneficiary"),
                timeout=self._config.get_timeout("beneficiary"),
                max_retries=self._config.get_retries("beneficiary"),
                api_key=self._config.get_api_key("beneficiary"),
            )
        else:
            return MockBeneficiaryService(data_loader=self._data_loader)

    def create_country_service(self) -> ICountryService:
        """
        Create country service (mock or HTTP).

        Returns:
            Country service instance
        """
        service_type = self._config.get_service_type("country")
        
        if service_type == "http":
            return HttpCountryService(
                base_url=self._config.get_base_url("country"),
                timeout=self._config.get_timeout("country"),
                max_retries=self._config.get_retries("country"),
                api_key=self._config.get_api_key("country"),
            )
        else:
            return MockCountryService(data_loader=self._data_loader)

    def create_amount_validation_service(self) -> IAmountValidationService:
        """
        Create amount validation service (mock or HTTP).

        Returns:
            Amount validation service instance
        """
        service_type = self._config.get_service_type("amount_validation")
        
        if service_type == "http":
            return HttpAmountValidationService(
                base_url=self._config.get_base_url("amount_validation"),
                timeout=self._config.get_timeout("amount_validation"),
                max_retries=self._config.get_retries("amount_validation"),
                api_key=self._config.get_api_key("amount_validation"),
            )
        else:
            return MockAmountValidationService(data_loader=self._data_loader)

    def create_delivery_method_service(self) -> IDeliveryMethodService:
        """
        Create delivery method service (mock or HTTP).

        Returns:
            Delivery method service instance
        """
        service_type = self._config.get_service_type("delivery_method")
        
        if service_type == "http":
            return HttpDeliveryMethodService(
                base_url=self._config.get_base_url("delivery_method"),
                timeout=self._config.get_timeout("delivery_method"),
                max_retries=self._config.get_retries("delivery_method"),
                api_key=self._config.get_api_key("delivery_method"),
            )
        else:
            return MockDeliveryMethodService(data_loader=self._data_loader)

