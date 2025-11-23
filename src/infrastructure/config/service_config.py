"""Service configuration loader."""

import os
from pathlib import Path
from typing import Dict, Optional

import yaml


class ServiceConfig:
    """Service configuration manager."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize service configuration.

        Args:
            config_path: Path to services_config.yaml (defaults to src/infrastructure/config/services_config.yaml)
        """
        if config_path is None:
            base_path = Path(__file__).parent
            config_path = str(base_path / "services_config.yaml")
        
        self._config_path = Path(config_path)
        if not self._config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        with open(self._config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    def get_service_config(self, service_name: str) -> Dict:
        """
        Get configuration for a specific service.

        Args:
            service_name: Name of the service (e.g., "beneficiary", "country")

        Returns:
            Service configuration dictionary
        """
        services = self._config.get("services", {})
        return services.get(service_name, {})

    def get_service_type(self, service_name: str) -> str:
        """
        Get service type (mock or http).

        Args:
            service_name: Name of the service

        Returns:
            Service type ("mock" or "http")
        """
        config = self.get_service_config(service_name)
        return config.get("type", "mock")

    def get_base_url(self, service_name: str) -> str:
        """
        Get base URL for HTTP service.

        Args:
            service_name: Name of the service

        Returns:
            Base URL string
        """
        config = self.get_service_config(service_name)
        return config.get("base_url", "")

    def get_timeout(self, service_name: str) -> float:
        """
        Get timeout for HTTP service.

        Args:
            service_name: Name of the service

        Returns:
            Timeout in seconds
        """
        config = self.get_service_config(service_name)
        return config.get("timeout", 5.0)

    def get_retries(self, service_name: str) -> int:
        """
        Get retry count for HTTP service.

        Args:
            service_name: Name of the service

        Returns:
            Number of retries
        """
        config = self.get_service_config(service_name)
        return config.get("retries", 3)

    def get_api_key(self, service_name: str) -> Optional[str]:
        """
        Get API key for HTTP service (from config or environment).

        Args:
            service_name: Name of the service

        Returns:
            API key or None
        """
        config = self.get_service_config(service_name)
        api_key = config.get("api_key")
        
        # Check environment variable if not in config
        if not api_key:
            env_var = f"{service_name.upper()}_API_KEY"
            api_key = os.getenv(env_var)
        
        return api_key

