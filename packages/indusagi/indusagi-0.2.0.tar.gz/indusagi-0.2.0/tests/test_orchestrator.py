"""Comprehensive tests for the Orchestrator system."""

import pytest

from indusagi import Agent


class TestOrchestrator:
    """Test suite for the Orchestrator."""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator.agent is not None
        assert orchestrator.tool_registry is not None
        assert orchestrator.memory_system is not None
        assert orchestrator.is_running is False

    @pytest.mark.asyncio
    async def test_orchestrator_has_components(self, orchestrator):
        """Test orchestrator has all required components."""
        assert hasattr(orchestrator, "agent")
        assert hasattr(orchestrator, "tool_registry")
        assert hasattr(orchestrator, "memory_system")
        assert hasattr(orchestrator, "execute")
        assert hasattr(orchestrator, "execute_with_tools")

    @pytest.mark.asyncio
    async def test_orchestrator_execute_basic(self, orchestrator):
        """Test basic orchestrator execution."""
        result = await orchestrator.execute("Hello, orchestrator!")

        assert result["success"] is True
        assert "response" in result
        assert isinstance(result["response"], str)

    @pytest.mark.asyncio
    async def test_orchestrator_updates_memory(self, orchestrator):
        """Test orchestrator updates memory during execution."""
        initial_count = orchestrator.memory_system.count()

        await orchestrator.execute("Test message")

        # Should add user message and assistant response
        assert orchestrator.memory_system.count() == initial_count + 2

    @pytest.mark.asyncio
    async def test_orchestrator_multiple_executions(self, orchestrator):
        """Test orchestrator handles multiple executions."""
        result1 = await orchestrator.execute("First message")
        assert result1["success"] is True

        result2 = await orchestrator.execute("Second message")
        assert result2["success"] is True

        # Memory should have 4 entries (2 conversations)
        assert orchestrator.memory_system.count() >= 4

    @pytest.mark.asyncio
    async def test_orchestrator_is_running_flag(self, orchestrator):
        """Test orchestrator sets is_running flag correctly."""
        assert orchestrator.is_running is False

        # Start execution (in background we can't test mid-execution easily)
        result = await orchestrator.execute("Test")

        # After completion, should be False again
        assert orchestrator.is_running is False

    @pytest.mark.asyncio
    async def test_orchestrator_with_tools(self, orchestrator):
        """Test orchestrator with tool calling."""
        result = await orchestrator.execute_with_tools("Calculate 5 + 3")

        assert result["success"] is True
        assert "response" in result
        assert "tool_calls" in result

    @pytest.mark.asyncio
    async def test_orchestrator_tool_calls_empty(self, orchestrator):
        """Test orchestrator tool_calls is list."""
        result = await orchestrator.execute_with_tools("Just a message")

        assert isinstance(result["tool_calls"], list)

    @pytest.mark.asyncio
    async def test_orchestrator_memory_persistence(self, orchestrator):
        """Test that orchestrator maintains memory across executions."""
        await orchestrator.execute("Remember this: blue")
        await orchestrator.execute("What should I remember?")

        memories = orchestrator.memory_system.get_recent(10)

        # Should have both conversations
        assert len(memories) >= 4

        # Check that first message is in memory
        contents = [m["content"] for m in memories]
        assert any("blue" in str(c) for c in contents)


class TestOrchestratorWithAgent:
    """Test suite for orchestrator with agent integration."""

    @pytest.mark.asyncio
    async def test_orchestrator_uses_agent(self, orchestrator):
        """Test orchestrator delegates to agent."""
        result = await orchestrator.execute("Test prompt")

        assert result["success"] is True

        # Agent should have history
        assert len(orchestrator.agent.history) > 0

    @pytest.mark.asyncio
    async def test_orchestrator_agent_history(self, orchestrator):
        """Test orchestrator and agent history stay in sync."""
        await orchestrator.execute("Message 1")
        await orchestrator.execute("Message 2")

        # Agent should have history
        agent_history = orchestrator.agent.get_history()
        assert len(agent_history) >= 4

    @pytest.mark.asyncio
    async def test_orchestrator_respects_agent_config(self, agent_config):
        """Test orchestrator respects agent configuration."""
        from tests.conftest import MockOrchestrator, MockToolRegistry, MockMemorySystem

        agent = Agent(agent_config)
        orch = MockOrchestrator(
            agent=agent,
            tool_registry=MockToolRegistry(),
            memory_system=MockMemorySystem(),
        )

        assert orch.agent.config.name == agent_config.name
        assert orch.agent.config.model == agent_config.model


class TestOrchestratorWithToolRegistry:
    """Test suite for orchestrator with tool registry."""

    @pytest.mark.asyncio
    async def test_orchestrator_has_tool_registry(self, orchestrator):
        """Test orchestrator has access to tool registry."""
        tools = orchestrator.tool_registry.list_tools()

        assert len(tools) >= 2  # calculator and weather from fixture

    @pytest.mark.asyncio
    async def test_orchestrator_can_access_tools(self, orchestrator):
        """Test orchestrator can access registered tools."""
        calculator = orchestrator.tool_registry.get_tool("calculator")
        weather = orchestrator.tool_registry.get_tool("weather")

        assert calculator is not None
        assert weather is not None

    @pytest.mark.asyncio
    async def test_orchestrator_tool_registry_modifications(
        self, orchestrator, failing_tool
    ):
        """Test orchestrator reflects tool registry changes."""
        initial_count = len(orchestrator.tool_registry.list_tools())

        # Add a tool
        orchestrator.tool_registry.register(failing_tool)

        assert len(orchestrator.tool_registry.list_tools()) == initial_count + 1

        # Remove a tool
        orchestrator.tool_registry.unregister("failing_tool")

        assert len(orchestrator.tool_registry.list_tools()) == initial_count


class TestOrchestratorWithMemory:
    """Test suite for orchestrator with memory system."""

    @pytest.mark.asyncio
    async def test_orchestrator_memory_starts_empty(self, orchestrator):
        """Test orchestrator memory can start empty."""
        # Reset memory
        orchestrator.memory_system.clear()

        assert orchestrator.memory_system.count() == 0

    @pytest.mark.asyncio
    async def test_orchestrator_adds_to_memory(self, orchestrator):
        """Test orchestrator adds interactions to memory."""
        orchestrator.memory_system.clear()

        await orchestrator.execute("Test message")

        assert orchestrator.memory_system.count() >= 2

    @pytest.mark.asyncio
    async def test_orchestrator_memory_retrieval(self, orchestrator):
        """Test orchestrator can retrieve from memory."""
        orchestrator.memory_system.clear()

        await orchestrator.execute("Hello")
        await orchestrator.execute("World")

        recent = orchestrator.memory_system.get_recent(5)

        assert len(recent) >= 4  # 2 conversations

    @pytest.mark.asyncio
    async def test_orchestrator_memory_search(self, orchestrator):
        """Test orchestrator memory search functionality."""
        orchestrator.memory_system.clear()

        await orchestrator.execute("The sky is blue")
        await orchestrator.execute("The grass is green")

        # Search for 'blue'
        results = orchestrator.memory_system.search("blue")

        assert len(results) > 0
        assert any("blue" in str(r) for r in results)

    @pytest.mark.asyncio
    async def test_orchestrator_memory_max_size(self):
        """Test orchestrator respects memory max size."""
        from tests.conftest import MockOrchestrator, MockMemorySystem, MockToolRegistry
        from indusagi.agent.base import AgentConfig

        agent = Agent(AgentConfig())
        memory = MockMemorySystem(max_size=5)
        orch = MockOrchestrator(
            agent=agent,
            tool_registry=MockToolRegistry(),
            memory_system=memory,
        )

        # Add more than max_size memories
        for i in range(10):
            await orch.execute(f"Message {i}")

        # Should not exceed max_size
        assert orch.memory_system.count() <= 5


class TestOrchestratorEdgeCases:
    """Test suite for orchestrator edge cases."""

    @pytest.mark.asyncio
    async def test_orchestrator_empty_prompt(self, orchestrator):
        """Test orchestrator with empty prompt."""
        result = await orchestrator.execute("")

        assert result["success"] is True
        assert "response" in result

    @pytest.mark.asyncio
    async def test_orchestrator_very_long_prompt(self, orchestrator):
        """Test orchestrator with very long prompt."""
        long_prompt = "Test " * 1000

        result = await orchestrator.execute(long_prompt)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_orchestrator_special_characters(self, orchestrator):
        """Test orchestrator with special characters."""
        special_prompt = "Test with \n\t special chars: @#$%^&*()"

        result = await orchestrator.execute(special_prompt)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_orchestrator_unicode(self, orchestrator):
        """Test orchestrator with unicode characters."""
        unicode_prompt = "Hello: 你好 こんにちは 😀"

        result = await orchestrator.execute(unicode_prompt)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_orchestrator_with_kwargs(self, orchestrator):
        """Test orchestrator execution with additional kwargs."""
        result = await orchestrator.execute(
            "Test prompt",
            temperature=0.5,
            max_tokens=100,
        )

        assert result["success"] is True


class TestOrchestratorIntegration:
    """Integration tests for orchestrator."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_orchestrator_full_workflow(self, orchestrator):
        """Test complete orchestrator workflow."""
        orchestrator.memory_system.clear()

        # First interaction
        result1 = await orchestrator.execute("What's 5 + 3?")
        assert result1["success"] is True

        # Second interaction
        result2 = await orchestrator.execute("What's the weather?")
        assert result2["success"] is True

        # Check memory
        assert orchestrator.memory_system.count() >= 4

        # Check agent history
        assert len(orchestrator.agent.history) >= 4

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_orchestrator_with_tool_execution(
        self, orchestrator, calculator_tool
    ):
        """Test orchestrator with actual tool execution."""
        # Execute tool directly
        tool_result = await calculator_tool.execute(operation="add", x=10, y=5)

        assert tool_result.success is True
        assert tool_result.result == 15

        # Execute through orchestrator
        orch_result = await orchestrator.execute_with_tools("Calculate something")

        assert orch_result["success"] is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_orchestrator_state_consistency(self, orchestrator):
        """Test orchestrator maintains consistent state."""
        orchestrator.memory_system.clear()
        orchestrator.agent.reset()

        # Execute multiple times
        for i in range(5):
            result = await orchestrator.execute(f"Message {i}")
            assert result["success"] is True

        # Verify consistency
        memory_count = orchestrator.memory_system.count()
        agent_history_count = len(orchestrator.agent.history)

        # Both should have entries (exact count may vary by implementation)
        assert memory_count > 0
        assert agent_history_count > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_orchestrator_error_handling(self, orchestrator, failing_tool):
        """Test orchestrator handles tool failures gracefully."""
        # Register failing tool
        orchestrator.tool_registry.register(failing_tool)

        # Execute failing tool
        tool_result = await failing_tool.execute()
        assert tool_result.success is False

        # Orchestrator should still work
        result = await orchestrator.execute("Continue after failure")
        assert result["success"] is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_orchestrator_memory_and_agent_sync(self, orchestrator):
        """Test orchestrator keeps memory and agent in sync."""
        orchestrator.memory_system.clear()
        orchestrator.agent.reset()

        messages = ["First", "Second", "Third"]

        for msg in messages:
            await orchestrator.execute(msg)

        # Memory should have all interactions
        memory_count = orchestrator.memory_system.count()
        assert memory_count >= len(messages) * 2

        # Agent should have all interactions
        agent_history = orchestrator.agent.get_history()
        assert len(agent_history) >= len(messages) * 2


class TestOrchestratorCreation:
    """Test suite for orchestrator creation and configuration."""

    @pytest.mark.asyncio
    async def test_create_orchestrator_with_defaults(self):
        """Test creating orchestrator with default components."""
        from tests.conftest import MockOrchestrator, MockMemorySystem, MockToolRegistry
        from indusagi.agent.base import AgentConfig

        agent = Agent(AgentConfig())
        orch = MockOrchestrator(agent)

        assert orch.agent is not None
        assert orch.tool_registry is not None
        assert orch.memory_system is not None

    @pytest.mark.asyncio
    async def test_create_orchestrator_with_custom_components(
        self, agent_config, tool_registry, memory_system
    ):
        """Test creating orchestrator with custom components."""
        from tests.conftest import MockOrchestrator

        agent = Agent(agent_config)
        orch = MockOrchestrator(agent, tool_registry, memory_system)

        assert orch.agent.config == agent_config
        assert orch.tool_registry == tool_registry
        assert orch.memory_system == memory_system

    @pytest.mark.asyncio
    async def test_orchestrator_with_empty_registry(self, agent_config, empty_tool_registry):
        """Test orchestrator with empty tool registry."""
        from tests.conftest import MockOrchestrator, MockMemorySystem

        agent = Agent(agent_config)
        orch = MockOrchestrator(agent, empty_tool_registry, MockMemorySystem())

        assert len(orch.tool_registry.list_tools()) == 0

        # Should still execute
        result = await orch.execute("Test")
        assert result["success"] is True
