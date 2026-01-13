"""
Google ADK (Agent Development Kit) integration for AEL.

This module provides utilities to track Google ADK agent actions in AEL.
"""

from typing import Any, Optional
from uuid import uuid4
from contextlib import contextmanager

from ..client import AELClient, ActionOption, ResultType, ActorType, OriginType


class AELTracker:
    """
    Tracker for Google ADK agents that records actions in AEL.

    Usage with Google ADK:
        from google import genai
        from google.adk import Agent
        from ael import AELClient
        from ael.integrations.google_adk import AELTracker

        # Initialize
        ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
        tracker = AELTracker(ael, agent_id="support-agent")

        # Create your ADK agent
        agent = Agent(name="support", model="gemini-2.0-flash", ...)

        # Track agent interactions
        with tracker.track("Handle refund request") as t:
            t.context({"customer_id": "123", "request": "refund"})

            # Run your agent
            response = agent.run(user_input)

            # Record what happened
            t.decision(
                chosen="approve_refund",
                confidence=0.92,
                reasoning=response.text,
                options=[
                    {"action": "approve_refund", "score": 0.92},
                    {"action": "deny_refund", "score": 0.08},
                ]
            )
            t.execute(action="approve_refund", result="success")
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

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new tracking session."""
        self._current_session = session_id or str(uuid4())
        return self._current_session

    @contextmanager
    def track(self, goal: str, session_id: Optional[str] = None):
        """
        Context manager for tracking an agent action.

        Usage:
            with tracker.track("Handle customer request") as t:
                t.context({"input": "..."})
                # ... run agent ...
                t.decision(chosen="action", confidence=0.9, ...)
                t.execute(action="action", result="success")
        """
        session = session_id or self._current_session or str(uuid4())
        tracker = _ActionTracker(
            client=self.client,
            goal=goal,
            agent_id=self.agent_id,
            session_id=session,
            model_version=self.model_version
        )
        try:
            yield tracker
        finally:
            tracker._finalize()

    def track_action(
        self,
        goal: str,
        inputs: dict,
        chosen_action: str,
        confidence: float,
        reasoning: str,
        options: Optional[list[dict]] = None,
        result: str = "success",
        side_effects: Optional[list[str]] = None,
    ) -> dict:
        """
        One-shot tracking of a complete agent action.

        Args:
            goal: What the agent was trying to accomplish
            inputs: The context/inputs the agent received
            chosen_action: The action the agent chose
            confidence: Confidence score (0-1)
            reasoning: Why the agent made this decision
            options: List of options considered [{"action": str, "score": float, "reason": str}]
            result: "success", "failure", or "pending"
            side_effects: List of side effects

        Returns:
            Dict with execution details
        """
        session_id = self._current_session or str(uuid4())

        with self.client.intent(
            goal=goal,
            agent_id=self.agent_id,
            session_id=session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context(inputs, {"model": self.model_version})

            # Build options
            action_options = []
            if options:
                for opt in options:
                    action_options.append(ActionOption(
                        action=opt.get("action", "unknown"),
                        score=opt.get("score", 0.5),
                        reason=opt.get("reason")
                    ))
            else:
                action_options.append(ActionOption(
                    action=chosen_action,
                    score=confidence
                ))

            intent.decide(
                options=action_options,
                chosen_action=chosen_action,
                confidence=confidence,
                model_version=self.model_version,
                reasoning=reasoning
            )

            result_type = {
                "success": ResultType.SUCCESS,
                "failure": ResultType.FAILURE,
                "pending": ResultType.PENDING
            }.get(result, ResultType.SUCCESS)

            execution_id = intent.execute(
                action=chosen_action,
                target=inputs,
                result=result_type,
                side_effects=side_effects or [],
                actor=ActorType.AGENT
            )

            return {
                "execution_id": str(execution_id),
                "session_id": session_id
            }


class _ActionTracker:
    """Internal tracker for a single action within a track() context."""

    def __init__(self, client, goal, agent_id, session_id, model_version):
        self._client = client
        self._goal = goal
        self._agent_id = agent_id
        self._session_id = session_id
        self._model_version = model_version
        self._context_data = {}
        self._decision_data = None
        self._execution_data = None
        self._intent_handle = None

    def context(self, inputs: dict, external_versions: Optional[dict] = None):
        """Record the context the agent saw."""
        self._context_data = {
            "inputs": inputs,
            "external_versions": external_versions or {"model": self._model_version}
        }

    def decision(
        self,
        chosen: str,
        confidence: float,
        reasoning: str = "",
        options: Optional[list[dict]] = None,
        rules_evaluated: Optional[list[str]] = None
    ):
        """Record the decision made by the agent."""
        self._decision_data = {
            "chosen": chosen,
            "confidence": confidence,
            "reasoning": reasoning,
            "options": options or [{"action": chosen, "score": confidence}],
            "rules_evaluated": rules_evaluated or []
        }

    def execute(
        self,
        action: str,
        result: str = "success",
        target: Optional[dict] = None,
        side_effects: Optional[list[str]] = None,
        revert_action: Optional[dict] = None
    ):
        """Record the execution result."""
        self._execution_data = {
            "action": action,
            "result": result,
            "target": target or self._context_data.get("inputs", {}),
            "side_effects": side_effects or [],
            "revert_action": revert_action
        }

    def _finalize(self):
        """Finalize and send all tracking data to AEL."""
        if not self._decision_data:
            return  # Nothing to track

        with self._client.intent(
            goal=self._goal,
            agent_id=self._agent_id,
            session_id=self._session_id,
            origin=OriginType.AGENT
        ) as intent:
            # Context
            intent.snapshot_context(
                self._context_data.get("inputs", {}),
                self._context_data.get("external_versions", {})
            )

            # Decision
            options = [
                ActionOption(
                    action=opt.get("action", "unknown"),
                    score=opt.get("score", 0.5),
                    reason=opt.get("reason")
                )
                for opt in self._decision_data.get("options", [])
            ]

            intent.decide(
                options=options,
                chosen_action=self._decision_data["chosen"],
                confidence=self._decision_data["confidence"],
                model_version=self._model_version,
                reasoning=self._decision_data.get("reasoning", ""),
                rules_evaluated=self._decision_data.get("rules_evaluated", [])
            )

            # Execution
            if self._execution_data:
                result_map = {
                    "success": ResultType.SUCCESS,
                    "failure": ResultType.FAILURE,
                    "pending": ResultType.PENDING
                }
                intent.execute(
                    action=self._execution_data["action"],
                    target=self._execution_data["target"],
                    result=result_map.get(self._execution_data["result"], ResultType.SUCCESS),
                    side_effects=self._execution_data.get("side_effects", []),
                    revert_action=self._execution_data.get("revert_action"),
                    actor=ActorType.AGENT
                )


# Backward compatibility alias
AELCallback = AELTracker
