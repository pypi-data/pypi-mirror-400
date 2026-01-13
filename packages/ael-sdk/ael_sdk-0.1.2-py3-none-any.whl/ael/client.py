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


class IntentHandle:
    """Context manager for tracking an intent through its lifecycle."""

    def __init__(self, client: "AELClient", intent_id: UUID, session_id: str):
        self.client = client
        self.intent_id = intent_id
        self.session_id = session_id
        self.context_id: Optional[UUID] = None
        self.decision_id: Optional[UUID] = None

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
        reasoning: Optional[str] = None
    ) -> UUID:
        """Record a decision."""
        if not self.context_id:
            raise ValueError("Must call snapshot_context before decide")

        response = self.client._post("/decisions", {
            "intent_id": str(self.intent_id),
            "context_id": str(self.context_id),
            "options": [opt.model_dump() for opt in options],
            "chosen_action": chosen_action,
            "confidence": confidence,
            "model_version": model_version,
            "rules_evaluated": rules_evaluated or [],
            "reasoning": reasoning
        })
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
        endpoint: str = "http://localhost:8000",
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
        constraints: Optional[List[str]] = None
    ):
        """
        Context manager for tracking an agent intent.

        Usage:
            with ael.intent("Handle refund request") as intent:
                intent.snapshot_context({"ticket_id": 123})
                intent.decide(...)
                intent.execute(...)
        """
        import uuid as uuid_module

        if session_id is None:
            session_id = str(uuid_module.uuid4())

        response = self._post("/intents", {
            "goal": goal,
            "origin": origin.value,
            "constraints": constraints or [],
            "agent_id": agent_id,
            "session_id": session_id
        })

        intent_id = UUID(response["id"])
        handle = IntentHandle(self, intent_id, session_id)

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

    def get_session_timeline(self, session_id: str) -> dict:
        """Get full timeline for a session."""
        return self._get(f"/sessions/{session_id}/timeline")

    def replay(self, execution_id: UUID, with_context_id: Optional[UUID] = None) -> dict:
        """Replay a decision."""
        data = {}
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
