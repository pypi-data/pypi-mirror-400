# AEL SDK

Python SDK for **Agent Execution Ledger** - Complete audit trail for AI agents.

## Installation

```bash
pip install ael-sdk
```

For Google ADK integration:
```bash
pip install ael-sdk[google-adk]
```

## Quick Start

```python
from ael import AELClient

# Initialize client
ael = AELClient(
    api_key="your-api-key",
    endpoint="https://your-ael-instance.com"
)

# Track agent decisions with context manager
with ael.intent("Process customer refund request") as intent:
    # Snapshot the context your agent sees
    intent.snapshot_context({
        "customer_id": "C-123",
        "order_id": "ORD-456",
        "refund_amount": 99.99,
        "reason": "Item not as described"
    })

    # Record the decision
    decision = intent.decide(
        options=[
            {"action": "approve_refund", "score": 0.95},
            {"action": "deny_refund", "score": 0.05}
        ],
        chosen="approve_refund",
        confidence=0.95,
        reasoning="Within policy, customer in good standing"
    )

    # Record the execution
    intent.execute(
        action="approve_refund",
        target={"order_id": "ORD-456"},
        result="success"
    )
```

## Google ADK Integration

```python
from ael import AELClient
from ael.integrations.google_adk import AELCallback
from google.adk import Agent

ael = AELClient(api_key="...", endpoint="...")

agent = Agent(
    model="gemini-2.0-flash",
    callbacks=[AELCallback(client=ael)]
)

# All agent decisions are automatically logged to AEL
response = agent.run("Handle customer support ticket #123")
```

## Features

- **Complete Audit Trail**: Every decision your AI agent makes is logged
- **Replay & Debug**: Reproduce any decision with the exact same context
- **Human Override Tracking**: When humans intervene, it's captured in the ledger
- **Multi-Framework Support**: Works with Google ADK, LangChain, and custom agents

## Documentation

Full documentation at [GitHub](https://github.com/vinayb21-work/Agent-Execution-Ledger)

## License

MIT License
