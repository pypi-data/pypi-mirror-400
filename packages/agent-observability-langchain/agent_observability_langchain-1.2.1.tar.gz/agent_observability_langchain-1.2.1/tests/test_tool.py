"""Tests for AgentObservabilityTool."""

import os
import pytest
from unittest.mock import patch, MagicMock


# Set test API key before imports
os.environ["AGENT_OBS_API_KEY"] = "ao_test_key_for_testing"


class TestAgentObservabilityToolImports:
    """Test that imports work correctly."""

    def test_import_tool(self):
        """Test importing AgentObservabilityTool."""
        from agent_observability_langchain import AgentObservabilityTool

        assert AgentObservabilityTool is not None

    def test_import_convenience_function(self):
        """Test importing create_observability_tool."""
        from agent_observability_langchain import create_observability_tool

        assert create_observability_tool is not None

    def test_import_input_schema(self):
        """Test importing LogEventInput."""
        from agent_observability_langchain import LogEventInput

        assert LogEventInput is not None

    def test_version_exists(self):
        """Test that __version__ is defined."""
        import agent_observability_langchain

        assert hasattr(agent_observability_langchain, "__version__")
        assert agent_observability_langchain.__version__ == "1.1.0"


class TestLogEventInput:
    """Test the input schema."""

    def test_valid_input(self):
        """Test valid input creates correctly."""
        from agent_observability_langchain import LogEventInput

        input_data = LogEventInput(
            event_type="api_call",
            metadata={"provider": "openai", "cost_usd": 0.01},
            severity="info",
        )
        assert input_data.event_type == "api_call"
        assert input_data.metadata["provider"] == "openai"
        assert input_data.severity == "info"

    def test_default_severity(self):
        """Test default severity is 'info'."""
        from agent_observability_langchain import LogEventInput

        input_data = LogEventInput(event_type="decision", metadata={})
        assert input_data.severity == "info"

    def test_default_metadata(self):
        """Test default metadata is empty dict."""
        from agent_observability_langchain import LogEventInput

        input_data = LogEventInput(event_type="error")
        assert input_data.metadata == {}


class TestAgentObservabilityTool:
    """Test the main tool class."""

    def test_tool_metadata(self):
        """Test tool has correct LangChain metadata."""
        from agent_observability_langchain import AgentObservabilityTool

        with patch("agent_observability_langchain.tool.AgentLogger"):
            tool = AgentObservabilityTool()

            assert tool.name == "agent_observability"
            assert "cost tracking" in tool.description.lower()
            assert "compliance" in tool.description.lower()
            assert "log" in tool.description.lower()

    def test_custom_agent_id(self):
        """Test custom agent_id is set."""
        from agent_observability_langchain import AgentObservabilityTool

        with patch("agent_observability_langchain.tool.AgentLogger"):
            tool = AgentObservabilityTool(agent_id="my-custom-agent")
            assert tool.agent_id == "my-custom-agent"

    def test_custom_api_base(self):
        """Test custom api_base is set."""
        from agent_observability_langchain import AgentObservabilityTool

        with patch("agent_observability_langchain.tool.AgentLogger"):
            tool = AgentObservabilityTool(api_base="https://custom.api.com")
            assert tool.api_base == "https://custom.api.com"

    def test_missing_api_key_uses_auto_registration(self):
        """Test that missing API key triggers auto-registration (no error)."""
        from agent_observability_langchain import AgentObservabilityTool

        # Temporarily remove the env var
        old_key = os.environ.pop("AGENT_OBS_API_KEY", None)

        try:
            # With auto-registration, tool creation should succeed without an API key
            tool = AgentObservabilityTool()
            assert tool is not None
            # The logger should be created (will auto-register on first log)
            assert hasattr(tool, "_logger")
        finally:
            if old_key:
                os.environ["AGENT_OBS_API_KEY"] = old_key

    def test_run_calls_logger(self):
        """Test that _run calls the logger correctly."""
        from agent_observability_langchain import AgentObservabilityTool

        with patch("agent_observability_langchain.tool.AgentLogger") as MockLogger:
            mock_logger = MagicMock()
            mock_logger.log.return_value = "test-log-id-123"
            MockLogger.return_value = mock_logger

            tool = AgentObservabilityTool()
            result = tool._run(
                event_type="api_call",
                metadata={"provider": "openai", "cost_usd": 0.01},
                severity="info",
            )

            # Verify logger was called
            mock_logger.log.assert_called_once()
            call_kwargs = mock_logger.log.call_args[1]
            assert call_kwargs["event_type"] == "api_call"
            assert call_kwargs["severity"] == "info"
            assert call_kwargs["metadata"]["provider"] == "openai"

            # Verify success message
            assert "test-log-id-123" in result or "logged" in result.lower()

    def test_run_with_none_metadata(self):
        """Test _run handles None metadata."""
        from agent_observability_langchain import AgentObservabilityTool

        with patch("agent_observability_langchain.tool.AgentLogger") as MockLogger:
            mock_logger = MagicMock()
            mock_logger.log.return_value = "log-id"
            MockLogger.return_value = mock_logger

            tool = AgentObservabilityTool()
            result = tool._run(event_type="state_change", metadata=None)

            # Should not raise, should use empty dict
            assert "log-id" in result or "logged" in result.lower()

    def test_run_handles_exception(self):
        """Test _run handles logger exceptions gracefully."""
        from agent_observability_langchain import AgentObservabilityTool

        with patch("agent_observability_langchain.tool.AgentLogger") as MockLogger:
            mock_logger = MagicMock()
            mock_logger.log.side_effect = Exception("Network error")
            MockLogger.return_value = mock_logger

            tool = AgentObservabilityTool()
            result = tool._run(event_type="error", metadata={})

            # Should return error message, not raise
            assert "Failed" in result or "error" in result.lower()

    def test_arun_calls_run(self):
        """Test _arun delegates to _run."""
        from agent_observability_langchain import AgentObservabilityTool
        import asyncio

        with patch("agent_observability_langchain.tool.AgentLogger") as MockLogger:
            mock_logger = MagicMock()
            mock_logger.log.return_value = "async-log-id"
            MockLogger.return_value = mock_logger

            tool = AgentObservabilityTool()

            # Run async method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    tool._arun(event_type="api_call", metadata={"test": True})
                )
            finally:
                loop.close()

            assert "async-log-id" in result or "logged" in result.lower()


class TestCreateObservabilityTool:
    """Test the convenience function."""

    def test_creates_tool(self):
        """Test create_observability_tool returns a tool."""
        from agent_observability_langchain import create_observability_tool

        with patch("agent_observability_langchain.tool.AgentLogger"):
            tool = create_observability_tool()
            assert tool is not None
            assert tool.name == "agent_observability"

    def test_passes_agent_id(self):
        """Test agent_id is passed correctly."""
        from agent_observability_langchain import create_observability_tool

        with patch("agent_observability_langchain.tool.AgentLogger"):
            tool = create_observability_tool(agent_id="custom-agent")
            assert tool.agent_id == "custom-agent"

    def test_passes_api_key(self):
        """Test api_key is passed correctly."""
        from agent_observability_langchain import create_observability_tool

        with patch("agent_observability_langchain.tool.AgentLogger"):
            tool = create_observability_tool(api_key="ao_custom_key")
            assert tool.api_key == "ao_custom_key"


class TestIntegration:
    """Integration tests (require real API key)."""

    @pytest.mark.skipif(
        os.getenv("AGENT_OBS_API_KEY", "").startswith("ao_test"),
        reason="Skipping integration test with test key",
    )
    def test_real_api_call(self):
        """Test real API call (skipped unless real key is set)."""
        from agent_observability_langchain import AgentObservabilityTool

        tool = AgentObservabilityTool(agent_id="pytest-integration")
        result = tool._run(
            event_type="test_event",
            metadata={"test": True, "source": "pytest"},
            severity="debug",
        )

        # Should succeed with real API
        assert "logged" in result.lower() or "ID" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

