"""Base HTTP service client with connection pooling and retries."""

import asyncio
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class BaseHttpService:
    """Base HTTP service with connection pooling, retries, and error handling."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        api_key: Optional[str] = None,
    ):
        """
        Initialize base HTTP service.

        Args:
            base_url: Base URL for the service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            api_key: Optional API key for authentication
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._api_key = api_key

        # Create HTTP client with connection pooling
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request with retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (relative to base_url)
            params: Query parameters
            json_data: JSON body
            headers: Additional headers

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPError: If request fails after retries
        """
        request_headers = {}
        if self._api_key:
            request_headers["Authorization"] = f"Bearer {self._api_key}"
        if headers:
            request_headers.update(headers)

        last_error = None
        for attempt in range(self._max_retries):
            try:
                response = await self._client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self._max_retries}): {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Request failed after {self._max_retries} attempts: {e}")
                    raise

        raise last_error

    async def get(self, path: str, params: Optional[dict] = None) -> dict:
        """Make GET request."""
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json_data: Optional[dict] = None) -> dict:
        """Make POST request."""
        return await self._request("POST", path, json_data=json_data)

    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

