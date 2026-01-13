"""Agent Observability integration for LangChain."""

__version__ = "1.1.0"

from .tool import AgentObservabilityTool, create_observability_tool, LogEventInput

__all__ = ["AgentObservabilityTool", "create_observability_tool", "LogEventInput"]

