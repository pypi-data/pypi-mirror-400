"""
OpenAI Assistants API integration for AEL.

This module provides utilities to track OpenAI Assistants actions in AEL.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4
from contextlib import contextmanager

from ..client import AELClient, ActionOption, ResultType, ActorType, OriginType


class AELAssistantTracker:
    """
    Tracker for OpenAI Assistants that records actions in AEL.

    Usage:
        from openai import OpenAI
        from ael import AELClient
        from ael.integrations.openai_assistants import AELAssistantTracker

        openai = OpenAI()
        ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
        tracker = AELAssistantTracker(ael)

        # Create assistant
        assistant = openai.beta.assistants.create(
            name="Math Tutor",
            instructions="You are a math tutor.",
            model="gpt-4o"
        )

        # Track a conversation
        with tracker.track_run(
            assistant_id=assistant.id,
            goal="Help with math problem"
        ) as t:
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
    """

    def __init__(
        self,
        client: AELClient,
        session_id: Optional[str] = None,
    ):
        self.client = client
        self.session_id = session_id or str(uuid4())

    @contextmanager
    def track_run(self, assistant_id: str, goal: str):
        """
        Context manager for tracking an OpenAI Assistant run.

        Usage:
            with tracker.track_run(assistant.id, "Answer user question") as t:
                # Run the assistant
                run = openai.beta.threads.runs.create_and_poll(...)
                messages = openai.beta.threads.messages.list(...)
                t.record_run(run, messages)
        """
        tracker = _RunTracker(
            client=self.client,
            assistant_id=assistant_id,
            goal=goal,
            session_id=self.session_id,
        )
        try:
            yield tracker
        finally:
            tracker._finalize()

    def track_run_sync(
        self,
        assistant_id: str,
        goal: str,
        run: Any,
        messages: Any,
        tools_called: Optional[List[Dict]] = None,
    ) -> Dict[str, str]:
        """
        One-shot tracking of a completed assistant run.

        Args:
            assistant_id: The OpenAI assistant ID
            goal: What the assistant was trying to accomplish
            run: The Run object from OpenAI
            messages: The Messages list from the thread
            tools_called: List of tools that were called

        Returns:
            Dict with execution details
        """
        # Extract run info
        run_id = getattr(run, 'id', 'unknown')
        status = getattr(run, 'status', 'unknown')
        model = getattr(run, 'model', 'unknown')

        # Extract messages
        message_list = []
        if hasattr(messages, 'data'):
            for msg in messages.data:
                content = ""
                if hasattr(msg, 'content') and msg.content:
                    for block in msg.content:
                        if hasattr(block, 'text') and hasattr(block.text, 'value'):
                            content = block.text.value
                            break
                message_list.append({
                    "role": getattr(msg, 'role', 'unknown'),
                    "content": content[:500],
                })

        # Build options from tools called
        options = []
        if tools_called:
            for i, tool in enumerate(tools_called):
                options.append(ActionOption(
                    action=tool.get("name", "unknown_tool"),
                    score=1.0 / (i + 1),
                    reason=tool.get("arguments", "")[:100]
                ))
        else:
            options.append(ActionOption(
                action="generate_response",
                score=1.0,
                reason="Direct response without tool use"
            ))

        with self.client.intent(
            goal=goal,
            agent_id=f"openai-assistant-{assistant_id[:8]}",
            session_id=self.session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "assistant_id": assistant_id,
                "run_id": run_id,
                "messages": message_list,
            })

            chosen_action = tools_called[0]["name"] if tools_called else "generate_response"

            intent.decide(
                options=options,
                chosen_action=chosen_action,
                confidence=0.9 if status == "completed" else 0.5,
                model_version=model,
                reasoning=f"Run {status}",
            )

            result_type = ResultType.SUCCESS if status == "completed" else ResultType.FAILURE

            # Get assistant response
            assistant_response = ""
            for msg in message_list:
                if msg["role"] == "assistant":
                    assistant_response = msg["content"]
                    break

            execution_id = intent.execute(
                action=chosen_action,
                target={"response": assistant_response},
                result=result_type,
                side_effects=[t.get("name", "") for t in (tools_called or [])],
                actor=ActorType.AGENT
            )

            return {
                "execution_id": str(execution_id),
                "session_id": self.session_id,
                "run_id": run_id,
            }


class _RunTracker:
    """Internal tracker for a single assistant run."""

    def __init__(self, client, assistant_id, goal, session_id):
        self._client = client
        self._assistant_id = assistant_id
        self._goal = goal
        self._session_id = session_id
        self._run = None
        self._messages = None
        self._tools_called = []

    def record_run(self, run: Any, messages: Any):
        """Record the run and messages."""
        self._run = run
        self._messages = messages

    def record_tool_call(self, tool_name: str, arguments: str = "", output: str = ""):
        """Record a tool call made during the run."""
        self._tools_called.append({
            "name": tool_name,
            "arguments": arguments,
            "output": output,
        })

    def _finalize(self):
        """Send tracking data to AEL."""
        if self._run is None:
            return

        # Extract run info
        run_id = getattr(self._run, 'id', 'unknown')
        status = getattr(self._run, 'status', 'unknown')
        model = getattr(self._run, 'model', 'unknown')

        # Extract messages
        message_list = []
        if self._messages and hasattr(self._messages, 'data'):
            for msg in self._messages.data:
                content = ""
                if hasattr(msg, 'content') and msg.content:
                    for block in msg.content:
                        if hasattr(block, 'text') and hasattr(block.text, 'value'):
                            content = block.text.value
                            break
                message_list.append({
                    "role": getattr(msg, 'role', 'unknown'),
                    "content": content[:500],
                })

        # Build options
        options = []
        if self._tools_called:
            for i, tool in enumerate(self._tools_called):
                options.append(ActionOption(
                    action=tool["name"],
                    score=1.0 / (i + 1),
                    reason=tool.get("arguments", "")[:100]
                ))
        else:
            options.append(ActionOption(
                action="generate_response",
                score=1.0,
                reason="Direct response"
            ))

        with self._client.intent(
            goal=self._goal,
            agent_id=f"openai-assistant-{self._assistant_id[:8]}",
            session_id=self._session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "assistant_id": self._assistant_id,
                "run_id": run_id,
                "messages": message_list,
            })

            chosen_action = self._tools_called[0]["name"] if self._tools_called else "generate_response"

            intent.decide(
                options=options,
                chosen_action=chosen_action,
                confidence=0.9 if status == "completed" else 0.5,
                model_version=model,
                reasoning=f"Run {status}",
            )

            result_type = ResultType.SUCCESS if status == "completed" else ResultType.FAILURE

            assistant_response = ""
            for msg in message_list:
                if msg["role"] == "assistant":
                    assistant_response = msg["content"]
                    break

            intent.execute(
                action=chosen_action,
                target={"response": assistant_response},
                result=result_type,
                side_effects=[t["name"] for t in self._tools_called],
                actor=ActorType.AGENT
            )


# Alias
OpenAIAssistantTracker = AELAssistantTracker
