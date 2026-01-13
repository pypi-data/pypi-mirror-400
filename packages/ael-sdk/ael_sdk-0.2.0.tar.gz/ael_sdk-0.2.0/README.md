# AEL SDK

Python SDK for **Agent Execution Ledger** - Complete audit trail for AI agents.

## Installation

```bash
pip install ael-sdk
```

With framework integrations:
```bash
pip install ael-sdk[langchain]     # LangChain
pip install ael-sdk[crewai]        # CrewAI
pip install ael-sdk[openai]        # OpenAI Assistants
pip install ael-sdk[autogen]       # Microsoft AutoGen
pip install ael-sdk[google-adk]    # Google ADK
pip install ael-sdk[all]           # All integrations
```

## Quick Start

```python
from ael import AELClient, ActionOption, ResultType

ael = AELClient(
    api_key="your-api-key",
    endpoint="https://your-ael-instance.com"
)

with ael.intent("Process customer refund request") as intent:
    intent.snapshot_context({
        "customer_id": "C-123",
        "order_id": "ORD-456",
        "refund_amount": 99.99,
    })

    intent.decide(
        options=[
            ActionOption(action="approve_refund", score=0.95, reason="Within policy"),
            ActionOption(action="deny_refund", score=0.05, reason="N/A")
        ],
        chosen_action="approve_refund",
        confidence=0.95,
        model_version="gpt-4",
        reasoning="Customer eligible per 30-day policy"
    )

    intent.execute(
        action="approve_refund",
        target={"order_id": "ORD-456"},
        result=ResultType.SUCCESS
    )
```

---

## Framework Integrations

### LangChain

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from ael import AELClient
from ael.integrations.langchain import AELCallbackHandler

ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
ael_handler = AELCallbackHandler(ael, agent_id="langchain-agent")

llm = ChatOpenAI(model="gpt-4")
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, callbacks=[ael_handler])

# All agent actions automatically logged to AEL
result = executor.invoke({"input": "What is the weather in NYC?"})
```

### CrewAI

```python
from crewai import Agent, Task, Crew
from ael import AELClient
from ael.integrations.crewai import AELCrewTracker

ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
tracker = AELCrewTracker(ael)

researcher = Agent(role="Researcher", goal="...", backstory="...")
writer = Agent(role="Writer", goal="...", backstory="...")

task1 = Task(description="Research topic", agent=researcher)
task2 = Task(description="Write article", agent=writer)

crew = Crew(agents=[researcher, writer], tasks=[task1, task2])

with tracker.track_crew("Content creation pipeline") as t:
    result = crew.kickoff()
    t.record_result(result, agents=[researcher, writer], tasks=[task1, task2])
```

### OpenAI Assistants

```python
from openai import OpenAI
from ael import AELClient
from ael.integrations.openai_assistants import AELAssistantTracker

openai = OpenAI()
ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
tracker = AELAssistantTracker(ael)

assistant = openai.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a math tutor.",
    model="gpt-4o"
)

with tracker.track_run(assistant_id=assistant.id, goal="Help with math") as t:
    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="What is 2+2?"
    )

    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    t.record_run(run, messages)
```

### Microsoft AutoGen

```python
from autogen import AssistantAgent, UserProxyAgent
from ael import AELClient
from ael.integrations.autogen import AELAutoGenTracker

ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
tracker = AELAutoGenTracker(ael)

assistant = AssistantAgent("assistant", llm_config={"model": "gpt-4"})
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding"})

with tracker.track_conversation("Solve coding problem") as t:
    user_proxy.initiate_chat(assistant, message="Write a sorting function")
    t.record_messages(user_proxy.chat_messages[assistant])
```

### Google ADK

```python
import asyncio
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from ael import AELClient
from ael.integrations.google_adk import AELTracker

ael = AELClient(api_key="...", endpoint="...")
tracker = AELTracker(ael, agent_id="support-agent")

agent = Agent(
    name="support",
    model="gemini-2.0-flash",
    instruction="You are a helpful customer support agent."
)

async def handle_request():
    with tracker.track("Handle customer request") as t:
        t.context({"customer_id": "123", "ticket": "support-456"})

        runner = InMemoryRunner(agent=agent, app_name="support-app")
        session = await runner.session_service.create_session(
            app_name="support-app", user_id="user-123"
        )

        content = types.Content(
            role="user",
            parts=[types.Part(text="Handle support ticket #123")]
        )

        response_text = ""
        async for event in runner.run_async(
            user_id="user-123",
            session_id=session.id,
            new_message=content
        ):
            if hasattr(event, 'content') and event.content:
                response_text = event.content.parts[0].text

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

---

## Features

- **Complete Audit Trail**: Every decision your AI agent makes is logged
- **Replay & Debug**: Reproduce any decision with the exact same context
- **Human Override Tracking**: When humans intervene, it's captured in the ledger
- **Multi-Framework Support**: LangChain, CrewAI, OpenAI, AutoGen, Google ADK

## Documentation

Full documentation at [GitHub](https://github.com/vinayb21-work/Agent-Execution-Ledger)

## License

MIT License
