"""HTTP client wrapper for Natural Server API."""

from __future__ import annotations

import hashlib
import logging
import os
import time
from typing import Any

import httpx

from naturalpay.exceptions import (
    AuthenticationError,
    InvalidRequestError,
    NaturalError,
    RateLimitError,
    ServerError,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.natural.co"

# API version prefix for v1 endpoints
API_V1_PREFIX = "/api/v1"
DEFAULT_TIMEOUT = 30.0


class HTTPClient:
    """Async HTTP client for Natural Server API.

    Handles API key → JWT exchange and caching.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key or os.getenv("NATURAL_API_KEY")
        self.base_url = (
            base_url or os.getenv("NATURAL_SERVER_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout

        self._client: httpx.AsyncClient | None = None

        # JWT cache: {hashed_api_key: (jwt_token, expiry_timestamp)}
        self._jwt_cache: dict[str, tuple[str, float]] = {}

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "naturalpay-python/0.0.3",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "HTTPClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _cache_key(self, api_key: str) -> str:
        """Generate hashed cache key from API key."""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]

    def _evict_expired_cache_entries(self) -> None:
        """Remove expired JWT entries."""
        current_time = time.time()
        expired_keys = [
            k for k, (_, expiry) in self._jwt_cache.items() if current_time >= expiry
        ]
        for key in expired_keys:
            del self._jwt_cache[key]

    async def _get_jwt(self, api_key: str) -> str:
        """Exchange API key for JWT token, with caching.

        If the token is already a JWT (not a pk_* API key), returns it directly.
        """
        # If already a JWT (not a pk_* key), use it directly
        if not api_key.startswith("pk_"):
            return api_key

        # Evict expired entries
        self._evict_expired_cache_entries()

        # Check cache
        cache_key = self._cache_key(api_key)
        if cache_key in self._jwt_cache:
            jwt, expiry = self._jwt_cache[cache_key]
            if time.time() < expiry:
                return jwt
            del self._jwt_cache[cache_key]

        # Exchange API key for JWT
        client = self._get_client()
        try:
            response = await client.post(
                "/api/auth/partner/token",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            data = response.json()

            jwt = data["access_token"]
            expires_in = data.get("expires_in", 900)  # Default 15 minutes

            # Cache JWT (expire 30 seconds early for safety)
            expiry = time.time() + expires_in - 30
            self._jwt_cache[cache_key] = (jwt, expiry)

            return jwt

        except httpx.HTTPStatusError as e:
            logger.error(f"JWT exchange failed: {e.response.status_code}")
            raise AuthenticationError(f"Authentication failed: {e.response.text}")
        except httpx.RequestError as e:
            raise NaturalError(f"Network error during authentication: {e}")

    async def _auth_headers(self) -> dict[str, str]:
        """Get authorization headers with JWT."""
        if not self.api_key:
            raise AuthenticationError()
        jwt = await self._get_jwt(self.api_key)
        return {"Authorization": f"Bearer {jwt}"}

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated request to the Natural Server API."""
        client = self._get_client()

        request_headers = await self._auth_headers()
        if headers:
            request_headers.update(headers)

        try:
            response = await client.request(
                method,
                path,
                json=json,
                params=params,
                headers=request_headers,
            )
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NaturalError(f"Network error: {e}") from e

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError()

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                retry_after=int(retry_after) if retry_after else None
            )

        if response.status_code >= 500:
            raise ServerError(f"Server error: {response.status_code}")

        try:
            data = response.json()
        except Exception:
            if response.status_code >= 400:
                raise NaturalError(
                    f"Request failed: {response.status_code}",
                    status_code=response.status_code,
                )
            return {}

        if response.status_code >= 400:
            error_message = data.get("message", data.get("error", "Request failed"))
            error_code = data.get("code", "unknown_error")
            raise InvalidRequestError(error_message, code=error_code)

        return data

    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.request("GET", path, params=params, headers=headers)

    async def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.request("POST", path, json=json, headers=headers)

    async def put(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.request("PUT", path, json=json, headers=headers)

    async def delete(self, path: str) -> dict[str, Any]:
        return await self.request("DELETE", path)
