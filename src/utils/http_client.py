"""
HTTP client with retry logic and error handling.
Uses tenacity for exponential backoff retries.
"""
import logging
from typing import Optional, Dict, Any
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)


def create_retry_decorator(max_attempts: int = 3, min_wait: float = 1, max_wait: float = 10):
    """Create a retry decorator with configurable parameters."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


class APIClient:
    """
    Reusable HTTP client with retry logic, timeouts, and error handling.
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 15.0,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.Client] = None
        self._retry = create_retry_decorator(max_attempts=max_retries)

    @property
    def client(self) -> httpx.Client:
        """Lazy-initialize the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout,
            )
        return self._client

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request with retry logic.

        Args:
            path: URL path (will be appended to base_url)
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        @self._retry
        def _get():
            response = self.client.get(path, params=params)
            response.raise_for_status()
            return response.json()

        return _get()

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request with retry logic.

        Args:
            path: URL path (will be appended to base_url)
            json: JSON body

        Returns:
            JSON response as dictionary
        """
        @self._retry
        def _post():
            response = self.client.post(path, json=json)
            response.raise_for_status()
            return response.json()

        return _post()

    def close(self):
        """Close the HTTP client connection."""
        if self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Pre-configured clients for common APIs
def get_dexscreener_client() -> APIClient:
    """Get a client configured for DexScreener API."""
    return APIClient(
        base_url="https://api.dexscreener.com",
        timeout=15.0,
    )


def get_helius_client(api_key: str) -> APIClient:
    """Get a client configured for Helius API."""
    return APIClient(
        base_url="https://api.helius.xyz",
        headers={"Content-Type": "application/json"},
        timeout=15.0,
    )


def get_birdeye_client(api_key: str) -> APIClient:
    """Get a client configured for Birdeye API."""
    return APIClient(
        base_url="https://public-api.birdeye.so",
        headers={
            "X-API-KEY": api_key,
            "x-chain": "solana",
            "accept": "application/json",
        },
        timeout=15.0,
    )
