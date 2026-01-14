"""Natural Payments MCP server using FastMCP."""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Literal

from fastmcp import FastMCP

from naturalpay.client import NaturalClient
from naturalpay.models import ParsedIntent

# Idempotency window in seconds (matches mcp-server)
IDEMPOTENCY_WINDOW_SECONDS = 300


def _parse_payment_intent(text: str) -> ParsedIntent:
    """Parse payment text using OpenAI.

    This matches the intent_parser.py from mcp-server.
    """
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set - required for intent parsing")

    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    timeout_ms = int(os.getenv("LLM_TIMEOUT_MS", "30000"))

    client = OpenAI(api_key=api_key, timeout=timeout_ms / 1000.0)

    system = (
        "You are a strict payment intent extractor. "
        "Output only a single JSON object matching this schema: "
        "{ recipient: oneOf({phone},{email},{bank_token},{counterparty_id}), "
        "  amount: number|null, currency: string, "
        "  business_context: { memo?: string, "
        "route?: { from: string|null, to: string|null } } } "
        "If a field is not present in the text, set it to null or omit optional fields. "
        "Do not include any extra keys."
    )

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
        temperature=0,
    )

    content = resp.output_text
    data = json.loads(content)
    return ParsedIntent.model_validate(data)


def create_server(api_key: str | None = None) -> FastMCP:
    """Create a Natural Payments MCP server.

    Args:
        api_key: API key (defaults to NATURAL_API_KEY env var)

    Returns:
        Configured FastMCP server instance
    """
    mcp = FastMCP("Natural Payments")

    # Lazy client initialization
    _client: NaturalClient | None = None

    def get_client() -> NaturalClient:
        nonlocal _client
        if _client is None:
            _client = NaturalClient(api_key=api_key)
        return _client

    @mcp.tool()
    async def parse_intent(text: str) -> dict:
        """Parse natural language into structured payment intent.

        Use this to preview what a payment instruction means without
        actually executing it.

        Args:
            text: Natural language payment instruction
                  (e.g., "Pay alice@example.com $50 for consulting")

        Returns:
            Parsed intent with recipient, amount, currency, memo
        """
        result = _parse_payment_intent(text)
        return result.model_dump(exclude_none=True)

    @mcp.tool()
    async def create_payment(
        text: str,
        agent_id: str,
        customer_party_id: str,
        instance_id: str | None = None,
    ) -> dict:
        """Parse natural language and execute a payment.

        Args:
            text: Natural language payment instruction
                  (e.g., "Pay alice@example.com $50 for consulting")
            agent_id: Agent ID - which agent is acting
            customer_party_id: Customer party ID - on whose behalf
            instance_id: Optional instance ID for audit grouping

        Returns:
            Payment result with transfer_id, status, amount, etc.
        """
        # Parse intent locally using OpenAI
        parsed = _parse_payment_intent(text)

        # Extract recipient
        recipient_email = parsed.recipient.email
        recipient_phone = parsed.recipient.phone

        if not recipient_email and not recipient_phone:
            raise ValueError(f"Could not extract recipient from text. Parsed: {parsed.model_dump()}")

        if not parsed.amount:
            raise ValueError(f"Could not extract amount from text. Parsed: {parsed.model_dump()}")

        memo = parsed.business_context.memo if parsed.business_context else None

        # Generate idempotency key
        recipient = recipient_email or recipient_phone
        idem_parts = [
            recipient,
            str(parsed.amount),
            parsed.currency,
            memo or "",
            str(int(time.time() // IDEMPOTENCY_WINDOW_SECONDS)),
        ]
        idem_data = ":".join(idem_parts)
        idempotency_key = hashlib.sha256(idem_data.encode()).hexdigest()[:32]

        # Create payment via SDK
        client = get_client()
        result = await client.payments.create(
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            amount=parsed.amount,
            currency=parsed.currency,
            memo=memo,
            agent_id=agent_id,
            customer_party_id=customer_party_id,
            instance_id=instance_id,
            idempotency_key=idempotency_key,
        )
        return result.model_dump(exclude_none=True)

    @mcp.tool()
    async def get_payment_status(transfer_id: str) -> dict:
        """Check the status of a payment by transfer ID.

        Args:
            transfer_id: The transfer ID returned from create_payment

        Returns:
            Payment details with current status
        """
        client = get_client()
        result = await client.payments.retrieve(transfer_id)
        return result.model_dump(exclude_none=True)

    @mcp.tool()
    async def get_account_balance() -> dict:
        """Get the current wallet balance.

        Returns:
            Wallet balance with available amount and breakdown by account type
        """
        client = get_client()
        result = await client.account.balance()
        # Return a simplified view for the MCP tool
        return {
            "wallet_id": result.wallet_id,
            "available_usd": result.available_usd,
            "balances": [
                {
                    "asset_code": bal.asset_code,
                    "available": bal.available.amount_dollars,
                    "breakdown": {
                        "operating_funded": bal.breakdown.operating_funded.amount_dollars,
                        "operating_advanced": bal.breakdown.operating_advanced.amount_dollars,
                        "escrow_funded_settled": bal.breakdown.escrow_funded_settled.amount_dollars,
                        "escrow_advanced": bal.breakdown.escrow_advanced.amount_dollars,
                        "holds_outbound": bal.breakdown.holds_outbound.amount_dollars,
                    }
                }
                for bal in result.balances
            ]
        }

    @mcp.tool()
    async def list_transactions(
        limit: int = 10,
        customer_filter: str | None = None,
        agent_id: str | None = None,
        customer_party_id: str | None = None,
    ) -> list[dict]:
        """List recent transactions.

        For full functionality, provide agent_id and customer_party_id
        to establish agent context for accessing delegated transactions.

        Args:
            limit: Maximum number of transactions (default: 10, max: 100)
            customer_filter: Filter by customer agent_id (or '_self' for partner only)
            agent_id: Agent ID for agent-context authentication
            customer_party_id: Customer party ID when acting on behalf of customer

        Returns:
            List of transactions with details
        """
        client = get_client()
        results = await client.transactions.list(
            limit=limit,
            customer_filter=customer_filter,
            agent_id=agent_id,
            customer_party_id=customer_party_id,
        )
        return [tx.model_dump(exclude_none=True) for tx in results]

    @mcp.tool()
    async def cancel_payment(transfer_id: str) -> dict:
        """Cancel a pending payment.

        Only pending payments can be cancelled. Completed or processing
        payments cannot be reversed.

        Args:
            transfer_id: The transfer ID to cancel

        Returns:
            Cancellation result with status and message
        """
        client = get_client()
        result = await client.payments.cancel(transfer_id)
        return result.model_dump()

    return mcp


def serve(
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
    *,
    host: str = "127.0.0.1",
    port: int = 8080,
    api_key: str | None = None,
) -> None:
    """Run the Natural Payments MCP server.

    Args:
        transport: Transport type (stdio, sse, streamable-http)
        host: Host to bind to (for HTTP transports)
        port: Port to bind to (for HTTP transports)
        api_key: API key (defaults to NATURAL_API_KEY env var)
    """
    mcp = create_server(api_key=api_key)

    if transport == "stdio":
        mcp.run()
    elif transport == "sse":
        mcp.run(transport="sse", host=host, port=port)
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        raise ValueError(f"Unknown transport: {transport}")
