"""SecBlast API client."""

from __future__ import annotations

from typing import Any

import httpx

from secblast.endpoints.documents import DocumentsMixin
from secblast.endpoints.entities import EntitiesMixin
from secblast.endpoints.filings import FilingsMixin
from secblast.endpoints.financials import FinancialsMixin
from secblast.endpoints.search import SearchMixin
from secblast.exceptions import (
    AuthenticationError,
    RateLimitError,
    SecBlastError,
    ServerError,
    ValidationError,
)

DEFAULT_BASE_URL = "https://api.secblast.com/v2"
DEFAULT_TIMEOUT = 60.0


class SecBlastClient(
    EntitiesMixin,
    FilingsMixin,
    SearchMixin,
    DocumentsMixin,
    FinancialsMixin,
):
    """
    SecBlast API client for accessing SEC filing data.

    Example:
        ```python
        from secblast import SecBlastClient

        client = SecBlastClient(api_key="your-api-key")

        # Look up a company
        entity = client.get_entity(ticker="AAPL")
        print(entity.name, entity.cik)

        # Search filings
        filings = client.lookup_filings(
            tickers=["AAPL"],
            form_types=["10-K"],
            date_from="2023-01-01",
        )

        # Full-text search
        results = client.fulltext_search(
            "material contract",
            form_types=["8-K"],
        )

        # Get financial data
        balance_sheet = client.get_balance_sheet(cik="320193")
        ```
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
    ):
        """
        Initialize the SecBlast client.

        Args:
            api_key: Your SecBlast API key
            timeout: Request timeout in seconds (default: 60)
            http_client: Custom httpx.Client instance (optional)
        """
        self.api_key = api_key
        self.base_url = DEFAULT_BASE_URL
        self.timeout = timeout

        if http_client is not None:
            self._client = http_client
            self._owns_client = False
        else:
            self._client = httpx.Client(timeout=timeout)
            self._owns_client = True

    def __enter__(self) -> "SecBlastClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        if self._owns_client:
            self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
    ) -> dict:
        """Make an API request and return JSON response."""
        url = f"{self.base_url}{path}"

        # Always include API key in the request body
        body = {"api_key": self.api_key}
        if json:
            body.update(json)

        response = self._client.request(method, url, json=body)
        return self._handle_response(response)

    def _request_raw(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
    ) -> bytes:
        """Make an API request and return raw bytes."""
        url = f"{self.base_url}{path}"

        body = {"api_key": self.api_key}
        if json:
            body.update(json)

        response = self._client.request(method, url, json=body)

        # Check for errors
        if response.status_code >= 400:
            self._handle_error(response)

        return response.content

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code >= 400:
            self._handle_error(response)

        try:
            return response.json()
        except Exception as e:
            raise SecBlastError(f"Failed to parse response: {e}")

    def _handle_error(self, response: httpx.Response) -> None:
        """Raise appropriate exception based on response status."""
        try:
            data = response.json()
            message = data.get("error", str(data))
        except Exception:
            message = response.text or f"HTTP {response.status_code}"

        status = response.status_code

        if status == 401:
            raise AuthenticationError(message)
        elif status == 429:
            limit_type = None
            if "bandwidth" in message.lower() or "byte" in message.lower():
                limit_type = "bandwidth"
            else:
                limit_type = "requests"
            raise RateLimitError(message, limit_type=limit_type)
        elif status == 400:
            raise ValidationError(message)
        elif status >= 500:
            raise ServerError(message, status_code=status)
        else:
            raise SecBlastError(message, status_code=status)

    def health_check(self) -> bool:
        """
        Check if the API is healthy.

        Returns:
            True if the API is responding normally
        """
        try:
            data = self._request("GET", "/health")
            return data.get("status") == "ok"
        except Exception:
            return False
