"""CrewAI callback handler for automatic observability."""

from __future__ import annotations

from typing import Any, Dict, Optional
import os
import time

try:
    from agent_observability import AgentLogger
except ImportError:
    AgentLogger = None


class ObservabilityCallback:
    """Callback handler for automatic CrewAI observability.

    Automatically logs:
        - Task starts and completions
        - Agent actions
        - Tool usage
        - Errors

    Usage:
        ```python
        from crewai import Crew
        from agent_observability_crewai import ObservabilityCallback

        callback = ObservabilityCallback(crew_id="my-crew")

        crew = Crew(
            agents=[...],
            tasks=[...],
            callbacks=[callback]
        )
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        crew_id: str = "crewai-crew",
        api_base: str = "https://api-production-0c55.up.railway.app",
    ):
        """Initialize callback handler.

        Args:
            api_key: API key (or set AGENT_OBS_API_KEY)
            crew_id: Identifier for the crew
            api_base: API base URL
        """
        self.crew_id = crew_id
        self.api_base = api_base
        self._task_start_times: Dict[str, float] = {}
        self._logger: Optional[AgentLogger] = None

        api_key = api_key or os.getenv("AGENT_OBS_API_KEY")

        if api_key and AgentLogger:
            self._logger = AgentLogger(
                api_key=api_key,
                base_url=api_base,
                default_agent_id=crew_id,
                registration_source="agent-observability-crewai",
            )

    def on_task_start(self, task: Any) -> None:
        """Called when a task starts."""
        if not self._logger:
            return

        task_id = str(id(task))
        self._task_start_times[task_id] = time.time()

        try:
            self._logger.log(
                event_type="task_started",
                metadata={
                    "crew_id": self.crew_id,
                    "task_description": str(task.description)[:500] if hasattr(task, "description") else "",
                    "agent": str(task.agent.role) if hasattr(task, "agent") and task.agent else "unknown",
                }
            )
        except Exception as e:
            print(f"[Agent Observability] Failed to log task start: {e}")

    def on_task_end(self, task: Any, output: Any) -> None:
        """Called when a task completes."""
        if not self._logger:
            return

        task_id = str(id(task))
        start_time = self._task_start_times.pop(task_id, None)
        duration_ms = int((time.time() - start_time) * 1000) if start_time else 0

        try:
            self._logger.log(
                event_type="task_complete",
                metadata={
                    "crew_id": self.crew_id,
                    "task_description": str(task.description)[:500] if hasattr(task, "description") else "",
                    "agent": str(task.agent.role) if hasattr(task, "agent") and task.agent else "unknown",
                    "output_preview": str(output)[:300],
                    "duration_ms": duration_ms,
                }
            )
        except Exception as e:
            print(f"[Agent Observability] Failed to log task end: {e}")

    def on_tool_use(self, agent: Any, tool: str, input_data: Any) -> None:
        """Called when an agent uses a tool."""
        if not self._logger:
            return

        try:
            self._logger.log(
                event_type="tool_use",
                metadata={
                    "crew_id": self.crew_id,
                    "agent": str(agent.role) if hasattr(agent, "role") else "unknown",
                    "tool": tool,
                    "input_preview": str(input_data)[:200],
                }
            )
        except Exception as e:
            print(f"[Agent Observability] Failed to log tool use: {e}")

    def on_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Called when an error occurs."""
        if not self._logger:
            return

        try:
            self._logger.log(
                event_type="error",
                severity="error",
                metadata={
                    "crew_id": self.crew_id,
                    "error_type": type(error).__name__,
                    "error_message": str(error)[:500],
                    "context": context or {},
                }
            )
        except Exception as e:
            print(f"[Agent Observability] Failed to log error: {e}")

