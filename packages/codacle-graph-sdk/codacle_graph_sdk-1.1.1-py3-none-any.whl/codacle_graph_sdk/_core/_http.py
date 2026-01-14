"""HTTP client wrapper for API communication."""

from __future__ import annotations

from typing import Any

import httpx

from ..exceptions import raise_for_error
from ..exceptions.auth import AuthenticationError
from ..exceptions.network import NetworkError
from ._validation import validate_api_key


class HttpClient:
    """Sync HTTP client."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
    ):
        # Validate API key before creating client
        try:
            validated_key = validate_api_key(api_key)
        except ValueError as e:
            raise AuthenticationError(str(e), status_code=None) from e

        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"x-api-key": validated_key},
            timeout=timeout,
        )

    def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            resp = self._client.request(method, path, json=json, params=params)
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except httpx.ConnectError as e:
            raise NetworkError(f"Connection failed: {e}") from e
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

        data = resp.json() if resp.content else {}

        if resp.status_code >= 400:
            raise_for_error(resp.status_code, data)

        return data

    def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return self._request("GET", path, params=params)

    def post(
        self, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return self._request("POST", path, json=json)

    def put(
        self, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return self._request("PUT", path, json=json)

    def delete(self, path: str) -> dict[str, Any]:
        return self._request("DELETE", path)

    def close(self) -> None:
        self._client.close()


class AsyncHttpClient:
    """Async HTTP client."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
    ):
        # Validate API key before creating client
        try:
            validated_key = validate_api_key(api_key)
        except ValueError as e:
            raise AuthenticationError(str(e), status_code=None) from e

        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"x-api-key": validated_key},
            timeout=timeout,
        )

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            resp = await self._client.request(
                method, path, json=json, params=params
            )
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except httpx.ConnectError as e:
            raise NetworkError(f"Connection failed: {e}") from e
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

        data = resp.json() if resp.content else {}

        if resp.status_code >= 400:
            raise_for_error(resp.status_code, data)

        return data

    async def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self._request("GET", path, params=params)

    async def post(
        self, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self._request("POST", path, json=json)

    async def put(
        self, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self._request("PUT", path, json=json)

    async def delete(self, path: str) -> dict[str, Any]:
        return await self._request("DELETE", path)

    async def close(self) -> None:
        await self._client.aclose()
