"""Natural Payments SDK models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Payment(BaseModel):
    """Payment result."""

    transfer_id: str
    payment_id: str | None = None
    # Status values from natural-api payment orchestration
    # PENDING_CLAIM: Payment sent to provisional recipient (needs to claim)
    # COMPLETED: Payment completed successfully
    # PENDING: Payment in progress
    # FAILED: Payment failed
    status: str  # Allow any status string from server
    amount: float | None = None
    currency: str = "USD"
    recipient_email: str | None = None
    recipient_phone: str | None = None
    memo: str | None = None
    created_at: datetime | str | None = None  # Server may return ISO string
    claim_link: str | None = None
    counterparty_party_id: str | None = None
    instance_id: str | None = None  # Echoed back for audit grouping


class AmountInfo(BaseModel):
    """Amount with minor and dollar representations."""

    amount_minor: int
    amount_dollars: str


class BalanceBreakdown(BaseModel):
    """Detailed balance breakdown."""

    operating_funded: AmountInfo
    operating_advanced: AmountInfo
    escrow_funded_settled: AmountInfo
    escrow_advanced: AmountInfo
    holds_outbound: AmountInfo


class AssetBalance(BaseModel):
    """Balance for a specific asset/currency."""

    asset_code: str
    breakdown: BalanceBreakdown
    available: AmountInfo
    metadata: dict | None = None


class AccountBalance(BaseModel):
    """Wallet balance information from /api/v1/wallet/balance."""

    wallet_id: str
    balances: list[AssetBalance]

    @property
    def available_usd(self) -> float:
        """Get available USD balance as a float."""
        for balance in self.balances:
            if balance.asset_code == "USD":
                return float(balance.available.amount_dollars)
        return 0.0


class Transaction(BaseModel):
    """Transaction record."""

    transaction_id: str
    type: Literal["payment_sent", "payment_received", "deposit", "withdrawal"]
    status: Literal["pending", "processing", "completed", "failed"]
    amount: float
    currency: str = "USD"
    counterparty: str | None = None
    memo: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class CancellationResult(BaseModel):
    """Payment cancellation result."""

    status: str
    message: str


class TransferSummary(BaseModel):
    """Summary view of a wallet transfer."""

    transfer_id: str
    transfer_type: str  # WITHDRAWAL, DEPOSIT, PAYMENT, etc.
    status: str
    amount: str  # String from API (e.g., "100.00")
    currency: str = "USD"
    party_id: str | None = None  # Included in response from BFF route
    created_at: str
    completed_at: str | None = None

    @property
    def amount_float(self) -> float:
        """Get amount as float."""
        return float(self.amount)


class TransferDetail(BaseModel):
    """Detailed view of a wallet transfer."""

    transfer_id: str
    transfer_type: str
    status: str
    amount: str
    currency: str = "USD"
    party_id: str
    wallet_id: str | None = None
    payment_instrument_id: str | None = None
    description: str | None = None
    created_at: str
    completed_at: str | None = None
    metadata: dict | None = None

    @property
    def amount_float(self) -> float:
        """Get amount as float."""
        return float(self.amount)


class TransferListResponse(BaseModel):
    """Response for list transfers endpoint."""

    transfers: list[TransferSummary]
    total: int
    limit: int = 20
    offset: int = 0
    has_more: bool = False


class ParsedIntent(BaseModel):
    """Parsed payment intent from natural language."""

    class Recipient(BaseModel):
        email: str | None = None
        phone: str | None = None
        bank_token: str | None = None
        counterparty_id: str | None = None

    class BusinessContext(BaseModel):
        memo: str | None = None

    recipient: Recipient
    amount: float | None = None
    currency: str = "USD"
    business_context: BusinessContext | None = None


# =============================================================================
# AGENT MODELS
# =============================================================================


class Agent(BaseModel):
    """Agent entity."""

    agent_id: str
    id: str  # Same as agent_id (BFF returns both)
    name: str
    description: str | None = None
    status: Literal["ACTIVE", "REVOKED"]
    party_id: str
    created_at: datetime | str
    created_by: str
    updated_at: datetime | str
    updated_by: str


class AgentCreateResponse(BaseModel):
    """Response from agent creation."""

    agent_id: str
    name: str
    description: str | None = None
    status: Literal["ACTIVE", "REVOKED"]
    party_id: str
    created_at: datetime | str
    created_by: str


class AgentUpdateResponse(BaseModel):
    """Response from agent update."""

    agent_id: str
    name: str
    description: str | None = None
    status: Literal["ACTIVE", "REVOKED"]
    party_id: str
    updated_at: datetime | str
    updated_by: str


class AgentListResponse(BaseModel):
    """Response for list agents endpoint."""

    agents: list[Agent]
    total: int
    page: int
    page_size: int


# =============================================================================
# DELEGATION MODELS
# =============================================================================


class Delegation(BaseModel):
    """Delegation entity (party-to-party trust relationship)."""

    id: str
    handle: str
    delegating_party_id: str  # Customer party granting access
    delegated_party_id: str  # Partner party receiving access
    permissions: list[str]
    expires_at: datetime | str | None = None
    status: str  # ACTIVE, SUSPENDED, REVOKED
    created_at: datetime | str
    created_by: str | None = None


class DelegationListResponse(BaseModel):
    """Response for list delegations endpoint."""

    delegations: list[Delegation]
    total: int


# =============================================================================
# CUSTOMER MODELS
# =============================================================================


class CustomerPartyInfo(BaseModel):
    """Customer party information."""

    id: str
    handle: str | None = None
    type: str  # PERSON or ORG
    legal_name: str | None = None
    display_name: str | None = None
    status: str | None = None


class Customer(BaseModel):
    """Customer with delegation details."""

    party: CustomerPartyInfo
    delegation_id: str
    permissions: list[str] = Field(default_factory=list)
    delegation_status: str
    created_at: str
