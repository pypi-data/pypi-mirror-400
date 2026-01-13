"""
Google ADK (Agent Development Kit) integration for AEL.

This module provides a callback that integrates with Google's ADK
to automatically capture agent decisions and executions.
"""

from typing import Any, Optional
from uuid import uuid4

from ..client import AELClient, ActionOption, ResultType, ActorType, OriginType


class AELCallback:
    """
    Callback for Google ADK that tracks agent actions in AEL.

    Usage with Google ADK:
        from google import genai
        from google.genai import types
        from ael.integrations.google_adk import AELCallback

        ael_client = AELClient(endpoint="http://localhost:8000")
        ael_callback = AELCallback(client=ael_client, agent_id="support-agent")

        # Use with ADK agent
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Handle this customer request...",
            config=types.GenerateContentConfig(
                tools=[...],
            )
        )

        # Track the agent action
        ael_callback.on_agent_action(
            goal="Handle customer request",
            inputs={"customer_message": "..."},
            model_response=response,
            tool_calls=[...],
            result={"status": "completed"}
        )
    """

    def __init__(
        self,
        client: AELClient,
        agent_id: str = "google-adk-agent",
        model_version: str = "gemini-2.0-flash"
    ):
        self.client = client
        self.agent_id = agent_id
        self.model_version = model_version
        self._current_session: Optional[str] = None
        self._current_intent = None

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new tracking session."""
        self._current_session = session_id or str(uuid4())
        return self._current_session

    def on_agent_action(
        self,
        goal: str,
        inputs: dict,
        model_response: Any,
        tool_calls: Optional[list[dict]] = None,
        result: Optional[dict] = None,
        success: bool = True,
        reasoning: Optional[str] = None
    ) -> dict:
        """
        Track a complete agent action cycle.

        Args:
            goal: What the agent was trying to accomplish
            inputs: The context/inputs the agent received
            model_response: The raw model response (will extract relevant parts)
            tool_calls: List of tool calls made by the agent
            result: The final result of the action
            success: Whether the action succeeded
            reasoning: Optional reasoning/explanation

        Returns:
            Dict with intent_id, context_id, decision_id, execution_id
        """
        session_id = self._current_session or str(uuid4())

        with self.client.intent(
            goal=goal,
            agent_id=self.agent_id,
            session_id=session_id,
            origin=OriginType.AGENT
        ) as intent:
            # Snapshot context
            external_versions = {
                "model": self.model_version,
                "adk_version": "0.3.0"  # Track ADK version
            }
            intent.snapshot_context(inputs, external_versions)

            # Build options from tool calls if available
            options = []
            if tool_calls:
                for i, call in enumerate(tool_calls):
                    options.append(ActionOption(
                        action=call.get("name", f"tool_{i}"),
                        target=call.get("args", {}),
                        score=call.get("confidence", 0.9),
                        reason=call.get("reason")
                    ))
            else:
                # Single action option
                options.append(ActionOption(
                    action="generate_response",
                    target=inputs,
                    score=1.0 if success else 0.0
                ))

            # Extract chosen action
            chosen_action = options[0].action if options else "unknown"

            # Get reasoning from model response if not provided
            if not reasoning and hasattr(model_response, "text"):
                reasoning = f"Model response: {str(model_response.text)[:500]}"

            # Record decision
            intent.decide(
                options=options,
                chosen_action=chosen_action,
                confidence=0.9 if success else 0.1,
                model_version=self.model_version,
                rules_evaluated=["adk_tool_selection"],
                reasoning=reasoning
            )

            # Record execution
            execution_id = intent.execute(
                action=chosen_action,
                target={"inputs": inputs, "result": result},
                result=ResultType.SUCCESS if success else ResultType.FAILURE,
                side_effects=[f"tool_call_{tc.get('name', 'unknown')}" for tc in (tool_calls or [])],
                actor=ActorType.AGENT
            )

            return {
                "intent_id": str(intent.intent_id),
                "context_id": str(intent.context_id),
                "decision_id": str(intent.decision_id),
                "execution_id": str(execution_id),
                "session_id": session_id
            }

    def on_tool_call(
        self,
        tool_name: str,
        tool_args: dict,
        tool_result: Any,
        success: bool = True
    ):
        """
        Track individual tool calls within an agent session.

        This is useful for fine-grained tracking of each tool invocation.
        """
        # For MVP, we track tool calls as part of the agent action
        # In production, this could create separate ledger entries
        pass

    def on_human_override(
        self,
        original_decision_id: str,
        override_action: str,
        reason: str,
        target: dict
    ) -> dict:
        """
        Record when a human overrides an agent decision.
        """
        # Create a new execution recording the override
        # This requires the decision_id from a previous action
        from uuid import UUID

        execution_data = {
            "decision_id": original_decision_id,
            "action": override_action,
            "target": target,
            "result": "success",
            "side_effects": ["human_override"],
            "actor": "human",
            "override_reason": reason
        }

        response = self.client._post("/executions", execution_data)
        return response


class AELToolWrapper:
    """
    Wrapper for ADK tools that automatically tracks their usage.

    Usage:
        from google.genai import types

        @ael_tool_wrapper.wrap
        def process_refund(ticket_id: str, amount: float) -> dict:
            # Your tool implementation
            return {"status": "approved"}

        # The tool will now automatically track calls in AEL
    """

    def __init__(self, callback: AELCallback):
        self.callback = callback

    def wrap(self, func):
        """Decorator to wrap a tool function with AEL tracking."""
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tool_args = kwargs.copy()

            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = {"error": str(e)}
                success = False
                raise

            finally:
                self.callback.on_tool_call(
                    tool_name=func.__name__,
                    tool_args=tool_args,
                    tool_result=result,
                    success=success
                )

            return result

        return wrapper
