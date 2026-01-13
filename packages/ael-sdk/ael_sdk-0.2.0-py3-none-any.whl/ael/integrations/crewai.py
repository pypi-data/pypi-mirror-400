"""
CrewAI integration for AEL.

This module provides utilities to track CrewAI agent and crew actions in AEL.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4
from contextlib import contextmanager

from ..client import AELClient, ActionOption, ResultType, ActorType, OriginType


class AELCrewTracker:
    """
    Tracker for CrewAI agents and crews that records actions in AEL.

    Usage:
        from crewai import Agent, Task, Crew
        from ael import AELClient
        from ael.integrations.crewai import AELCrewTracker

        ael = AELClient(endpoint="http://localhost:8000", api_key="ael_xxx")
        tracker = AELCrewTracker(ael)

        # Define your crew
        researcher = Agent(role="Researcher", goal="...", backstory="...")
        writer = Agent(role="Writer", goal="...", backstory="...")

        task1 = Task(description="Research topic", agent=researcher)
        task2 = Task(description="Write article", agent=writer)

        crew = Crew(agents=[researcher, writer], tasks=[task1, task2])

        # Track crew execution
        with tracker.track_crew("Content creation pipeline") as t:
            result = crew.kickoff()
            t.record_result(result, agents=[researcher, writer], tasks=[task1, task2])
    """

    def __init__(
        self,
        client: AELClient,
        session_id: Optional[str] = None,
    ):
        self.client = client
        self.session_id = session_id or str(uuid4())

    @contextmanager
    def track_crew(self, goal: str, crew_id: str = "crewai-crew"):
        """
        Context manager for tracking a CrewAI crew execution.

        Usage:
            with tracker.track_crew("Research and write article") as t:
                result = crew.kickoff()
                t.record_result(result, agents=crew.agents, tasks=crew.tasks)
        """
        tracker = _CrewExecutionTracker(
            client=self.client,
            goal=goal,
            crew_id=crew_id,
            session_id=self.session_id,
        )
        try:
            yield tracker
        finally:
            tracker._finalize()

    @contextmanager
    def track_agent(self, agent_role: str, task_description: str):
        """
        Context manager for tracking a single CrewAI agent's task execution.

        Usage:
            with tracker.track_agent("Researcher", "Find information about AI") as t:
                # Agent executes task
                t.record_decision(
                    chosen="web_search",
                    confidence=0.85,
                    reasoning="Need current information",
                    options=[
                        {"action": "web_search", "score": 0.85},
                        {"action": "use_knowledge", "score": 0.15}
                    ]
                )
                t.record_execution(action="web_search", result="success")
        """
        tracker = _AgentTaskTracker(
            client=self.client,
            agent_role=agent_role,
            task_description=task_description,
            session_id=self.session_id,
        )
        try:
            yield tracker
        finally:
            tracker._finalize()

    def track_task_completion(
        self,
        agent_role: str,
        task_description: str,
        output: str,
        tools_used: Optional[List[str]] = None,
        reasoning: str = "",
    ) -> Dict[str, str]:
        """
        One-shot tracking of a completed CrewAI task.

        Args:
            agent_role: The role of the agent that completed the task
            task_description: Description of the task
            output: The task output/result
            tools_used: List of tools used during execution
            reasoning: Agent's reasoning for decisions made

        Returns:
            Dict with execution details
        """
        with self.client.intent(
            goal=task_description[:200],
            agent_id=f"crewai-{agent_role.lower().replace(' ', '-')}",
            session_id=self.session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "agent_role": agent_role,
                "task_description": task_description,
            })

            options = [
                ActionOption(
                    action=tool,
                    score=1.0 / (i + 1),
                    reason=f"Tool used in execution"
                )
                for i, tool in enumerate(tools_used or ["task_execution"])
            ]

            intent.decide(
                options=options,
                chosen_action=tools_used[0] if tools_used else "task_execution",
                confidence=0.9,
                model_version="crewai",
                reasoning=reasoning,
            )

            execution_id = intent.execute(
                action="complete_task",
                target={"output": output[:1000]},
                result=ResultType.SUCCESS,
                side_effects=tools_used or [],
                actor=ActorType.AGENT
            )

            return {
                "execution_id": str(execution_id),
                "session_id": self.session_id
            }


class _CrewExecutionTracker:
    """Internal tracker for crew execution."""

    def __init__(self, client, goal, crew_id, session_id):
        self._client = client
        self._goal = goal
        self._crew_id = crew_id
        self._session_id = session_id
        self._result = None
        self._agents = []
        self._tasks = []

    def record_result(
        self,
        result: Any,
        agents: Optional[List[Any]] = None,
        tasks: Optional[List[Any]] = None,
    ):
        """Record the crew execution result."""
        self._result = result
        self._agents = agents or []
        self._tasks = tasks or []

    def _finalize(self):
        """Send tracking data to AEL."""
        if self._result is None:
            return

        # Extract agent info
        agent_info = []
        for agent in self._agents:
            agent_info.append({
                "role": getattr(agent, 'role', 'unknown'),
                "goal": getattr(agent, 'goal', '')[:200],
            })

        # Extract task info
        task_info = []
        for task in self._tasks:
            task_info.append({
                "description": getattr(task, 'description', '')[:200],
                "agent": getattr(getattr(task, 'agent', None), 'role', 'unknown'),
            })

        with self._client.intent(
            goal=self._goal,
            agent_id=self._crew_id,
            session_id=self._session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "agents": agent_info,
                "tasks": task_info,
            })

            options = [
                ActionOption(
                    action=f"task_{i}",
                    score=1.0 / (i + 1),
                    reason=t.get("description", "")[:100]
                )
                for i, t in enumerate(task_info)
            ] or [ActionOption(action="execute_crew", score=1.0)]

            intent.decide(
                options=options,
                chosen_action="execute_crew",
                confidence=0.9,
                model_version="crewai",
                reasoning=f"Crew completed {len(task_info)} tasks with {len(agent_info)} agents",
            )

            result_str = str(self._result)[:1000] if self._result else ""

            intent.execute(
                action="crew_completion",
                target={"result": result_str},
                result=ResultType.SUCCESS,
                side_effects=[t.get("description", "")[:50] for t in task_info],
                actor=ActorType.AGENT
            )


class _AgentTaskTracker:
    """Internal tracker for single agent task execution."""

    def __init__(self, client, agent_role, task_description, session_id):
        self._client = client
        self._agent_role = agent_role
        self._task_description = task_description
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
        action: str,
        result: str = "success",
        output: Optional[Dict] = None,
        tools_used: Optional[List[str]] = None,
    ):
        """Record the execution result."""
        self._execution_data = {
            "action": action,
            "result": result,
            "output": output or {},
            "tools_used": tools_used or [],
        }

    def _finalize(self):
        """Send tracking data to AEL."""
        if not self._decision_data:
            return

        with self._client.intent(
            goal=self._task_description[:200],
            agent_id=f"crewai-{self._agent_role.lower().replace(' ', '-')}",
            session_id=self._session_id,
            origin=OriginType.AGENT
        ) as intent:
            intent.snapshot_context({
                "agent_role": self._agent_role,
                "task": self._task_description,
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
                model_version="crewai",
                reasoning=self._decision_data.get("reasoning", ""),
            )

            if self._execution_data:
                result_map = {
                    "success": ResultType.SUCCESS,
                    "failure": ResultType.FAILURE,
                    "pending": ResultType.PENDING
                }
                intent.execute(
                    action=self._execution_data["action"],
                    target=self._execution_data.get("output", {}),
                    result=result_map.get(self._execution_data["result"], ResultType.SUCCESS),
                    side_effects=self._execution_data.get("tools_used", []),
                    actor=ActorType.AGENT
                )


# Alias
CrewAITracker = AELCrewTracker
