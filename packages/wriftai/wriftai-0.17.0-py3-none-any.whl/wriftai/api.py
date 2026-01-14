"""API client module."""

from collections.abc import Mapping
from typing import Any, Optional, cast

import httpx

from wriftai.common_types import JsonValue


class API:
    """Client for WriftAI's API."""

    def __init__(
        self, sync_client: httpx.Client, async_client: httpx.AsyncClient
    ) -> None:
        """Initializes the API with synchronous and asynchronous HTTP clients.

        Args:
            sync_client: An instance of a synchronous HTTP client.
            async_client: An instance of an asynchronous HTTP client.
        """
        self._sync_client = sync_client
        self._async_client = async_client

    def request(
        self,
        method: str,
        path: str,
        body: Optional[JsonValue] = None,
        headers: Optional[dict[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> JsonValue:
        """Sends a synchronous HTTP request using the configured sync client.

        Args:
            method: The HTTP method to use (e.g., 'GET', 'POST').
            path: The URL path to send the request to.
            body: The JSON body to include in the request.
            headers: Optional HTTP headers to include in the request.
            params: Optional query parameters.


        Returns:
            The json response received from the server.
        """
        response = self._sync_client.request(
            method=method, url=path, json=body, headers=headers, params=params
        )
        response.raise_for_status()
        return cast(JsonValue, response.json())

    async def async_request(
        self,
        method: str,
        path: str,
        body: JsonValue = None,
        headers: Optional[dict[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> JsonValue:
        """Sends an asynchronous HTTP request using the configured async client.

        Args:
            method: The HTTP method to use (e.g., 'GET', 'POST').
            path: The URL path to send the request to.
            body: The JSON body to include in the request.
            headers: Optional HTTP headers to include in the request.
            params: Optional query parameters.


        Returns:
            The json response received from the server.
        """
        response = await self._async_client.request(
            method=method, url=path, json=body, headers=headers, params=params
        )
        response.raise_for_status()
        return cast(JsonValue, response.json())
