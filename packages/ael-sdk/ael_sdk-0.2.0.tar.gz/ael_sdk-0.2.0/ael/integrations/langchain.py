"""
LangChain integration for AEL.

This module provides callbacks and utilities to track LangChain agent actions in AEL.
"""

from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.outputs import LLMResult
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object

from ..client import AELClient, ActionOption, ResultType, ActorType, OriginType


class AELCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler that records agent actions in AEL.

    Usage:
        from langchain.agents import create_react_agent, AgentExecutor
        from langchain_openai import ChatOpenAI
        from ael import AELClient
        from ael.integrations.langchain import AELCallbackHandler

        ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
        ael_handler = AELCallbackHandler(ael, agent_id="langchain-agent")

        llm = ChatOpenAI(model="gpt-4")
        agent = create_react_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools, callbacks=[ael_handler])

        # All agent actions are automatically logged to AEL
        result = executor.invoke({"input": "What is the weather in NYC?"})
    """

    def __init__(
        self,
        client: AELClient,
        agent_id: str = "langchain-agent",
        session_id: Optional[str] = None,
    ):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. Install with: pip install langchain-core"
            )
        super().__init__()
        self.client = client
        self.agent_id = agent_id
        self.session_id = session_id or str(uuid4())
        self._current_intent = None
        self._current_context = {}
        self._actions_taken = []
        self._llm_outputs = []

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts generating."""
        self._current_context["prompts"] = prompts
        self._current_context["llm_config"] = serialized

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM finishes generating."""
        self._llm_outputs.append({
            "generations": [
                [g.text for g in gen] for gen in response.generations
            ],
            "llm_output": response.llm_output,
        })

    def on_agent_action(
        self,
        action: AgentAction,
        **kwargs: Any,
    ) -> None:
        """Called when agent takes an action."""
        self._actions_taken.append({
            "tool": action.tool,
            "tool_input": action.tool_input,
            "log": action.log,
        })

    def on_agent_finish(
        self,
        finish: AgentFinish,
        **kwargs: Any,
    ) -> None:
        """Called when agent finishes. Records everything to AEL."""
        # Build options from actions taken
        options = []
        for i, action in enumerate(self._actions_taken):
            options.append(ActionOption(
                action=action["tool"],
                score=1.0 / (i + 1),  # Higher score for earlier actions
                reason=action.get("log", "")[:200]
            ))

        # If no actions, create a default option
        if not options:
            options.append(ActionOption(
                action="direct_response",
                score=1.0,
                reason="Agent responded directly without tool use"
            ))

        # Record to AEL
        with self.client.intent(
            goal=self._current_context.get("prompts", ["Unknown goal"])[0][:200],
            agent_id=self.agent_id,
            session_id=self.session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "input": self._current_context,
                "actions_taken": self._actions_taken,
            })

            chosen_action = self._actions_taken[-1]["tool"] if self._actions_taken else "direct_response"

            intent.decide(
                options=options,
                chosen_action=chosen_action,
                confidence=0.9,
                model_version=self._current_context.get("llm_config", {}).get("_type", "unknown"),
                reasoning=finish.log[:500] if finish.log else "",
            )

            intent.execute(
                action=chosen_action,
                target=finish.return_values,
                result=ResultType.SUCCESS,
                side_effects=[a["tool"] for a in self._actions_taken],
                actor=ActorType.AGENT
            )

        # Reset state
        self._current_context = {}
        self._actions_taken = []
        self._llm_outputs = []

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when chain errors."""
        if self._actions_taken:
            with self.client.intent(
                goal="Error during agent execution",
                agent_id=self.agent_id,
                session_id=self.session_id,
                origin=OriginType.AGENT
            ) as intent:
                intent.snapshot_context({
                    "input": self._current_context,
                    "error": str(error),
                })

                intent.decide(
                    options=[ActionOption(action="error", score=0.0, reason=str(error))],
                    chosen_action="error",
                    confidence=0.0,
                    model_version="unknown",
                    reasoning=f"Agent failed with error: {error}",
                )

                intent.execute(
                    action="error",
                    target={"error": str(error)},
                    result=ResultType.FAILURE,
                    actor=ActorType.AGENT
                )

        # Reset state
        self._current_context = {}
        self._actions_taken = []
        self._llm_outputs = []


# Alias for backward compatibility
LangChainCallback = AELCallbackHandler
