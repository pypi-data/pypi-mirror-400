# HaltState Sentinel SDK

[![PyPI](https://img.shields.io/pypi/v/haltstate-sdk.svg)](https://pypi.org/project/haltstate-sdk/)

Compliance & policy checks for AI agents. Perform pre-action checks, approvals, and post-action reporting with minimal code.

## Installation
```bash
pip install haltstate-sdk
```

## Quickstart (sync)
```python
from haltstate import HaltStateClient

client = HaltStateClient(tenant_id="your_tenant_id", api_key="janus_xyz", fail_open=False)

decision = client.check(
    action="payment.process",
    params={"amount": 5000, "currency": "USD"},
    agent_id="payment-bot-01",
)

if decision.allowed:
    process_payment(...)
    client.report(decision, status="success", result={"transaction_id": "tx_123"}, action="payment.process", agent_id="payment-bot-01")
elif decision.requires_approval:
    print(f"Approval required: {decision.reason}")
else:
    print(f"Action denied: {decision.reason}")
```

### Backward Compatibility

Existing code using `janus` imports continues to work:

```python
from janus import JanusClient  # Still works!
```

## Guard Pattern (SDK 0.5.0+)

For actions requiring human approval, use the idempotent guard pattern:

```python
from haltstate import AsyncHaltStateClient, ActionPending, ActionRejected

async def process_high_value_payment(invoice_id: str, amount: float):
    client = AsyncHaltStateClient(tenant_id="acme", api_key="janus_xxx")

    try:
        async with client.guard(
            action="payment.process",
            agent_id="payment-bot",
            params={"invoice_id": invoice_id, "amount": amount},
            idempotency_key=f"payment-{invoice_id}",  # Retry-safe
            timeout_seconds=300
        ) as permit:
            # Only executes after human approval
            result = await execute_payment(amount)
            print(f"Approved by {permit.approver} at {permit.approved_at}")
            return result

    except ActionPending:
        print("Awaiting human approval...")
        return {"status": "pending"}

    except ActionRejected as e:
        print(f"Rejected by {e.rejected_by}: {e.reason}")
        raise
```

Key features:
- **Idempotency keys**: Same key = same approval request, safe for retries
- **Process restart safety**: Approved actions can be executed after restart
- **Audit trail**: Full record of who approved and when

## Decorators
```python
from haltstate import HaltStateClient, haltstate_guard

client = HaltStateClient(tenant_id="acme", api_key="janus_xxx")

@haltstate_guard(client, action="email.send", agent_id="email-bot")
def send_email(to, subject, body):
    return mailer.send(to, subject, body)
```

## Async
```python
from haltstate import AsyncHaltStateClient

async def main():
    async with AsyncHaltStateClient(tenant_id="acme", api_key="janus_xxx") as client:
        res = await client.check("database.drop", params={"table": "users"})
        if res.allowed:
            await client.report(res, status="success", action="database.drop", agent_id="ops-bot")
```

## Exceptions

```python
from haltstate import (
    HaltStateError,           # Base error
    HaltStateAuthError,       # Invalid API key
    HaltStateConnectionError, # Network/timeout
    ActionPending,            # Awaiting approval (guard pattern)
    ActionRejected,           # Human rejected (guard pattern)
    ActionTimeout,            # Approval expired (guard pattern)
)
```

## Docs

Full documentation at [haltstate.ai/docs](https://haltstate.ai/docs):
- Quickstart - 5-minute setup
- Guard Pattern - HITL approval flow
- API Reference - All methods
- Error Handling - Exception handling
- SB-53 Compliance - Regulatory mapping

## Migration from janus-sdk

If upgrading from `janus-sdk`:

```python
# Old (still works)
from janus import JanusClient, janus_guard

# New
from haltstate import HaltStateClient, haltstate_guard
```

Both import styles work - no code changes required for existing users.

## License
MIT
