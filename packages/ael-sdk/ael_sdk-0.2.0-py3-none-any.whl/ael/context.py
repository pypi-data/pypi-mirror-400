import hashlib
import json
from datetime import datetime
from typing import Any, Optional


class ContextBuilder:
    """
    Helper class for building context snapshots.

    Usage:
        ctx = ContextBuilder()
        ctx.add("ticket", ticket_data)
        ctx.add("customer", customer_data)
        ctx.set_version("crm", "v2.1")
        ctx.set_version("policy", "2026-01-01")

        with ael.intent("Handle ticket") as intent:
            intent.snapshot_context(ctx.inputs, ctx.versions)
    """

    def __init__(self):
        self._inputs: dict[str, Any] = {}
        self._versions: dict[str, str] = {}
        self._timestamp = datetime.utcnow().isoformat()

    def add(self, key: str, value: Any) -> "ContextBuilder":
        """Add an input to the context."""
        self._inputs[key] = value
        return self

    def add_all(self, data: dict) -> "ContextBuilder":
        """Add multiple inputs from a dictionary."""
        self._inputs.update(data)
        return self

    def set_version(self, system: str, version: str) -> "ContextBuilder":
        """Set the version of an external system."""
        self._versions[system] = version
        return self

    @property
    def inputs(self) -> dict:
        """Get all inputs."""
        return self._inputs

    @property
    def versions(self) -> dict:
        """Get all versions."""
        return self._versions

    def compute_hash(self) -> str:
        """Compute a hash of the context for integrity verification."""
        data = {
            "inputs": self._inputs,
            "versions": self._versions,
            "timestamp": self._timestamp
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()


def snapshot_context(
    inputs: dict,
    external_versions: Optional[dict] = None
) -> tuple[dict, dict]:
    """
    Simple function to prepare context data for snapshot.

    Returns:
        Tuple of (inputs, external_versions) ready for snapshot_context call
    """
    return inputs, external_versions or {}


def serialize_for_context(obj: Any) -> Any:
    """
    Serialize an object for inclusion in context.
    Handles common types that need special treatment.
    """
    if hasattr(obj, "model_dump"):
        # Pydantic model
        return obj.model_dump()
    elif hasattr(obj, "__dict__"):
        # Regular object
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_context(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize_for_context(v) for k, v in obj.items()}
    else:
        return obj
