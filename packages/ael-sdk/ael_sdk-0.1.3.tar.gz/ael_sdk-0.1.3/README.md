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
import asyncio
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from ael import AELClient
from ael.integrations.google_adk import AELTracker

# Initialize
ael = AELClient(api_key="...", endpoint="...")
tracker = AELTracker(ael, agent_id="support-agent")

# Create your ADK agent
agent = Agent(
    name="support",
    model="gemini-2.0-flash",
    instruction="You are a helpful customer support agent."
)

async def handle_request():
    # Track agent interactions
    with tracker.track("Handle customer request") as t:
        t.context({"customer_id": "123", "ticket": "support-456"})

        # Run your agent using InMemoryRunner
        runner = InMemoryRunner(agent=agent, app_name="support-app")
        user_id = "user-123"
        session = await runner.session_service.create_session(
            app_name="support-app", user_id=user_id
        )

        content = types.Content(
            role="user",
            parts=[types.Part(text="Handle customer support ticket #123")]
        )

        response_text = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content
        ):
            if hasattr(event, 'content') and event.content:
                response_text = event.content.parts[0].text

        # Record decision and execution
        t.decision(
            chosen="resolve_ticket",
            confidence=0.92,
            reasoning=response_text,
            options=[
                {"action": "resolve_ticket", "score": 0.92},
                {"action": "escalate", "score": 0.08},
            ]
        )
        t.execute(action="resolve_ticket", result="success")

asyncio.run(handle_request())
```

You can also use the one-shot `track_action` method:

```python
tracker.track_action(
    goal="Handle refund request",
    inputs={"customer_id": "123", "amount": 99.99},
    chosen_action="approve_refund",
    confidence=0.95,
    reasoning="Within policy limits",
    options=[
        {"action": "approve_refund", "score": 0.95},
        {"action": "deny_refund", "score": 0.05}
    ],
    result="success"
)
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
