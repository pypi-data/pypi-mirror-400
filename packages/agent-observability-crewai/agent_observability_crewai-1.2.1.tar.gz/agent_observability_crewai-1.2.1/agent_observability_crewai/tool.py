"""CrewAI tool for Agent Observability.

Provides structured logging for multi-agent CrewAI workflows with
per-agent and per-crew cost tracking.
"""

from __future__ import annotations

from typing import Optional, Any, Type
import os

from pydantic import BaseModel, Field

try:
    from crewai_tools import BaseTool
except ImportError:
    # Fallback for when crewai_tools is not installed
    BaseTool = object

try:
    from agent_observability import AgentLogger
except ImportError:
    AgentLogger = None


class LogEventInput(BaseModel):
    """Input schema for logging events."""

    event_type: str = Field(
        description="Type of event: 'api_call', 'decision', 'task_complete', 'error', 'delegation'"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Event metadata (agent_role, cost_usd, latency_ms, task_id, etc.)"
    )
    severity: str = Field(
        default="info",
        description="Severity: 'debug', 'info', 'warning', 'error', 'critical'"
    )


class AgentObservabilityTool(BaseTool):
    """CrewAI tool for logging agent events.

    Integrates with CrewAI's task execution to provide:
        - Structured event logging per agent
        - Cost tracking per crew/agent/task
        - Performance analytics
        - Compliance audit trails
        - Multi-agent workflow visibility

    Perfect for production crews that need:
        - Cost allocation per agent role
        - Task completion tracking
        - Delegation chain auditing
        - Error investigation

    Setup (Auto-Registration - v1.1.0+):
        Just add to agent - auto-registers on first log:
        ```python
        from agent_observability_crewai import AgentObservabilityTool
        agent = Agent(tools=[AgentObservabilityTool()])
        # First log auto-registers and shows API key
        ```

    Setup (Traditional):
        1. export AGENT_OBS_API_KEY=ao_live_...
        2. Add to agent:
           from agent_observability_crewai import AgentObservabilityTool
           agent = Agent(tools=[AgentObservabilityTool()])

    Example:
        ```python
        from crewai import Agent, Task, Crew
        from agent_observability_crewai import AgentObservabilityTool

        obs_tool = AgentObservabilityTool(crew_id="research-crew-v1")

        researcher = Agent(
            role="Researcher",
            tools=[obs_tool],
            verbose=True
        )

        crew = Crew(agents=[researcher], tasks=[...])
        crew.kickoff()
        ```
    """

    name: str = "agent_observability"
    description: str = (
        "Log agent events for observability, cost tracking, and compliance in multi-agent workflows. "
        "Use this to track API calls, decisions, task completions, delegations, and errors. "
        "Inputs: event_type (string), metadata (dict), severity (optional). "
        "Cost: $0.0001 per log (100K free/month)."
    )

    api_key: Optional[str] = None
    api_base: str = "https://api-production-0c55.up.railway.app"
    crew_id: str = "crewai-crew"
    agent_role: str = "crewai-agent"
    _logger: Optional[Any] = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        crew_id: str = "crewai-crew",
        agent_role: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs
    ):
        """Initialize the observability tool.

        Args:
            api_key: API key (or set AGENT_OBS_API_KEY env var). If not provided,
                     auto-registers on first log (v1.1.0+).
            crew_id: Identifier for the crew
            agent_role: Role of this agent (auto-detected if not provided)
            api_base: Override API URL
        """
        super().__init__(**kwargs)

        self.api_key = api_key or os.getenv("AGENT_OBS_API_KEY")
        self.crew_id = crew_id
        if agent_role:
            self.agent_role = agent_role
        if api_base:
            self.api_base = api_base

        if AgentLogger is None:
            raise ImportError(
                "agent-observability>=1.1.0 package required. "
                "Install: pip install agent-observability>=1.1.0"
            )

        # Initialize logger - will auto-register if no API key provided
        self._logger = AgentLogger(
            api_key=self.api_key,
            base_url=self.api_base,
            default_agent_id=f"{self.crew_id}/{self.agent_role}",
        )

    def _run(
        self,
        event_type: str,
        metadata: Optional[dict] = None,
        severity: str = "info",
        **kwargs
    ) -> str:
        """Log an event.

        Args:
            event_type: Type of event
            metadata: Event metadata
            severity: Log severity

        Returns:
            Success or error message
        """
        if metadata is None:
            metadata = {}

        # Add CrewAI context
        metadata["crew_id"] = self.crew_id
        metadata["agent_role"] = self.agent_role

        try:
            log_id = self._logger.log(
                event_type=event_type,
                severity=severity,
                metadata=metadata
            )

            return f"Event logged (ID: {log_id}, crew: {self.crew_id}, agent: {self.agent_role})"

        except Exception as e:
            return f"Failed to log: {e}"

    def log_task_start(self, task_description: str, expected_output: str = "") -> str:
        """Convenience method to log task start."""
        return self._run(
            event_type="task_started",
            metadata={
                "task_description": task_description[:500],
                "expected_output": expected_output[:200],
            }
        )

    def log_task_complete(
        self,
        task_description: str,
        output: str,
        cost_usd: float = 0,
        duration_ms: int = 0
    ) -> str:
        """Convenience method to log task completion."""
        return self._run(
            event_type="task_complete",
            metadata={
                "task_description": task_description[:500],
                "output_preview": output[:300],
                "cost_usd": cost_usd,
                "duration_ms": duration_ms,
            }
        )

    def log_delegation(
        self,
        from_agent: str,
        to_agent: str,
        task: str,
        reason: str = ""
    ) -> str:
        """Log task delegation between agents."""
        return self._run(
            event_type="delegation",
            metadata={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "task": task[:300],
                "reason": reason[:200],
            }
        )


def create_observability_tool(
    api_key: Optional[str] = None,
    crew_id: str = "crewai-crew",
    agent_role: str = "crewai-agent",
) -> AgentObservabilityTool:
    """Create an observability tool instance.

    Args:
        api_key: API key (or set env var)
        crew_id: Crew identifier
        agent_role: Agent role

    Returns:
        Configured tool
    """
    return AgentObservabilityTool(
        api_key=api_key,
        crew_id=crew_id,
        agent_role=agent_role,
    )

