"""Synchronous Natural Payments SDK client."""

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
from naturalpay.models import (
    AccountBalance,
    Agent,
    AgentCreateResponse,
    AgentListResponse,
    AgentUpdateResponse,
    CancellationResult,
    Customer,
    Delegation,
    DelegationListResponse,
    Payment,
    Transaction,
    TransferDetail,
    TransferListResponse,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.natural.co"
DEFAULT_TIMEOUT = 30.0
IDEMPOTENCY_WINDOW_SECONDS = 300


class SyncHTTPClient:
    """Synchronous HTTP client for Natural Server API."""

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

        self._client: httpx.Client | None = None
        self._jwt_cache: dict[str, tuple[str, float]] = {}

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"User-Agent": "naturalpay-python/0.0.3"},
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "SyncHTTPClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _cache_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]

    def _evict_expired_cache_entries(self) -> None:
        current_time = time.time()
        expired_keys = [
            k for k, (_, expiry) in self._jwt_cache.items() if current_time >= expiry
        ]
        for key in expired_keys:
            del self._jwt_cache[key]

    def _get_jwt(self, api_key: str) -> str:
        """Exchange API key for JWT token, with caching."""
        if not api_key.startswith("pk_"):
            return api_key

        self._evict_expired_cache_entries()

        cache_key = self._cache_key(api_key)
        if cache_key in self._jwt_cache:
            jwt, expiry = self._jwt_cache[cache_key]
            if time.time() < expiry:
                return jwt
            del self._jwt_cache[cache_key]

        client = self._get_client()
        try:
            response = client.post(
                "/api/auth/partner/token",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            data = response.json()

            jwt = data["access_token"]
            expires_in = data.get("expires_in", 900)
            expiry = time.time() + expires_in - 30
            self._jwt_cache[cache_key] = (jwt, expiry)

            return jwt

        except httpx.HTTPStatusError as e:
            logger.error(f"JWT exchange failed: {e.response.status_code}")
            raise AuthenticationError(f"Authentication failed: {e.response.text}")
        except httpx.RequestError as e:
            raise NaturalError(f"Network error during authentication: {e}")

    def _auth_headers(self) -> dict[str, str]:
        if not self.api_key:
            raise AuthenticationError()
        jwt = self._get_jwt(self.api_key)
        return {"Authorization": f"Bearer {jwt}"}

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        client = self._get_client()

        request_headers = self._auth_headers()
        if headers:
            request_headers.update(headers)

        try:
            response = client.request(
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

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.request("POST", path, json=json, headers=headers)

    def put(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.request("PUT", path, json=json, headers=headers)

    def delete(self, path: str) -> dict[str, Any]:
        return self.request("DELETE", path)


# --- Sync Resource Classes ---


class SyncPaymentsResource:
    """Synchronous Payments API resource."""

    def __init__(self, http: SyncHTTPClient):
        self._http = http

    def _generate_idempotency_key(
        self,
        recipient: str,
        amount: float,
        currency: str,
        memo: str | None,
    ) -> str:
        idem_parts = [
            recipient,
            str(amount),
            currency,
            memo or "",
            str(int(time.time() // IDEMPOTENCY_WINDOW_SECONDS)),
        ]
        idem_data = ":".join(idem_parts)
        return hashlib.sha256(idem_data.encode()).hexdigest()[:32]

    def create(
        self,
        *,
        recipient_email: str | None = None,
        recipient_phone: str | None = None,
        amount: float,
        currency: str = "USD",
        memo: str | None = None,
        agent_id: str | None = None,
        customer_party_id: str | None = None,
        instance_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Payment:
        """Create a payment (synchronous).

        Args:
            recipient_email: Recipient email address
            recipient_phone: Recipient phone number
            amount: Payment amount
            currency: Currency code (default: USD)
            memo: Optional payment memo
            agent_id: Agent ID (for agent-initiated payments)
            customer_party_id: Customer party ID
            instance_id: Instance ID for audit grouping
            idempotency_key: Idempotency key to prevent duplicates

        Returns:
            Payment object with transfer_id, status, etc.
        """
        recipient_identifier = recipient_email or recipient_phone
        if not recipient_identifier:
            raise ValueError("Either recipient_email or recipient_phone is required")

        if idempotency_key is None:
            idempotency_key = self._generate_idempotency_key(
                recipient_identifier, amount, currency, memo
            )

        payload: dict[str, Any] = {"amount": amount, "currency": currency}

        if recipient_email:
            payload["recipient_email"] = recipient_email
        if recipient_phone:
            payload["recipient_phone"] = recipient_phone
        if memo:
            payload["memo"] = memo
        if agent_id:
            payload["agent_id"] = agent_id
        if customer_party_id:
            payload["customer_party_id"] = customer_party_id
        if instance_id:
            payload["instance_id"] = instance_id

        headers = {"Idempotency-Key": idempotency_key}

        data = self._http.post("/api/payments/initiate", json=payload, headers=headers)
        return Payment.model_validate(data)

    def retrieve(self, transfer_id: str) -> Payment:
        """Get payment status by transfer ID (synchronous)."""
        data = self._http.get(f"/api/payments/{transfer_id}")
        return Payment.model_validate(data)

    def cancel(self, transfer_id: str) -> CancellationResult:
        """Cancel a pending payment (synchronous)."""
        data = self._http.post(f"/api/payments/{transfer_id}/cancel")
        return CancellationResult.model_validate(data)


class SyncAccountResource:
    """Synchronous Account API resource (legacy, use SyncWalletResource for new code)."""

    def __init__(self, http: SyncHTTPClient):
        self._http = http

    def balance(self) -> AccountBalance:
        """Get current account balance (synchronous)."""
        data = self._http.get("/api/v1/wallet/balance")
        return AccountBalance.model_validate(data)


class SyncWalletResource:
    """Synchronous Wallet API resource."""

    def __init__(self, http: SyncHTTPClient):
        self._http = http

    def balance(self) -> AccountBalance:
        """Get current wallet balance (synchronous)."""
        data = self._http.get("/api/v1/wallet/balance")
        return AccountBalance.model_validate(data)

    def transfers(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> TransferListResponse:
        """List wallet transfers (synchronous).

        Args:
            limit: Maximum number of transfers (default: 20, max: 100)
            offset: Pagination offset

        Returns:
            TransferListResponse with list of transfers and pagination info
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        data = self._http.get("/api/v1/wallet/transfers", params=params)
        return TransferListResponse.model_validate(data)

    def get_transfer(self, transfer_id: str) -> TransferDetail:
        """Get detailed transfer information (synchronous).

        Args:
            transfer_id: The transfer ID to look up

        Returns:
            TransferDetail with full transfer information
        """
        data = self._http.get(f"/api/v1/wallet/transfers/{transfer_id}")
        return TransferDetail.model_validate(data)


class SyncTransactionsResource:
    """Synchronous Transactions API resource."""

    def __init__(self, http: SyncHTTPClient):
        self._http = http

    def list(
        self,
        *,
        limit: int = 10,
        customer_filter: str | None = None,
        offset: int = 0,
        agent_id: str | None = None,
        customer_party_id: str | None = None,
    ) -> list[Transaction]:
        """List recent transactions (synchronous).

        Args:
            limit: Maximum number of transactions (default: 10, max: 100)
            customer_filter: Filter by customer agent_id
            offset: Pagination offset
            agent_id: Agent ID for delegation access
            customer_party_id: Customer party ID when acting on behalf of customer

        Returns:
            List of Transaction objects
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if customer_filter:
            params["customer_filter"] = customer_filter

        headers: dict[str, str] = {}
        if agent_id:
            headers["X-Agent-ID"] = agent_id
        if customer_party_id:
            headers["X-On-Behalf-Of"] = customer_party_id

        data = self._http.get(
            "/api/transactions",
            params=params,
            headers=headers if headers else None,
        )
        transactions = data.get("transfers", data.get("transactions", []))
        return [Transaction.model_validate(tx) for tx in transactions]


class SyncAgentsResource:
    """Synchronous Agents API resource."""

    def __init__(self, http: SyncHTTPClient):
        self._http = http

    def list(
        self,
        *,
        status: str | None = None,
        party_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AgentListResponse:
        """List agents for the partner (synchronous).

        Args:
            status: Filter by status (ACTIVE, REVOKED)
            party_id: Filter by party ID
            limit: Maximum number of agents (default: 50, max: 100)
            offset: Pagination offset

        Returns:
            AgentListResponse with list of agents and pagination info
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if party_id:
            params["party_id"] = party_id

        data = self._http.get("/api/agents", params=params)
        return AgentListResponse.model_validate(data)

    def get(self, agent_id: str) -> Agent:
        """Get agent by ID (synchronous).

        Args:
            agent_id: The agent ID to retrieve (agt_xxx)

        Returns:
            Agent details
        """
        data = self._http.get(f"/api/agents/{agent_id}")
        return Agent.model_validate(data)

    def create(
        self,
        *,
        name: str,
        party_id: str,
        description: str | None = None,
        idempotency_key: str | None = None,
    ) -> AgentCreateResponse:
        """Create a new agent (synchronous).

        Args:
            name: Human-readable name for the agent
            party_id: Party ID to associate agent with
            description: Optional description of the agent's purpose
            idempotency_key: Idempotency key to prevent duplicates

        Returns:
            AgentCreateResponse with created agent details
        """
        payload: dict[str, Any] = {"name": name, "party_id": party_id}
        if description:
            payload["description"] = description

        headers: dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        data = self._http.post(
            "/api/agents",
            json=payload,
            headers=headers if headers else None,
        )
        return AgentCreateResponse.model_validate(data)

    def update(
        self,
        agent_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        idempotency_key: str | None = None,
    ) -> AgentUpdateResponse:
        """Update an existing agent (synchronous).

        Args:
            agent_id: The agent ID to update (agt_xxx)
            name: Updated name for the agent
            description: Updated description
            status: Updated status (ACTIVE, REVOKED)
            idempotency_key: Idempotency key to prevent duplicates

        Returns:
            AgentUpdateResponse with updated agent details
        """
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status

        headers: dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        data = self._http.put(
            f"/api/agents/{agent_id}",
            json=payload,
            headers=headers if headers else None,
        )
        return AgentUpdateResponse.model_validate(data)

    def delete(self, agent_id: str) -> None:
        """Delete an agent (synchronous).

        Args:
            agent_id: The agent ID to delete (agt_xxx)
        """
        self._http.delete(f"/api/agents/{agent_id}")


class SyncDelegationsResource:
    """Synchronous Delegations API resource."""

    def __init__(self, http: SyncHTTPClient):
        self._http = http

    def list(
        self,
        *,
        status: str | None = None,
        delegating_party_id: str | None = None,
        delegated_party_id: str | None = None,
    ) -> DelegationListResponse:
        """List delegations with optional filters (synchronous).

        Args:
            status: Filter by status (ACTIVE, SUSPENDED, REVOKED)
            delegating_party_id: Filter by customer party granting access
            delegated_party_id: Filter by partner party receiving access

        Returns:
            DelegationListResponse with list of delegations
        """
        params: dict[str, Any] = {}
        if status:
            params["status"] = status
        if delegating_party_id:
            params["delegating_party_id"] = delegating_party_id
        if delegated_party_id:
            params["delegated_party_id"] = delegated_party_id

        data = self._http.get("/api/delegations", params=params)
        return DelegationListResponse.model_validate(data)

    def get(self, delegation_id: str) -> Delegation:
        """Get delegation by ID (synchronous).

        Args:
            delegation_id: The delegation handle (dlg_xxx)

        Returns:
            Delegation details
        """
        data = self._http.get(f"/api/delegations/{delegation_id}")
        return Delegation.model_validate(data)


class SyncCustomersResource:
    """Synchronous Customers API resource."""

    def __init__(self, http: SyncHTTPClient):
        self._http = http

    def list(self) -> list[Customer]:
        """List customers onboarded by the partner via delegation (synchronous).

        Returns:
            List of Customer objects with party info and delegation details
        """
        data = self._http.get("/api/customers")
        return [Customer.model_validate(c) for c in data]


class NaturalClientSync:
    """Synchronous Natural Payments SDK client.

    Use this for non-async codebases. For async code, use NaturalClient instead.

    Example:
        ```python
        from naturalpay import NaturalClientSync

        client = NaturalClientSync(api_key="pk_sandbox_xxx")

        # Create a payment
        payment = client.payments.create(
            recipient_email="alice@example.com",
            amount=50.00,
            memo="For consulting"
        )

        # Check balance
        balance = client.account.balance()

        # Don't forget to close
        client.close()
        ```

    Or use as context manager:
        ```python
        with NaturalClientSync(api_key="pk_sandbox_xxx") as client:
            balance = client.account.balance()
        ```
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize the synchronous Natural client.

        Args:
            api_key: API key (defaults to NATURAL_API_KEY env var)
            base_url: API base URL (defaults to NATURAL_SERVER_URL env var)
            timeout: Request timeout in seconds (default: 30)
        """
        self._http = SyncHTTPClient(api_key=api_key, base_url=base_url, timeout=timeout)

        self.payments = SyncPaymentsResource(self._http)
        self.account = SyncAccountResource(self._http)
        self.wallet = SyncWalletResource(self._http)
        self.transactions = SyncTransactionsResource(self._http)
        self.agents = SyncAgentsResource(self._http)
        self.delegations = SyncDelegationsResource(self._http)
        self.customers = SyncCustomersResource(self._http)

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    def __enter__(self) -> "NaturalClientSync":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
