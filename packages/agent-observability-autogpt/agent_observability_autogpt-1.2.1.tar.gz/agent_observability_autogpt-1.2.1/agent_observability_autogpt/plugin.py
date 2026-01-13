"""AutoGPT plugin for Agent Observability.

This plugin integrates with AutoGPT to automatically log:
- All command executions
- Agent responses
- Custom events via the log_event method

Setup (Auto-Registration - v1.1.0+):
    1. pip install agent-observability-autogpt
    2. Add to AutoGPT plugins
    3. First log auto-registers and displays your API key

Setup (Traditional):
    1. pip install agent-observability-autogpt
    2. export AGENT_OBS_API_KEY=ao_live_...
    3. Add to AutoGPT plugins
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import os
import time

try:
    from agent_observability import AgentLogger
except ImportError:
    AgentLogger = None


class AgentObservabilityPlugin:
    """AutoGPT plugin for logging agent events to Agent Observability platform.

    Features:
        - Automatic logging of all agent commands
        - Response tracking
        - Cost tracking per task
        - Performance metrics
        - Compliance audit trails

    Setup:
        1. Install: pip install agent-observability-autogpt
        2. Get API key:
           curl -X POST https://api-production-0c55.up.railway.app/v1/register \\
             -d '{"agent_id":"my-autogpt"}'
        3. Set AGENT_OBS_API_KEY environment variable
        4. Enable in AutoGPT plugins configuration
    """

    def __init__(self):
        """Initialize the plugin."""
        self.name = "agent-observability"
        self.version = "1.1.0"
        self.description = "Log agent events for observability, cost tracking, and compliance"

        self._logger: Optional[AgentLogger] = None
        self._task_start_time: Optional[float] = None
        self._task_costs: float = 0.0
        self._command_count: int = 0

        # Initialize logger - will auto-register if no API key provided (v1.1.0+)
        if AgentLogger:
            try:
                api_key = os.getenv("AGENT_OBS_API_KEY")
                self._logger = AgentLogger(
                    api_key=api_key,  # None is OK - will auto-register
                    base_url="https://api-production-0c55.up.railway.app",
                    default_agent_id="autogpt",
                    registration_source="agent-observability-autogpt",
                )
            except Exception as e:
                print(f"[Agent Observability] Warning: Failed to initialize logger: {e}")
        else:
            print("[Agent Observability] Warning: agent-observability>=1.1.0 package not installed")

    def can_handle_on_response(self) -> bool:
        """Plugin can handle agent responses."""
        return self._logger is not None

    def on_response(self, response: str, *args, **kwargs) -> str:
        """Log agent responses.

        Args:
            response: The agent's response text

        Returns:
            The response unchanged
        """
        if not self._logger:
            return response

        try:
            self._logger.log(
                event_type="agent_response",
                agent_id="autogpt",
                metadata={
                    "response_length": len(response),
                    "response_preview": response[:200] if len(response) > 200 else response,
                    "command_count": self._command_count,
                },
                severity="info"
            )
        except Exception as e:
            print(f"[Agent Observability] Failed to log response: {e}")

        return response

    def can_handle_on_planning(self) -> bool:
        """Plugin can handle planning phase."""
        return self._logger is not None

    def on_planning(
        self,
        prompt: str,
        messages: list,
        *args,
        **kwargs
    ) -> Optional[str]:
        """Log when agent starts planning.

        Args:
            prompt: The planning prompt
            messages: Message history

        Returns:
            None (don't modify planning)
        """
        if not self._logger:
            return None

        try:
            self._logger.log(
                event_type="state_change",
                agent_id="autogpt",
                metadata={
                    "state": "planning",
                    "prompt_length": len(prompt),
                    "message_count": len(messages),
                },
                severity="debug"
            )
        except Exception as e:
            print(f"[Agent Observability] Failed to log planning: {e}")

        return None

    def can_handle_post_command(self) -> bool:
        """Plugin can handle post-command events."""
        return self._logger is not None

    def post_command(
        self,
        command_name: str,
        arguments: Dict[str, Any],
        *args,
        **kwargs
    ) -> None:
        """Log commands after execution.

        Args:
            command_name: Name of the executed command
            arguments: Command arguments
        """
        if not self._logger:
            return

        self._command_count += 1

        try:
            # Truncate large arguments
            safe_args = {}
            for k, v in arguments.items():
                str_v = str(v)
                safe_args[k] = str_v[:500] if len(str_v) > 500 else str_v

            self._logger.log(
                event_type="command_executed",
                agent_id="autogpt",
                metadata={
                    "command": command_name,
                    "arguments": safe_args,
                    "command_number": self._command_count,
                },
                severity="info"
            )
        except Exception as e:
            print(f"[Agent Observability] Failed to log command: {e}")

    def can_handle_pre_command(self) -> bool:
        """Plugin can handle pre-command events."""
        return self._logger is not None

    def pre_command(
        self,
        command_name: str,
        arguments: Dict[str, Any],
        *args,
        **kwargs
    ) -> tuple:
        """Track command start time.

        Args:
            command_name: Name of the command to execute
            arguments: Command arguments

        Returns:
            Unchanged command and arguments
        """
        # Track timing for latency measurement
        self._current_command_start = time.time()
        return command_name, arguments

    def can_handle_on_instruction(self) -> bool:
        """Plugin can handle task instructions."""
        return self._logger is not None

    def on_instruction(self, instruction: str, *args, **kwargs) -> str:
        """Log new task instructions.

        Args:
            instruction: The task instruction

        Returns:
            The instruction unchanged
        """
        if not self._logger:
            return instruction

        # Reset task metrics
        self._task_start_time = time.time()
        self._task_costs = 0.0
        self._command_count = 0

        try:
            self._logger.log(
                event_type="state_change",
                agent_id="autogpt",
                metadata={
                    "state": "task_started",
                    "instruction_preview": instruction[:200],
                },
                severity="info"
            )
        except Exception as e:
            print(f"[Agent Observability] Failed to log instruction: {e}")

        return instruction

    def log_event(
        self,
        event_type: str,
        metadata: Dict[str, Any],
        severity: str = "info"
    ) -> str:
        """Log a custom event to Agent Observability.

        This method can be called by AutoGPT agents to log custom events.

        Args:
            event_type: Type of event (api_call, decision, transaction, error)
            metadata: Event metadata dict
            severity: Log severity (debug, info, warning, error, critical)

        Returns:
            Success or error message
        """
        if not self._logger:
            return "Agent Observability not configured (missing API key or package)"

        try:
            # Track costs if provided
            if "cost_usd" in metadata:
                self._task_costs += float(metadata["cost_usd"])

            log_id = self._logger.log(
                event_type=event_type,
                agent_id="autogpt",
                metadata=metadata,
                severity=severity
            )

            return f"Logged {event_type} event (ID: {log_id})"

        except Exception as e:
            return f"Failed to log event: {e}"

    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of current task.

        Returns:
            Dict with task metrics
        """
        elapsed = time.time() - self._task_start_time if self._task_start_time else 0

        return {
            "elapsed_seconds": round(elapsed, 2),
            "total_cost_usd": round(self._task_costs, 4),
            "commands_executed": self._command_count,
        }


def init_plugin() -> AgentObservabilityPlugin:
    """Initialize and return the plugin instance.

    This function is called by AutoGPT's plugin loader.

    Returns:
        Configured plugin instance
    """
    return AgentObservabilityPlugin()

