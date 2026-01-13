"""Comprehensive integration tests for the entire framework."""

import pytest

from indusagi import Agent, AgentConfig


@pytest.mark.integration
class TestFrameworkIntegration:
    """Integration tests for the complete framework."""

    @pytest.mark.asyncio
    async def test_basic_agent_workflow(self):
        """Test basic agent workflow from start to finish."""
        # Create agent
        agent = Agent()

        # Run agent
        response = await agent.run("Hello!")

        # Verify
        assert isinstance(response, str)
        assert len(agent.history) == 2

        # Run again
        response2 = await agent.run("How are you?")

        assert len(agent.history) == 4

        # Reset
        agent.reset()
        assert len(agent.history) == 0

    @pytest.mark.asyncio
    async def test_agent_with_config_workflow(self, sample_config):
        """Test agent with configuration workflow."""
        # Create agent config from main config
        agent_config = AgentConfig(
            name="TestBot",
            model=sample_config.default_model,
            temperature=sample_config.default_temperature,
        )

        # Create agent
        agent = Agent(agent_config)

        # Verify config
        assert agent.config.name == "TestBot"
        assert agent.config.model == sample_config.default_model

        # Run agent
        response = await agent.run("Test message")

        assert response is not None

    @pytest.mark.asyncio
    async def test_agent_with_tools_workflow(
        self, agent_config, calculator_tool, weather_tool
    ):
        """Test complete agent with tools workflow."""
        # Create agent with tools
        agent = Agent(agent_config, tools=[calculator_tool, weather_tool])

        assert len(agent.tools) == 2

        # Execute calculator tool
        calc_result = await calculator_tool.execute(operation="add", x=5, y=3)
        assert calc_result.success is True
        assert calc_result.result == 8

        # Execute weather tool
        weather_result = await weather_tool.execute(location="New York")
        assert weather_result.success is True
        assert weather_result.result["location"] == "New York"

        # Run agent
        response = await agent.run("Calculate and check weather")
        assert response is not None

    @pytest.mark.asyncio
    async def test_tool_registry_workflow(self, tool_registry, agent_config):
        """Test tool registry integration workflow."""
        # Create agent
        agent = Agent(agent_config)

        # Get tools from registry
        calculator = tool_registry.get_tool("calculator")
        weather = tool_registry.get_tool("weather")

        # Add to agent
        agent.add_tool(calculator)
        agent.add_tool(weather)

        assert len(agent.tools) == 2

        # Execute tools
        calc_result = await calculator.execute(operation="multiply", x=6, y=7)
        assert calc_result.result == 42

        # Run agent
        await agent.run("Use tools")

        # Remove tool
        agent.remove_tool(calculator)
        assert len(agent.tools) == 1

    @pytest.mark.asyncio
    async def test_orchestrator_complete_workflow(self, orchestrator):
        """Test complete orchestrator workflow."""
        # Clear state
        orchestrator.memory_system.clear()
        orchestrator.agent.reset()

        # Execute multiple prompts
        result1 = await orchestrator.execute("First message")
        assert result1["success"] is True

        result2 = await orchestrator.execute("Second message")
        assert result2["success"] is True

        # Check memory
        assert orchestrator.memory_system.count() >= 4

        # Check agent history
        assert len(orchestrator.agent.history) >= 4

        # Search memory
        results = orchestrator.memory_system.search("message")
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_memory_with_agent_workflow(self, memory_system, agent_config):
        """Test memory system with agent workflow."""
        agent = Agent(agent_config)

        # Run conversations
        await agent.run("Message 1")
        await agent.run("Message 2")

        # Store in memory
        for msg in agent.history:
            memory_system.add(msg)

        # Verify
        assert memory_system.count() >= 4

        # Search
        results = memory_system.search("Message")
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_error_handling_workflow(
        self, agent_config, calculator_tool, failing_tool
    ):
        """Test error handling across the framework."""
        agent = Agent(agent_config, tools=[calculator_tool, failing_tool])

        # Execute failing tool
        fail_result = await failing_tool.execute()
        assert fail_result.success is False

        # Agent should still work
        response = await agent.run("Continue after error")
        assert response is not None

        # Calculator should still work
        calc_result = await calculator_tool.execute(operation="add", x=1, y=1)
        assert calc_result.success is True

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self, calculator_tool, weather_tool):
        """Test executing multiple tools concurrently."""
        import asyncio

        # Execute tools concurrently
        calc_task = calculator_tool.execute(operation="add", x=5, y=3)
        weather_task = weather_tool.execute(location="London")

        calc_result, weather_result = await asyncio.gather(calc_task, weather_task)

        assert calc_result.success is True
        assert calc_result.result == 8

        assert weather_result.success is True
        assert weather_result.result["location"] == "London"

    @pytest.mark.asyncio
    async def test_agent_state_persistence(self, agent_config):
        """Test that agent state persists correctly."""
        agent = Agent(agent_config)

        # First conversation
        await agent.run("Remember: blue")
        history1 = agent.get_history()

        # Second conversation
        await agent.run("What color?")
        history2 = agent.get_history()

        # History should grow
        assert len(history2) > len(history1)

        # Original history should still be there
        assert "blue" in str(history2)


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end scenario tests."""

    @pytest.mark.asyncio
    async def test_calculator_conversation(self, agent_config, calculator_tool):
        """Test a complete calculator conversation."""
        agent = Agent(agent_config, tools=[calculator_tool])

        # Add numbers
        add_result = await calculator_tool.execute(operation="add", x=10, y=5)
        assert add_result.result == 15

        # Multiply result
        mult_result = await calculator_tool.execute(operation="multiply", x=15, y=2)
        assert mult_result.result == 30

        # Subtract
        sub_result = await calculator_tool.execute(operation="subtract", x=30, y=10)
        assert sub_result.result == 20

        # Divide
        div_result = await calculator_tool.execute(operation="divide", x=20, y=4)
        assert div_result.result == 5

        # Agent interaction
        await agent.run("Calculate 5 + 5")
        assert len(agent.history) > 0

    @pytest.mark.asyncio
    async def test_weather_query_scenario(self, agent_config, weather_tool):
        """Test a weather query scenario."""
        agent = Agent(agent_config, tools=[weather_tool])

        # Query weather for multiple cities
        cities = ["New York", "London", "Tokyo"]

        for city in cities:
            result = await weather_tool.execute(location=city)

            assert result.success is True
            assert result.result["location"] == city
            assert "temperature" in result.result

        # Agent conversation
        await agent.run("What's the weather in Paris?")
        assert len(agent.history) > 0

    @pytest.mark.asyncio
    async def test_multi_tool_scenario(
        self, agent_config, calculator_tool, weather_tool
    ):
        """Test scenario using multiple tools."""
        agent = Agent(agent_config, tools=[calculator_tool, weather_tool])

        # Use calculator
        calc_result = await calculator_tool.execute(operation="add", x=20, y=22)
        assert calc_result.result == 42

        # Use weather
        weather_result = await weather_tool.execute(location="New York")
        assert weather_result.success is True

        # Agent uses both
        await agent.run("Calculate temperature + 10")

        assert len(agent.tools) == 2
        assert len(agent.history) > 0

    @pytest.mark.asyncio
    async def test_error_recovery_scenario(self, agent_config, calculator_tool):
        """Test error recovery scenario."""
        agent = Agent(agent_config, tools=[calculator_tool])

        # Cause error
        error_result = await calculator_tool.execute(operation="divide", x=10, y=0)
        assert error_result.success is False

        # Recover with valid operation
        success_result = await calculator_tool.execute(operation="divide", x=10, y=2)
        assert success_result.success is True
        assert success_result.result == 5

        # Agent continues
        await agent.run("Continue after error")
        assert len(agent.history) > 0

    @pytest.mark.asyncio
    async def test_conversation_history_scenario(self, orchestrator):
        """Test maintaining conversation history."""
        orchestrator.memory_system.clear()
        orchestrator.agent.reset()

        # Multi-turn conversation
        await orchestrator.execute("My name is Alice")
        await orchestrator.execute("What is my name?")
        await orchestrator.execute("I like programming")
        await orchestrator.execute("What do I like?")

        # Check memory
        memories = orchestrator.memory_system.get_recent(10)
        assert len(memories) >= 8

        # Search for context
        alice_memories = orchestrator.memory_system.search("Alice")
        assert len(alice_memories) > 0

        programming_memories = orchestrator.memory_system.search("programming")
        assert len(programming_memories) > 0

    @pytest.mark.asyncio
    async def test_tool_chaining_scenario(self, calculator_tool, weather_tool):
        """Test chaining tool outputs."""
        # Calculate a value
        step1 = await calculator_tool.execute(operation="add", x=15, y=10)
        result1 = step1.result  # 25

        # Use in next calculation
        step2 = await calculator_tool.execute(operation="multiply", x=result1, y=2)
        result2 = step2.result  # 50

        # Final calculation
        step3 = await calculator_tool.execute(operation="divide", x=result2, y=10)
        final_result = step3.result  # 5

        assert final_result == 5

        # Get weather (independent operation)
        weather = await weather_tool.execute(location="City")
        assert weather.success is True


@pytest.mark.integration
class TestFrameworkLimits:
    """Test framework behavior at limits."""

    @pytest.mark.asyncio
    async def test_maximum_history_length(self):
        """Test agent behavior with maximum history length."""
        agent = Agent()

        # Add many messages
        for i in range(150):
            await agent.run(f"Message {i}")

        # History should be very long
        assert len(agent.history) > 100

    @pytest.mark.asyncio
    async def test_maximum_memory_size(self):
        """Test memory system at maximum size."""
        from tests.conftest import MockMemorySystem

        memory = MockMemorySystem(max_size=10)

        # Add more than max
        for i in range(50):
            memory.add({"number": i})

        # Should respect max size
        assert memory.count() == 10

        # Should have most recent
        recent = memory.get_recent(10)
        numbers = [m["number"] for m in recent]
        assert 49 in numbers

    @pytest.mark.asyncio
    async def test_many_tools(self, agent_config):
        """Test agent with many tools."""
        from tests.conftest import MockCalculatorTool

        agent = Agent(agent_config)

        # Add many tools
        for i in range(20):
            config = ToolConfig(
                name=f"tool_{i}",
                description=f"Tool number {i}",
            )
            tool = MockCalculatorTool(config)
            agent.add_tool(tool)

        assert len(agent.tools) == 20

    @pytest.mark.asyncio
    async def test_very_long_prompt(self, agent_config):
        """Test agent with very long prompt."""
        agent = Agent(agent_config)

        long_prompt = "Test " * 10000  # Very long

        response = await agent.run(long_prompt)

        assert response is not None
        assert len(agent.history) == 2


@pytest.mark.integration
class TestFrameworkPerformance:
    """Performance tests for the framework."""

    @pytest.mark.asyncio
    async def test_rapid_tool_execution(self, calculator_tool):
        """Test rapid consecutive tool executions."""
        import time

        start = time.time()

        for i in range(100):
            result = await calculator_tool.execute(operation="add", x=i, y=1)
            assert result.success is True

        duration = time.time() - start

        # Should complete quickly (under 5 seconds for 100 operations)
        assert duration < 5.0

    @pytest.mark.asyncio
    async def test_rapid_agent_runs(self, agent_config):
        """Test rapid consecutive agent runs."""
        import time

        agent = Agent(agent_config)

        start = time.time()

        for i in range(50):
            await agent.run(f"Message {i}")

        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 5.0

    @pytest.mark.asyncio
    async def test_memory_search_performance(self):
        """Test memory search with many entries."""
        from tests.conftest import MockMemorySystem
        import time

        memory = MockMemorySystem(max_size=1000)

        # Add many memories
        for i in range(500):
            memory.add({"number": i, "content": f"Message {i}"})

        # Search should be fast
        start = time.time()

        results = memory.search("Message 250")

        duration = time.time() - start

        assert len(results) > 0
        assert duration < 1.0  # Should be under 1 second


@pytest.mark.integration
class TestFrameworkReliability:
    """Reliability tests for the framework."""

    @pytest.mark.asyncio
    async def test_framework_resilience(
        self, agent_config, calculator_tool, failing_tool
    ):
        """Test framework resilience to errors."""
        agent = Agent(agent_config, tools=[calculator_tool, failing_tool])

        # Mix of success and failures
        for i in range(10):
            if i % 2 == 0:
                result = await calculator_tool.execute(operation="add", x=i, y=1)
                assert result.success is True
            else:
                result = await failing_tool.execute()
                assert result.success is False

        # Agent should still work
        response = await agent.run("Continue")
        assert response is not None

    @pytest.mark.asyncio
    async def test_state_consistency(self, orchestrator):
        """Test state consistency across operations."""
        orchestrator.memory_system.clear()
        orchestrator.agent.reset()

        # Perform various operations
        await orchestrator.execute("Message 1")
        memory_count_1 = orchestrator.memory_system.count()

        await orchestrator.execute("Message 2")
        memory_count_2 = orchestrator.memory_system.count()

        # State should be consistent
        assert memory_count_2 > memory_count_1
        assert len(orchestrator.agent.history) >= 4

    @pytest.mark.asyncio
    async def test_cleanup_and_reset(self, orchestrator):
        """Test proper cleanup and reset."""
        # Add data
        await orchestrator.execute("Test message")

        assert orchestrator.memory_system.count() > 0
        assert len(orchestrator.agent.history) > 0

        # Cleanup
        orchestrator.memory_system.clear()
        orchestrator.agent.reset()

        # Should be clean
        assert orchestrator.memory_system.count() == 0
        assert len(orchestrator.agent.history) == 0

        # Should still work after cleanup
        result = await orchestrator.execute("New message")
        assert result["success"] is True
