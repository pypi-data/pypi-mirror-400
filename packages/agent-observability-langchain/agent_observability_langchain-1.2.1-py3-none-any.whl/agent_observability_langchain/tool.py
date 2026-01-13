"""LangChain tool for Agent Observability platform."""

from __future__ import annotations

from typing import Optional, Type, Any
import os

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

try:
    from agent_observability import AgentLogger
except ImportError:
    AgentLogger = None


class LogEventInput(BaseModel):
    """Input schema for logging agent events."""

    event_type: str = Field(
        description="Type of event: 'api_call', 'decision', 'transaction', 'error', 'state_change'"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Event metadata (provider, cost_usd, latency_ms, model, tokens, etc.)"
    )
    severity: str = Field(
        default="info",
        description="Event severity: 'debug', 'info', 'warning', 'error', 'critical'"
    )


class AgentObservabilityTool(BaseTool):
    """Tool for logging agent events to Agent Observability platform.

    This tool provides structured logging, cost tracking, and compliance audit trails
    for AI agents. Perfect for production agents that need to maintain logs for
    debugging, cost analysis, or regulatory compliance (SOC 2, GDPR, financial regs).

    Features:
        - Structured event logging with metadata
        - Automatic cost tracking per API call
        - Performance analytics (latency, error rates)
        - Compliance-ready audit trails
        - Queryable historical logs

    Pricing:
        - Free: 100,000 logs/month
        - Paid: $0.0001 per log entry ($10 per 100K logs)
        - See: https://api-production-0c55.up.railway.app/pricing.json

    Setup (Auto-Registration - NEW in v1.1.0):
        No API key needed! Auto-registers on first use:

        ```python
        from langchain.agents import initialize_agent
        from agent_observability_langchain import AgentObservabilityTool

        tools = [AgentObservabilityTool(), ...other_tools...]
        agent = initialize_agent(tools, llm)
        # First log auto-registers and shows:
        # ✅ Agent Observability - Auto-registered!
        # 📋 Your API key: ao_live_abc123...
        ```

    Setup (Traditional - Optional):
        If you prefer to set an API key explicitly:
        ```bash
        export AGENT_OBS_API_KEY=ao_live_...
        ```

    Example:
        ```python
        from langchain.agents import initialize_agent, AgentType
        from langchain.llms import OpenAI
        from agent_observability_langchain import AgentObservabilityTool

        # Initialize
        obs_tool = AgentObservabilityTool()
        llm = OpenAI()

        # Create agent with observability
        agent = initialize_agent(
            tools=[obs_tool],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

        # Logs are tracked when agent uses the tool
        result = agent.run(
            "Log an API call to OpenAI with cost $0.05 and latency 1200ms"
        )
        ```
    """

    name: str = "agent_observability"
    description: str = (
        "Log agent events for observability, cost tracking, and compliance. "
        "Use this to track API calls, decisions, transactions, errors, and state changes. "
        "Required inputs: event_type (string), metadata (dict with provider, cost_usd, latency_ms, etc.). "
        "Optional: severity (default 'info'). "
        "Cost: $0.0001 per log (100K free/month). "
        "Essential for production agents needing audit trails or cost analysis."
    )
    args_schema: Type[BaseModel] = LogEventInput

    api_key: Optional[str] = None
    api_base: str = "https://api-production-0c55.up.railway.app"
    agent_id: str = "langchain-agent"
    _logger: Optional[Any] = None

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        agent_id: str = "langchain-agent",
        **kwargs
    ):
        """Initialize with optional API key.

        Args:
            api_key: API key for authentication. If not provided:
                     1. Reads from AGENT_OBS_API_KEY environment variable
                     2. Auto-registers on first log if not found (v1.1.0+)
            api_base: Base URL for the API. Defaults to production.
            agent_id: Default agent identifier for logs.
        """
        super().__init__(**kwargs)

        self.api_key = api_key or os.getenv("AGENT_OBS_API_KEY")
        if api_base:
            self.api_base = api_base
        self.agent_id = agent_id

        if AgentLogger is None:
            raise ImportError(
                "agent-observability>=1.1.0 package required. "
                "Install: pip install agent-observability>=1.1.0"
            )

        # Initialize the logger - will auto-register if no API key provided
        self._logger = AgentLogger(
            api_key=self.api_key,
            base_url=self.api_base,
            default_agent_id=self.agent_id,
            registration_source="agent-observability-langchain",
        )

    def _run(
        self,
        event_type: str,
        metadata: Optional[dict] = None,
        severity: str = "info",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Log an event synchronously.

        Args:
            event_type: Type of event (any string, e.g., api_call, decision, test, custom_event)
            metadata: Event metadata dict
            severity: Log severity level
            run_manager: LangChain callback manager

        Returns:
            Success or error message
        """
        if metadata is None:
            metadata = {}

        try:
            # Add LangChain context if available
            if run_manager and hasattr(run_manager, "run_id"):
                metadata["langchain_run_id"] = str(run_manager.run_id)

            log_id = self._logger.log(
                event_type=event_type,
                severity=severity,
                agent_id=self.agent_id,
                metadata=metadata
            )

            if log_id:
                return f"Event logged successfully (ID: {log_id}, type: {event_type}, severity: {severity})"
            else:
                return f"Event logged (async mode, type: {event_type})"

        except Exception as e:
            error_msg = f"Failed to log event: {str(e)}"
            if run_manager:
                try:
                    run_manager.on_tool_error(error_msg)
                except Exception:
                    pass  # Ignore callback errors
            return error_msg

    async def _arun(
        self,
        event_type: str,
        metadata: Optional[dict] = None,
        severity: str = "info",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Log an event asynchronously.

        Falls back to synchronous for now. Can be upgraded to full async
        if needed for high-throughput scenarios.
        """
        return self._run(event_type, metadata, severity, run_manager)


def create_observability_tool(
    api_key: Optional[str] = None,
    agent_id: str = "langchain-agent",
    api_base: Optional[str] = None,
) -> AgentObservabilityTool:
    """Create an Agent Observability tool instance.

    Convenience function for quick tool creation.

    Args:
        api_key: API key (or set AGENT_OBS_API_KEY env var)
        agent_id: Identifier for this agent
        api_base: Override API base URL

    Returns:
        Configured AgentObservabilityTool instance

    Example:
        ```python
        from agent_observability_langchain import create_observability_tool

        tool = create_observability_tool(agent_id="my-research-agent")
        result = tool.invoke({
            "event_type": "api_call",
            "metadata": {"provider": "openai", "cost_usd": 0.002}
        })
        ```
    """
    return AgentObservabilityTool(
        api_key=api_key,
        agent_id=agent_id,
        api_base=api_base,
    )

