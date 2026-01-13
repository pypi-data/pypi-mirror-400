import functools
import inspect
from typing import Callable, Optional
from uuid import uuid4

from .client import AELClient, ActionOption, ResultType, ActorType


def track(
    client: AELClient,
    goal: str,
    agent_id: str = "default",
    model_version: str = "unknown"
):
    """
    Decorator to automatically track function executions in the AEL.

    Usage:
        @ael.track(goal="Process customer refund")
        def handle_refund(ticket_id: str, amount: float):
            # Your agent logic here
            return {"status": "approved", "amount": amount}

    The decorator will:
    1. Create an intent with the specified goal
    2. Snapshot the function arguments as context
    3. Record a decision based on the function execution
    4. Record the execution result
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            session_id = str(uuid4())

            # Get function signature to capture all args
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            inputs = dict(bound_args.arguments)

            with client.intent(
                goal=goal,
                agent_id=agent_id,
                session_id=session_id
            ) as intent:
                # Snapshot context (function inputs)
                intent.snapshot_context(inputs)

                # Execute the function
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)

                # Record decision (we treat the function as a single decision)
                action_name = func.__name__
                intent.decide(
                    options=[
                        ActionOption(
                            action=action_name,
                            target=inputs,
                            score=1.0 if success else 0.0,
                            reason="Function executed" if success else f"Error: {error}"
                        )
                    ],
                    chosen_action=action_name,
                    confidence=1.0 if success else 0.0,
                    model_version=model_version,
                    reasoning=f"Executed {action_name} with args: {list(inputs.keys())}"
                )

                # Record execution
                intent.execute(
                    action=action_name,
                    target={"args": inputs, "result": result if success else None},
                    result=ResultType.SUCCESS if success else ResultType.FAILURE,
                    side_effects=[f"called_{action_name}"],
                    actor=ActorType.AGENT
                )

                if not success:
                    raise Exception(error)

                return result

        return wrapper
    return decorator
