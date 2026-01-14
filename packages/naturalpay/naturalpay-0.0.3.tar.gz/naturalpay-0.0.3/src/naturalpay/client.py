"""Natural Payments SDK client."""

from __future__ import annotations

import hashlib
import time
from typing import Any

from naturalpay._http import HTTPClient
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

# Idempotency window in seconds (matches mcp-server)
IDEMPOTENCY_WINDOW_SECONDS = 300


class PaymentsResource:
    """Payments API resource."""

    def __init__(self, http: HTTPClient):
        self._http = http
        # Idempotency cache: {(cache_key, idem_key): (result, timestamp)}
        self._idempotency_cache: dict[tuple[str, str], tuple[Payment, float]] = {}

    def _generate_idempotency_key(
        self,
        recipient: str,
        amount: float,
        currency: str,
        memo: str | None,
    ) -> str:
        """Generate idempotency key based on payment details + time window."""
        idem_parts = [
            recipient,
            str(amount),
            currency,
            memo or "",
            str(int(time.time() // IDEMPOTENCY_WINDOW_SECONDS)),
        ]
        idem_data = ":".join(idem_parts)
        return hashlib.sha256(idem_data.encode()).hexdigest()[:32]

    async def create(
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
        """Create a payment.

        Args:
            recipient_email: Recipient email address
            recipient_phone: Recipient phone number
            amount: Payment amount
            currency: Currency code (default: USD)
            memo: Optional payment memo
            agent_id: Agent ID (for agent-initiated payments)
            customer_party_id: Customer party ID
            instance_id: Instance ID for audit grouping
            idempotency_key: Idempotency key to prevent duplicates (auto-generated if not provided)

        Returns:
            Payment object with transfer_id, status, etc.
        """
        # Determine recipient
        recipient_identifier = recipient_email or recipient_phone
        if not recipient_identifier:
            raise ValueError("Either recipient_email or recipient_phone is required")

        # Auto-generate idempotency key if not provided
        if idempotency_key is None:
            idempotency_key = self._generate_idempotency_key(
                recipient_identifier, amount, currency, memo
            )

        # Build payload
        payload: dict[str, Any] = {
            "amount": amount,
            "currency": currency,
        }

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

        data = await self._http.post("/api/payments/initiate", json=payload, headers=headers)
        return Payment.model_validate(data)

    async def retrieve(self, transfer_id: str) -> Payment:
        """Get payment status by transfer ID.

        Args:
            transfer_id: The transfer ID to look up

        Returns:
            Payment object with current status
        """
        data = await self._http.get(f"/api/payments/{transfer_id}")
        return Payment.model_validate(data)

    async def cancel(self, transfer_id: str) -> CancellationResult:
        """Cancel a pending payment.

        Args:
            transfer_id: The transfer ID to cancel

        Returns:
            CancellationResult with status and message
        """
        data = await self._http.post(f"/api/payments/{transfer_id}/cancel")
        return CancellationResult.model_validate(data)


class AccountResource:
    """Account API resource (legacy, use WalletResource for new code)."""

    def __init__(self, http: HTTPClient):
        self._http = http

    async def balance(self) -> AccountBalance:
        """Get current account balance.

        Returns:
            AccountBalance with available, current, pending amounts
        """
        data = await self._http.get("/api/v1/wallet/balance")
        return AccountBalance.model_validate(data)


class WalletResource:
    """Wallet API resource for balance, transfers, deposits, and withdrawals."""

    def __init__(self, http: HTTPClient):
        self._http = http

    async def balance(self) -> AccountBalance:
        """Get current wallet balance.

        Returns:
            AccountBalance with available, current, pending amounts
        """
        data = await self._http.get("/api/v1/wallet/balance")
        return AccountBalance.model_validate(data)

    async def transfers(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> TransferListResponse:
        """List wallet transfers (deposits, withdrawals, payments).

        Args:
            limit: Maximum number of transfers (default: 20, max: 100)
            offset: Pagination offset

        Returns:
            TransferListResponse with list of transfers and pagination info
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        data = await self._http.get("/api/v1/wallet/transfers", params=params)
        return TransferListResponse.model_validate(data)

    async def get_transfer(self, transfer_id: str) -> TransferDetail:
        """Get detailed transfer information.

        Args:
            transfer_id: The transfer ID to look up

        Returns:
            TransferDetail with full transfer information
        """
        data = await self._http.get(f"/api/v1/wallet/transfers/{transfer_id}")
        return TransferDetail.model_validate(data)


class TransactionsResource:
    """Transactions API resource.

    For full functionality with partner API keys, pass agent_id and
    customer_party_id to provide agent context.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    async def list(
        self,
        *,
        limit: int = 10,
        customer_filter: str | None = None,
        offset: int = 0,
        agent_id: str | None = None,
        customer_party_id: str | None = None,
    ) -> list[Transaction]:
        """List recent transactions.

        Args:
            limit: Maximum number of transactions (default: 10, max: 100)
            customer_filter: Filter by customer agent_id (or '_self' for partner only)
            offset: Pagination offset
            agent_id: Agent ID for agent-context authentication (required for delegation access)
            customer_party_id: Customer party ID when acting on behalf of customer

        Returns:
            List of Transaction objects
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if customer_filter:
            params["customer_filter"] = customer_filter

        # Build agent context headers
        headers: dict[str, str] = {}
        if agent_id:
            headers["X-Agent-ID"] = agent_id
        if customer_party_id:
            headers["X-On-Behalf-Of"] = customer_party_id

        data = await self._http.get(
            "/api/transactions",
            params=params,
            headers=headers if headers else None,
        )
        transactions = data.get("transfers", data.get("transactions", []))
        return [Transaction.model_validate(tx) for tx in transactions]


class AgentsResource:
    """Agents API resource for managing agents.

    Agents are software systems that can act on behalf of partners.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    async def list(
        self,
        *,
        status: str | None = None,
        party_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AgentListResponse:
        """List agents for the partner.

        Args:
            status: Filter by status (ACTIVE, REVOKED)
            party_id: Filter by party ID (defaults to authenticated partner's party)
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

        data = await self._http.get("/api/agents", params=params)
        return AgentListResponse.model_validate(data)

    async def get(self, agent_id: str) -> Agent:
        """Get agent by ID.

        Args:
            agent_id: The agent ID to retrieve (agt_xxx)

        Returns:
            Agent details
        """
        data = await self._http.get(f"/api/agents/{agent_id}")
        return Agent.model_validate(data)

    async def create(
        self,
        *,
        name: str,
        party_id: str,
        description: str | None = None,
        idempotency_key: str | None = None,
    ) -> AgentCreateResponse:
        """Create a new agent.

        Args:
            name: Human-readable name for the agent
            party_id: Party ID to associate agent with
            description: Optional description of the agent's purpose
            idempotency_key: Idempotency key to prevent duplicates

        Returns:
            AgentCreateResponse with created agent details
        """
        payload: dict[str, Any] = {
            "name": name,
            "party_id": party_id,
        }
        if description:
            payload["description"] = description

        headers: dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        data = await self._http.post(
            "/api/agents",
            json=payload,
            headers=headers if headers else None,
        )
        return AgentCreateResponse.model_validate(data)

    async def update(
        self,
        agent_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        idempotency_key: str | None = None,
    ) -> AgentUpdateResponse:
        """Update an existing agent.

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

        data = await self._http.put(
            f"/api/agents/{agent_id}",
            json=payload,
            headers=headers if headers else None,
        )
        return AgentUpdateResponse.model_validate(data)

    async def delete(self, agent_id: str) -> None:
        """Delete an agent.

        Args:
            agent_id: The agent ID to delete (agt_xxx)
        """
        await self._http.delete(f"/api/agents/{agent_id}")


class DelegationsResource:
    """Delegations API resource for managing party-to-party delegations.

    Delegations represent trust relationships where a customer grants
    a partner access to act on their behalf.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    async def list(
        self,
        *,
        status: str | None = None,
        delegating_party_id: str | None = None,
        delegated_party_id: str | None = None,
    ) -> DelegationListResponse:
        """List delegations with optional filters.

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

        data = await self._http.get("/api/delegations", params=params)
        return DelegationListResponse.model_validate(data)

    async def get(self, delegation_id: str) -> Delegation:
        """Get delegation by ID.

        Args:
            delegation_id: The delegation handle (dlg_xxx)

        Returns:
            Delegation details
        """
        data = await self._http.get(f"/api/delegations/{delegation_id}")
        return Delegation.model_validate(data)


class CustomersResource:
    """Customers API resource for listing customers onboarded via delegation.

    Customers are parties that have delegated access to the partner.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    async def list(self) -> list[Customer]:
        """List customers onboarded by the partner via delegation.

        Returns:
            List of Customer objects with party info and delegation details
        """
        data = await self._http.get("/api/customers")
        return [Customer.model_validate(c) for c in data]


class NaturalClient:
    """Natural Payments SDK client.

    Example:
        ```python
        from naturalpay import NaturalClient

        client = NaturalClient(api_key="pk_sandbox_xxx")

        # Create a payment
        payment = await client.payments.create(
            recipient_email="alice@example.com",
            amount=50.00,
            memo="For consulting"
        )

        # Check balance
        balance = await client.account.balance()
        ```
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize the Natural client.

        Args:
            api_key: API key (defaults to NATURAL_API_KEY env var)
            base_url: API base URL (defaults to NATURAL_SERVER_URL env var)
            timeout: Request timeout in seconds (default: 30)
        """
        self._http = HTTPClient(api_key=api_key, base_url=base_url, timeout=timeout)

        self.payments = PaymentsResource(self._http)
        self.account = AccountResource(self._http)
        self.wallet = WalletResource(self._http)
        self.transactions = TransactionsResource(self._http)
        self.agents = AgentsResource(self._http)
        self.delegations = DelegationsResource(self._http)
        self.customers = CustomersResource(self._http)

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> "NaturalClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
