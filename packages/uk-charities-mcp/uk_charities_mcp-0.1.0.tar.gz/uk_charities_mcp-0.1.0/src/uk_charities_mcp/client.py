"""Charity Commission for England & Wales (CCEW) API client."""

import os
from typing import Any

import httpx

CCEW_BASE_URL = "https://api.charitycommission.gov.uk/register/api"


class CCEWError(Exception):
    """Error from CCEW API."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class CCEWClient:
    """Async client for the Charity Commission API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("CCEW_API_KEY")
        if not self.api_key:
            raise ValueError(
                "CCEW API key required. Set CCEW_API_KEY environment variable."
            )
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=CCEW_BASE_URL,
                headers={
                    "Ocp-Apim-Subscription-Key": self.api_key,
                    "Accept": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request(self, endpoint: str) -> Any:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint path (e.g., "allcharitydetails/202918/0")

        Returns:
            Parsed JSON response.

        Raises:
            CCEWError: If the API returns an error.
        """
        client = await self._get_client()
        response = await client.get(f"/{endpoint}")

        if response.status_code == 404:
            raise CCEWError("Charity not found", status_code=404)

        if response.status_code != 200:
            raise CCEWError(
                f"API error: {response.status_code}", status_code=response.status_code
            )

        return response.json()

    async def get_charity_details(self, registration_number: int) -> dict[str, Any]:
        """Get full details for a charity.

        Args:
            registration_number: The charity's registration number.

        Returns:
            Full charity details including trustees and classifications.
        """
        return await self._request(f"allcharitydetails/{registration_number}/0")

    async def get_financial_history(self, registration_number: int) -> list[dict[str, Any]]:
        """Get financial history for a charity.

        Args:
            registration_number: The charity's registration number.

        Returns:
            List of financial records (up to 5 years).
        """
        return await self._request(f"charityfinancialhistory/{registration_number}/0")

    async def get_governing_document(self, registration_number: int) -> dict[str, Any]:
        """Get governing document info for a charity.

        Args:
            registration_number: The charity's registration number.

        Returns:
            Governing document details including charitable objects.
        """
        return await self._request(f"charitygoverningdocument/{registration_number}/0")

    async def __aenter__(self) -> "CCEWClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
