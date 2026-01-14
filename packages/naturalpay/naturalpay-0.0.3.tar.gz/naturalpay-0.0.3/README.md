# naturalpay

Natural Payments SDK

## Installation

```bash
pip install naturalpay
# or
uv add naturalpay
```

## Quick Start

```python
from naturalpay import NaturalClient

client = NaturalClient(api_key="pk_sandbox_xxx")

# Create a payment
payment = await client.payments.create(
    recipient_email="alice@example.com",
    amount=50.00,
    memo="For consulting"
)

print(payment.transfer_id)  # txn_abc123
```

## MCP Server

Run the MCP server for AI agent integrations:

```bash
naturalpay mcp serve
```

## Documentation

- [API Reference](https://docs.natural.co)
- [Examples](https://github.com/naturalpay/natural-examples)

## License

MIT
