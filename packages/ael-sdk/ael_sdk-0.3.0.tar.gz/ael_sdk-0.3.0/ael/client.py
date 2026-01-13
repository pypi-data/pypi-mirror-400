import httpx
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from contextlib import contextmanager
from enum import Enum


class OriginType(str, Enum):
    HUMAN = "human"
    AGENT = "agent"
    SCHEDULER = "scheduler"


class ResultType(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"


class ActorType(str, Enum):
    AGENT = "agent"
    HUMAN = "human"


class ActionOption(BaseModel):
    action: str
    target: Optional[dict] = None
    score: float
    reason: Optional[str] = None


class ReplayConfig(BaseModel):
    """Configuration for replaying a decision with an LLM."""
    model: str = "gpt-4o-mini"
    temperature: float = 0.0  # Use 0 for deterministic replay
    max_tokens: int = 1000
    api_base: Optional[str] = None


class IntentHandle:
    """Context manager for tracking an intent through its lifecycle."""

    def __init__(
        self,
        client: "AELClient",
        intent_id: UUID,
        session_id: str,
        parent_intent_id: Optional[UUID] = None
    ):
        self.client = client
        self.intent_id = intent_id
        self.session_id = session_id
        self.parent_intent_id = parent_intent_id
        self.context_id: Optional[UUID] = None
        self.decision_id: Optional[UUID] = None

    def child_intent(
        self,
        goal: str,
        agent_id: str = "default",
        origin: "OriginType" = None,
        constraints: Optional[List[str]] = None,
        mcp_server: Optional[str] = None,
        tool_name: Optional[str] = None
    ):
        """Create a child intent that links back to this parent intent.

        Use this when delegating to sub-agents or calling MCP tools.

        Usage:
            with parent_intent.child_intent("Search documents", mcp_server="filesystem") as child:
                child.snapshot_context({"query": "test"})
                child.decide(...)
                child.execute(...)
        """
        if origin is None:
            origin = OriginType.AGENT
        return self.client.intent(
            goal=goal,
            agent_id=agent_id,
            session_id=self.session_id,
            origin=origin,
            constraints=constraints,
            parent_intent_id=self.intent_id,
            mcp_server=mcp_server,
            tool_name=tool_name
        )

    def snapshot_context(
        self,
        inputs: dict,
        external_versions: Optional[dict] = None
    ) -> UUID:
        """Capture the context the agent sees."""
        response = self.client._post("/contexts", {
            "intent_id": str(self.intent_id),
            "inputs": inputs,
            "external_versions": external_versions or {}
        })
        self.context_id = UUID(response["id"])
        return self.context_id

    def decide(
        self,
        options: List[ActionOption],
        chosen_action: str,
        confidence: float,
        model_version: str = "unknown",
        rules_evaluated: Optional[List[str]] = None,
        reasoning: Optional[str] = None,
        replay_prompt: Optional[str] = None,
        replay_config: Optional["ReplayConfig"] = None,
    ) -> UUID:
        """Record a decision.

        Args:
            options: List of options that were considered
            chosen_action: The action that was selected
            confidence: Confidence score (0-1)
            model_version: Version of the model/agent that made the decision
            rules_evaluated: List of rules that were evaluated
            reasoning: Explanation of why this action was chosen
            replay_prompt: The full prompt sent to the LLM (enables replay)
            replay_config: Model configuration for replay (model, temperature, etc.)
        """
        if not self.context_id:
            raise ValueError("Must call snapshot_context before decide")

        data = {
            "intent_id": str(self.intent_id),
            "context_id": str(self.context_id),
            "options": [opt.model_dump() for opt in options],
            "chosen_action": chosen_action,
            "confidence": confidence,
            "model_version": model_version,
            "rules_evaluated": rules_evaluated or [],
            "reasoning": reasoning
        }

        if replay_prompt:
            data["replay_prompt"] = replay_prompt
        if replay_config:
            data["replay_config"] = replay_config.model_dump()

        response = self.client._post("/decisions", data)
        self.decision_id = UUID(response["id"])
        return self.decision_id

    def execute(
        self,
        action: str,
        target: dict,
        result: ResultType = ResultType.SUCCESS,
        side_effects: Optional[List[str]] = None,
        revert_action: Optional[dict] = None,
        actor: ActorType = ActorType.AGENT,
        override_reason: Optional[str] = None
    ) -> UUID:
        """Record an execution."""
        if not self.decision_id:
            raise ValueError("Must call decide before execute")

        response = self.client._post("/executions", {
            "decision_id": str(self.decision_id),
            "action": action,
            "target": target,
            "result": result.value,
            "side_effects": side_effects or [],
            "revert_action": revert_action,
            "actor": actor.value,
            "override_reason": override_reason
        })
        return UUID(response["id"])


class AELClient:
    """Client for interacting with the Agent Execution Ledger API."""

    def __init__(
        self,
        endpoint: str = "https://ael-backend.onrender.com",
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _post(self, path: str, data: dict) -> dict:
        url = f"{self.endpoint}/api/v1{path}"
        response = self._client.post(url, json=data, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def _get(self, path: str) -> dict:
        url = f"{self.endpoint}/api/v1{path}"
        response = self._client.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @contextmanager
    def intent(
        self,
        goal: str,
        agent_id: str = "default",
        session_id: Optional[str] = None,
        origin: OriginType = OriginType.AGENT,
        constraints: Optional[List[str]] = None,
        parent_intent_id: Optional[UUID] = None,
        mcp_server: Optional[str] = None,
        tool_name: Optional[str] = None
    ):
        """
        Context manager for tracking an agent intent.

        Usage:
            with ael.intent("Handle refund request") as intent:
                intent.snapshot_context({"ticket_id": 123})
                intent.decide(...)
                intent.execute(...)

        For multi-agent or MCP tool calls, use parent_intent_id:
            with ael.intent("Main task") as parent:
                # ... parent logic ...
                with parent.child_intent("Sub-task", mcp_server="filesystem") as child:
                    # ... child logic ...
        """
        import uuid as uuid_module

        if session_id is None:
            session_id = str(uuid_module.uuid4())

        data = {
            "goal": goal,
            "origin": origin.value,
            "constraints": constraints or [],
            "agent_id": agent_id,
            "session_id": session_id
        }

        if parent_intent_id:
            data["parent_intent_id"] = str(parent_intent_id)
        if mcp_server:
            data["mcp_server"] = mcp_server
        if tool_name:
            data["tool_name"] = tool_name

        response = self._post("/intents", data)

        intent_id = UUID(response["id"])
        handle = IntentHandle(self, intent_id, session_id, parent_intent_id)

        try:
            yield handle
        except Exception:
            # Could log failed intents here
            raise

    def track(self, goal: str, agent_id: str = "default"):
        """Decorator for tracking function executions as agent actions."""
        from .decorators import track as track_decorator
        return track_decorator(self, goal, agent_id)

    def get_execution(self, execution_id: UUID) -> dict:
        """Get execution details."""
        return self._get(f"/executions/{execution_id}")

    def get_intent(self, intent_id: UUID) -> dict:
        """Get intent details."""
        return self._get(f"/intents/{intent_id}")

    def get_intent_hierarchy(self, intent_id: UUID) -> List[dict]:
        """Get the full parent chain from root to this intent.

        Returns list of intents from root parent to the specified intent.
        Useful for showing breadcrumb navigation in multi-agent scenarios.
        """
        return self._get(f"/intents/{intent_id}/hierarchy")

    def get_intent_children(self, intent_id: UUID) -> List[dict]:
        """Get all direct child intents of this intent.

        Returns list of child intents spawned by this parent intent.
        """
        return self._get(f"/intents/{intent_id}/children")

    def get_intent_tree(self, intent_id: UUID) -> dict:
        """Get full intent tree recursively from this intent as root.

        Returns nested structure showing all descendant intents.
        Useful for visualizing complete multi-agent delegation chains.
        """
        return self._get(f"/intents/{intent_id}/tree")

    def get_session_timeline(self, session_id: str) -> dict:
        """Get full timeline for a session."""
        return self._get(f"/sessions/{session_id}/timeline")

    def replay(
        self,
        execution_id: UUID,
        with_context_id: Optional[UUID] = None,
        force_llm_call: bool = False
    ) -> dict:
        """Replay a decision to verify determinism or test what-if scenarios.

        Args:
            execution_id: The execution to replay
            with_context_id: Optional different context for what-if analysis
            force_llm_call: Force actual LLM call even if context hasn't changed

        Returns:
            ReplayResponse with original and replayed decisions, plus divergence info
        """
        data = {"force_llm_call": force_llm_call}
        if with_context_id:
            data["with_context_id"] = str(with_context_id)
        return self._post(f"/replay/{execution_id}", data)

    def revert(self, execution_id: UUID, reason: str, force: bool = False) -> dict:
        """Revert an execution."""
        return self._post(f"/revert/{execution_id}", {
            "reason": reason,
            "force": force
        })

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
