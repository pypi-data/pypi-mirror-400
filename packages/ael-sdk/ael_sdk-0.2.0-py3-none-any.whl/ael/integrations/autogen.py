"""
AutoGen integration for AEL.

This module provides utilities to track Microsoft AutoGen agent actions in AEL.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4
from contextlib import contextmanager

from ..client import AELClient, ActionOption, ResultType, ActorType, OriginType


class AELAutoGenTracker:
    """
    Tracker for Microsoft AutoGen agents that records actions in AEL.

    Usage:
        from autogen import AssistantAgent, UserProxyAgent
        from ael import AELClient
        from ael.integrations.autogen import AELAutoGenTracker

        ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
        tracker = AELAutoGenTracker(ael)

        assistant = AssistantAgent("assistant", llm_config={"model": "gpt-4"})
        user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding"})

        # Track a conversation
        with tracker.track_conversation("Solve coding problem") as t:
            user_proxy.initiate_chat(assistant, message="Write a Python function to sort a list")
            t.record_messages(user_proxy.chat_messages[assistant])
    """

    def __init__(
        self,
        client: AELClient,
        session_id: Optional[str] = None,
    ):
        self.client = client
        self.session_id = session_id or str(uuid4())

    @contextmanager
    def track_conversation(self, goal: str, agent_id: str = "autogen-agent"):
        """
        Context manager for tracking an AutoGen conversation.

        Usage:
            with tracker.track_conversation("Solve problem") as t:
                user_proxy.initiate_chat(assistant, message="...")
                t.record_messages(chat_messages)
        """
        tracker = _ConversationTracker(
            client=self.client,
            goal=goal,
            agent_id=agent_id,
            session_id=self.session_id,
        )
        try:
            yield tracker
        finally:
            tracker._finalize()

    @contextmanager
    def track_agent_action(self, agent_name: str, action_type: str):
        """
        Context manager for tracking a single agent action.

        Usage:
            with tracker.track_agent_action("assistant", "code_generation") as t:
                # Agent performs action
                t.record_decision(
                    chosen="write_function",
                    confidence=0.9,
                    reasoning="User requested a sorting function"
                )
                t.record_execution(result="success", output={"code": "def sort..."})
        """
        tracker = _ActionTracker(
            client=self.client,
            agent_name=agent_name,
            action_type=action_type,
            session_id=self.session_id,
        )
        try:
            yield tracker
        finally:
            tracker._finalize()

    def track_message(
        self,
        sender: str,
        receiver: str,
        content: str,
        message_type: str = "text",
        function_call: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """
        Track a single message exchange between agents.

        Args:
            sender: Name of the sending agent
            receiver: Name of the receiving agent
            content: Message content
            message_type: Type of message (text, function_call, function_response)
            function_call: Function call details if applicable

        Returns:
            Dict with execution details
        """
        options = [
            ActionOption(
                action=message_type,
                score=1.0,
                reason=f"Message from {sender} to {receiver}"
            )
        ]

        if function_call:
            options.append(ActionOption(
                action=function_call.get("name", "function"),
                score=0.9,
                reason=function_call.get("arguments", "")[:100]
            ))

        with self.client.intent(
            goal=f"Agent communication: {sender} -> {receiver}",
            agent_id=f"autogen-{sender.lower().replace(' ', '-')}",
            session_id=self.session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "sender": sender,
                "receiver": receiver,
                "content": content[:500],
                "message_type": message_type,
            })

            intent.decide(
                options=options,
                chosen_action=message_type,
                confidence=0.9,
                model_version="autogen",
                reasoning=f"{sender} sending {message_type} to {receiver}",
            )

            execution_id = intent.execute(
                action="send_message",
                target={"receiver": receiver, "content": content[:500]},
                result=ResultType.SUCCESS,
                side_effects=[function_call["name"]] if function_call else [],
                actor=ActorType.AGENT
            )

            return {
                "execution_id": str(execution_id),
                "session_id": self.session_id
            }


class _ConversationTracker:
    """Internal tracker for AutoGen conversations."""

    def __init__(self, client, goal, agent_id, session_id):
        self._client = client
        self._goal = goal
        self._agent_id = agent_id
        self._session_id = session_id
        self._messages = []
        self._agents = set()

    def record_messages(self, messages: List[Dict[str, Any]]):
        """Record the conversation messages."""
        self._messages = messages
        for msg in messages:
            if "name" in msg:
                self._agents.add(msg["name"])
            if "role" in msg:
                self._agents.add(msg["role"])

    def add_agent(self, agent_name: str):
        """Add an agent to the tracked agents."""
        self._agents.add(agent_name)

    def _finalize(self):
        """Send tracking data to AEL."""
        if not self._messages:
            return

        # Build summary
        message_summary = []
        for msg in self._messages[-10:]:  # Last 10 messages
            content = msg.get("content", "")
            if isinstance(content, str):
                content = content[:200]
            message_summary.append({
                "role": msg.get("role", msg.get("name", "unknown")),
                "content": content,
            })

        options = [
            ActionOption(
                action=f"agent_{agent}",
                score=1.0 / (i + 1),
                reason=f"Participated in conversation"
            )
            for i, agent in enumerate(self._agents)
        ] or [ActionOption(action="conversation", score=1.0)]

        with self._client.intent(
            goal=self._goal,
            agent_id=self._agent_id,
            session_id=self._session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "agents": list(self._agents),
                "message_count": len(self._messages),
                "messages": message_summary,
            })

            intent.decide(
                options=options,
                chosen_action="multi_agent_conversation",
                confidence=0.9,
                model_version="autogen",
                reasoning=f"Conversation with {len(self._agents)} agents, {len(self._messages)} messages",
            )

            # Get final response
            final_content = ""
            if self._messages:
                last_msg = self._messages[-1]
                final_content = last_msg.get("content", "")
                if isinstance(final_content, str):
                    final_content = final_content[:500]

            intent.execute(
                action="conversation_complete",
                target={"final_response": final_content},
                result=ResultType.SUCCESS,
                side_effects=list(self._agents),
                actor=ActorType.AGENT
            )


class _ActionTracker:
    """Internal tracker for single agent actions."""

    def __init__(self, client, agent_name, action_type, session_id):
        self._client = client
        self._agent_name = agent_name
        self._action_type = action_type
        self._session_id = session_id
        self._decision_data = None
        self._execution_data = None

    def record_decision(
        self,
        chosen: str,
        confidence: float,
        reasoning: str = "",
        options: Optional[List[Dict]] = None,
    ):
        """Record the agent's decision."""
        self._decision_data = {
            "chosen": chosen,
            "confidence": confidence,
            "reasoning": reasoning,
            "options": options or [{"action": chosen, "score": confidence}],
        }

    def record_execution(
        self,
        result: str = "success",
        output: Optional[Dict] = None,
        side_effects: Optional[List[str]] = None,
    ):
        """Record the execution result."""
        self._execution_data = {
            "result": result,
            "output": output or {},
            "side_effects": side_effects or [],
        }

    def _finalize(self):
        """Send tracking data to AEL."""
        if not self._decision_data:
            return

        with self._client.intent(
            goal=f"{self._agent_name}: {self._action_type}",
            agent_id=f"autogen-{self._agent_name.lower().replace(' ', '-')}",
            session_id=self._session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "agent_name": self._agent_name,
                "action_type": self._action_type,
            })

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
                model_version="autogen",
                reasoning=self._decision_data.get("reasoning", ""),
            )

            if self._execution_data:
                result_map = {
                    "success": ResultType.SUCCESS,
                    "failure": ResultType.FAILURE,
                    "pending": ResultType.PENDING
                }
                intent.execute(
                    action=self._action_type,
                    target=self._execution_data.get("output", {}),
                    result=result_map.get(self._execution_data["result"], ResultType.SUCCESS),
                    side_effects=self._execution_data.get("side_effects", []),
                    actor=ActorType.AGENT
                )


# Alias
AutoGenTracker = AELAutoGenTracker
