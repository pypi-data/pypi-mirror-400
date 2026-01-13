"""Comprehensive tests for the Agent class."""

import pytest

from indusagi import Agent, AgentConfig


class TestAgentConfig:
    """Test suite for AgentConfig."""

    def test_agent_config_defaults(self):
        """Test that AgentConfig has correct default values."""
        config = AgentConfig()

        assert config.name == "Agent"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.system_prompt is None

    def test_agent_config_custom_values(self):
        """Test that AgentConfig accepts custom values."""
        config = AgentConfig(
            name="CustomAgent",
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=2000,
            system_prompt="Custom system prompt",
        )

        assert config.name == "CustomAgent"
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
        assert config.system_prompt == "Custom system prompt"

    def test_agent_config_temperature_validation(self):
        """Test that temperature is validated to be between 0 and 2."""
        # Valid temperatures
        config1 = AgentConfig(temperature=0.0)
        assert config1.temperature == 0.0

        config2 = AgentConfig(temperature=2.0)
        assert config2.temperature == 2.0

        # Invalid temperatures should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(temperature=-0.1)

        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(temperature=2.1)

    def test_agent_config_dict_conversion(self):
        """Test that AgentConfig can be converted to and from dict."""
        config = AgentConfig(
            name="TestAgent",
            model="gpt-4",
            temperature=0.8,
        )

        config_dict = config.model_dump()
        assert config_dict["name"] == "TestAgent"
        assert config_dict["model"] == "gpt-4"
        assert config_dict["temperature"] == 0.8


class TestBaseAgent:
    """Test suite for BaseAgent abstract class."""

    def test_base_agent_is_abstract(self):
        """Test that BaseAgent cannot be instantiated directly."""
        config = AgentConfig()

        with pytest.raises(TypeError):
            BaseAgent(config)

    @pytest.mark.asyncio
    async def test_concrete_agent_initialization(self, agent_config):
        """Test that a concrete agent initializes correctly."""
        agent = Agent(agent_config)

        assert agent.config == agent_config
        assert agent.history == []
        assert agent.tools == []

    @pytest.mark.asyncio
    async def test_agent_reset(self, agent_config):
        """Test that agent.reset() clears history."""
        agent = Agent(agent_config)

        # Add some history
        agent.history.append({"role": "user", "content": "Hello"})
        agent.history.append({"role": "assistant", "content": "Hi"})

        assert len(agent.history) == 2

        # Reset
        agent.reset()

        assert len(agent.history) == 0

    @pytest.mark.asyncio
    async def test_agent_get_history(self, agent_config):
        """Test that get_history returns a copy of history."""
        agent = Agent(agent_config)

        # Add history
        agent.history.append({"role": "user", "content": "Test"})

        # Get history
        history = agent.get_history()

        assert len(history) == 1
        assert history[0]["content"] == "Test"

        # Modify the returned history
        history.append({"role": "assistant", "content": "Response"})

        # Original should be unchanged
        assert len(agent.history) == 1

    @pytest.mark.asyncio
    async def test_agent_get_history_empty(self, agent_config):
        """Test get_history with no history."""
        agent = Agent(agent_config)

        history = agent.get_history()

        assert history == []
        assert isinstance(history, list)


class TestAgent:
    """Test suite for the Agent implementation."""

    @pytest.mark.asyncio
    async def test_agent_initialization_with_defaults(self):
        """Test agent initialization with default config."""
        agent = Agent()

        assert agent.config.name == "Agent"
        assert agent.config.model == "gpt-4"
        assert agent.tools == []
        assert agent.history == []

    @pytest.mark.asyncio
    async def test_agent_initialization_with_config(self, agent_config):
        """Test agent initialization with custom config."""
        agent = Agent(agent_config)

        assert agent.config == agent_config
        assert agent.config.name == "TestAgent"
        assert agent.tools == []

    @pytest.mark.asyncio
    async def test_agent_initialization_with_tools(self, agent_config, calculator_tool):
        """Test agent initialization with tools."""
        agent = Agent(agent_config, tools=[calculator_tool])

        assert len(agent.tools) == 1
        assert agent.tools[0] == calculator_tool

    @pytest.mark.asyncio
    async def test_agent_run_basic(self, agent_config):
        """Test basic agent.run() functionality."""
        agent = Agent(agent_config)

        response = await agent.run("Hello, agent!")

        assert isinstance(response, str)
        assert "Hello, agent!" in response
        assert len(agent.history) == 2  # User message and assistant response

    @pytest.mark.asyncio
    async def test_agent_run_updates_history(self, agent_config):
        """Test that agent.run() updates history correctly."""
        agent = Agent(agent_config)

        await agent.run("First message")

        assert len(agent.history) == 2
        assert agent.history[0]["role"] == "user"
        assert agent.history[0]["content"] == "First message"
        assert agent.history[1]["role"] == "assistant"

        await agent.run("Second message")

        assert len(agent.history) == 4

    @pytest.mark.asyncio
    async def test_agent_run_with_kwargs(self, agent_config):
        """Test agent.run() with additional kwargs."""
        agent = Agent(agent_config)

        response = await agent.run(
            "Test prompt",
            temperature=0.5,
            max_tokens=100,
        )

        assert isinstance(response, str)

    @pytest.mark.asyncio
    async def test_agent_step_basic(self, agent_config):
        """Test basic agent.step() functionality."""
        agent = Agent(agent_config)

        result = await agent.step(action="test_action")

        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "message" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_agent_step_with_kwargs(self, agent_config):
        """Test agent.step() with various kwargs."""
        agent = Agent(agent_config)

        result = await agent.step(
            action="complex_action",
            param1="value1",
            param2=42,
        )

        assert result["status"] == "success"
        assert result["data"]["action"] == "complex_action"
        assert result["data"]["param1"] == "value1"
        assert result["data"]["param2"] == 42

    @pytest.mark.asyncio
    async def test_agent_add_tool(self, agent_config, calculator_tool):
        """Test adding a tool to the agent."""
        agent = Agent(agent_config)

        assert len(agent.tools) == 0

        agent.add_tool(calculator_tool)

        assert len(agent.tools) == 1
        assert agent.tools[0] == calculator_tool

    @pytest.mark.asyncio
    async def test_agent_add_multiple_tools(self, agent_config, calculator_tool, weather_tool):
        """Test adding multiple tools to the agent."""
        agent = Agent(agent_config)

        agent.add_tool(calculator_tool)
        agent.add_tool(weather_tool)

        assert len(agent.tools) == 2
        assert calculator_tool in agent.tools
        assert weather_tool in agent.tools

    @pytest.mark.asyncio
    async def test_agent_remove_tool(self, agent_config, calculator_tool):
        """Test removing a tool from the agent."""
        agent = Agent(agent_config, tools=[calculator_tool])

        assert len(agent.tools) == 1

        agent.remove_tool(calculator_tool)

        assert len(agent.tools) == 0

    @pytest.mark.asyncio
    async def test_agent_remove_nonexistent_tool(self, agent_config, calculator_tool):
        """Test removing a tool that doesn't exist (should not raise error)."""
        agent = Agent(agent_config)

        # Should not raise an error
        agent.remove_tool(calculator_tool)

        assert len(agent.tools) == 0

    @pytest.mark.asyncio
    async def test_agent_remove_tool_from_multiple(
        self, agent_config, calculator_tool, weather_tool
    ):
        """Test removing a specific tool when multiple tools exist."""
        agent = Agent(agent_config, tools=[calculator_tool, weather_tool])

        assert len(agent.tools) == 2

        agent.remove_tool(calculator_tool)

        assert len(agent.tools) == 1
        assert weather_tool in agent.tools
        assert calculator_tool not in agent.tools


class TestAgentEdgeCases:
    """Test suite for agent edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_agent_empty_prompt(self, agent_config):
        """Test agent with empty prompt."""
        agent = Agent(agent_config)

        response = await agent.run("")

        assert isinstance(response, str)
        assert len(agent.history) == 2

    @pytest.mark.asyncio
    async def test_agent_very_long_prompt(self, agent_config):
        """Test agent with very long prompt."""
        agent = Agent(agent_config)

        long_prompt = "Test " * 1000  # Very long prompt

        response = await agent.run(long_prompt)

        assert isinstance(response, str)
        assert long_prompt in agent.history[0]["content"]

    @pytest.mark.asyncio
    async def test_agent_special_characters_prompt(self, agent_config):
        """Test agent with special characters in prompt."""
        agent = Agent(agent_config)

        special_prompt = "Test with \n\t special chars: @#$%^&*()"

        response = await agent.run(special_prompt)

        assert isinstance(response, str)
        assert special_prompt in agent.history[0]["content"]

    @pytest.mark.asyncio
    async def test_agent_unicode_prompt(self, agent_config):
        """Test agent with unicode characters."""
        agent = Agent(agent_config)

        unicode_prompt = "Hello in Chinese: 你好, Japanese: こんにちは, Emoji: 😀"

        response = await agent.run(unicode_prompt)

        assert isinstance(response, str)
        assert unicode_prompt in agent.history[0]["content"]

    @pytest.mark.asyncio
    async def test_agent_multiple_resets(self, agent_config):
        """Test multiple consecutive resets."""
        agent = Agent(agent_config)

        await agent.run("Test")
        agent.reset()
        agent.reset()
        agent.reset()

        assert len(agent.history) == 0

    @pytest.mark.asyncio
    async def test_agent_run_after_reset(self, agent_config):
        """Test that agent can run normally after reset."""
        agent = Agent(agent_config)

        await agent.run("First message")
        agent.reset()
        await agent.run("Second message")

        assert len(agent.history) == 2  # Only second conversation


class TestAgentIntegration:
    """Integration tests for Agent with tools."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_with_calculator_tool(self, agent_config, calculator_tool):
        """Test agent with calculator tool integration."""
        agent = Agent(agent_config, tools=[calculator_tool])

        assert len(agent.tools) == 1

        # Execute calculator tool
        result = await calculator_tool.execute(operation="add", x=5, y=3)

        assert result.success
        assert result.result == 8

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_with_multiple_tools(
        self, agent_config, calculator_tool, weather_tool
    ):
        """Test agent with multiple tools."""
        agent = Agent(agent_config, tools=[calculator_tool, weather_tool])

        assert len(agent.tools) == 2

        # Test calculator
        calc_result = await calculator_tool.execute(operation="multiply", x=4, y=5)
        assert calc_result.success
        assert calc_result.result == 20

        # Test weather
        weather_result = await weather_tool.execute(location="New York")
        assert weather_result.success
        assert weather_result.result["location"] == "New York"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_tool_lifecycle(
        self, agent_config, calculator_tool, weather_tool
    ):
        """Test complete tool lifecycle: add, use, remove."""
        agent = Agent(agent_config)

        # Add tools
        agent.add_tool(calculator_tool)
        agent.add_tool(weather_tool)
        assert len(agent.tools) == 2

        # Use tools
        await agent.run("Calculate 5 + 3")

        # Remove tool
        agent.remove_tool(calculator_tool)
        assert len(agent.tools) == 1

        # Continue using remaining tools
        await agent.run("What's the weather?")

        assert len(agent.history) == 4  # 2 conversations
