"""Pytest configuration and fixtures."""

import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from indusagi import Agent, AgentConfig
from indusagi.tools.base import BaseTool


# Compatibility classes for legacy test fixtures
class ToolResult:
    """Legacy tool result class for backward compatibility with existing tests."""
    def __init__(self, success: bool, result: Any = None, error: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.result = result
        self.error = error
        self.metadata = metadata or {}


class ToolConfig:
    """Legacy tool config class for backward compatibility with existing tests."""
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}


# ============================================================================
# Pytest Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def sample_config():
    """Fixture providing a sample configuration (deprecated - use agent_config instead)."""
    # Config class no longer exists - return AgentConfig instead
    return AgentConfig(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=1000,
    )


@pytest.fixture
def agent_config():
    """Fixture providing a sample agent configuration."""
    return AgentConfig(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=1000,
    )


@pytest.fixture
def llm_config():
    """Fixture providing LLM configuration (deprecated - use agent_config instead)."""
    # LLMConfig class no longer exists - return AgentConfig instead
    return AgentConfig(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=1000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )


# ============================================================================
# Mock OpenAI Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """Fixture providing a mock OpenAI response."""
    return {
        "id": "chatcmpl-123456",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the assistant.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }


@pytest.fixture
def mock_openai_tool_response():
    """Fixture providing a mock OpenAI response with tool calls."""
    return {
        "id": "chatcmpl-123456",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": "calculator",
                                "arguments": '{"operation": "add", "x": 5, "y": 3}',
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80,
        },
    }


@pytest.fixture
def mock_openai_client():
    """Fixture providing a mock OpenAI client."""
    mock_client = MagicMock()

    # Mock chat completions
    mock_completion = MagicMock()
    mock_completion.id = "chatcmpl-123456"
    mock_completion.model = "gpt-4"
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                role="assistant",
                content="This is a test response.",
            ),
            finish_reason="stop",
        )
    ]

    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    return mock_client


@pytest.fixture
def mock_openai_client_with_error():
    """Fixture providing a mock OpenAI client that raises errors."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=Exception("API Error: Invalid API key")
    )
    return mock_client


# ============================================================================
# Tool Fixtures
# ============================================================================

class MockCalculatorTool:
    """Mock calculator tool for testing (legacy pattern)."""

    def __init__(self, config: ToolConfig):
        self.name = config.name
        self.description = config.description
        self.config = config

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the calculator tool."""
        operation = kwargs.get("operation")
        x = kwargs.get("x", 0)
        y = kwargs.get("y", 0)

        if operation == "add":
            result = x + y
        elif operation == "subtract":
            result = x - y
        elif operation == "multiply":
            result = x * y
        elif operation == "divide":
            if y == 0:
                return ToolResult(
                    success=False,
                    result=None,
                    error="Division by zero",
                )
            result = x / y
        else:
            return ToolResult(
                success=False,
                result=None,
                error=f"Unknown operation: {operation}",
            )

        return ToolResult(
            success=True,
            result=result,
            metadata={"operation": operation, "x": x, "y": y},
        )


class MockWeatherTool:
    """Mock weather tool for testing (legacy pattern)."""

    def __init__(self, config: ToolConfig):
        self.name = config.name
        self.description = config.description
        self.config = config

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the weather tool."""
        location = kwargs.get("location", "Unknown")

        # Mock weather data
        weather_data = {
            "location": location,
            "temperature": 72,
            "condition": "Sunny",
            "humidity": 65,
        }

        return ToolResult(
            success=True,
            result=weather_data,
            metadata={"source": "mock"},
        )


class MockFailingTool:
    """Mock tool that always fails for testing error handling (legacy pattern)."""

    def __init__(self, config: ToolConfig):
        self.name = config.name
        self.description = config.description
        self.config = config

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the failing tool."""
        return ToolResult(
            success=False,
            result=None,
            error="Tool execution failed intentionally",
        )


@pytest.fixture
def calculator_tool():
    """Fixture providing a calculator tool."""
    config = ToolConfig(
        name="calculator",
        description="Perform basic arithmetic operations",
        parameters={
            "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
            "x": {"type": "number"},
            "y": {"type": "number"},
        },
    )
    return MockCalculatorTool(config)


@pytest.fixture
def weather_tool():
    """Fixture providing a weather tool."""
    config = ToolConfig(
        name="weather",
        description="Get weather information for a location",
        parameters={
            "location": {"type": "string"},
        },
    )
    return MockWeatherTool(config)


@pytest.fixture
def failing_tool():
    """Fixture providing a tool that always fails."""
    config = ToolConfig(
        name="failing_tool",
        description="A tool that always fails",
        parameters={},
    )
    return MockFailingTool(config)


@pytest.fixture
def tool_list(calculator_tool, weather_tool):
    """Fixture providing a list of tools."""
    return [calculator_tool, weather_tool]


# ============================================================================
# Tool Registry Fixtures (for future use)
# ============================================================================

class MockToolRegistry:
    """Mock tool registry for testing."""

    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Any] = {}

    def register(self, tool: Any):
        """Register a tool."""
        self.tools[tool.name] = tool

    def unregister(self, tool_name: str):
        """Unregister a tool."""
        if tool_name in self.tools:
            del self.tools[tool_name]

    def get_tool(self, tool_name: str) -> Any:
        """Get a tool by name."""
        return self.tools.get(tool_name)

    def list_tools(self) -> List[Any]:
        """List all registered tools."""
        return list(self.tools.values())

    def clear(self):
        """Clear all tools."""
        self.tools.clear()


@pytest.fixture
def tool_registry(calculator_tool, weather_tool):
    """Fixture providing a tool registry."""
    registry = MockToolRegistry()
    registry.register(calculator_tool)
    registry.register(weather_tool)
    return registry


@pytest.fixture
def empty_tool_registry():
    """Fixture providing an empty tool registry."""
    return MockToolRegistry()


# ============================================================================
# Memory System Fixtures (for future use)
# ============================================================================

class MockMemorySystem:
    """Mock memory system for testing."""

    def __init__(self, max_size: int = 100):
        """Initialize the memory system."""
        self.max_size = max_size
        self.memories: List[Dict[str, Any]] = []

    def add(self, memory: Dict[str, Any]):
        """Add a memory."""
        self.memories.append(memory)
        if len(self.memories) > self.max_size:
            self.memories.pop(0)

    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get recent memories."""
        return self.memories[-n:]

    def clear(self):
        """Clear all memories."""
        self.memories.clear()

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search memories (simple mock implementation)."""
        results = []
        for memory in self.memories:
            if query.lower() in str(memory).lower():
                results.append(memory)
        return results

    def count(self) -> int:
        """Get count of memories."""
        return len(self.memories)


@pytest.fixture
def memory_system():
    """Fixture providing a memory system."""
    return MockMemorySystem(max_size=100)


@pytest.fixture
def memory_with_data():
    """Fixture providing a memory system with pre-populated data."""
    memory = MockMemorySystem(max_size=100)
    memory.add({"role": "user", "content": "Hello"})
    memory.add({"role": "assistant", "content": "Hi there!"})
    memory.add({"role": "user", "content": "What's the weather?"})
    memory.add({"role": "assistant", "content": "It's sunny today."})
    return memory


# ============================================================================
# Orchestrator Fixtures (for future use)
# ============================================================================

class MockOrchestrator:
    """Mock orchestrator for testing."""

    def __init__(self, agent, tool_registry=None, memory_system=None):
        """Initialize the orchestrator."""
        self.agent = agent
        self.tool_registry = tool_registry or MockToolRegistry()
        self.memory_system = memory_system or MockMemorySystem()
        self.is_running = False

    async def execute(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute a prompt through the orchestrator."""
        self.is_running = True

        # Add to memory
        self.memory_system.add({"role": "user", "content": prompt})

        # Run agent
        response = await self.agent.run(prompt, **kwargs)

        # Add response to memory
        self.memory_system.add({"role": "assistant", "content": response})

        self.is_running = False

        return {
            "success": True,
            "response": response,
            "tool_calls": [],
        }

    async def execute_with_tools(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute with tool calling capability."""
        self.is_running = True

        # Simulate tool calling
        tools_used = []

        # Add to memory
        self.memory_system.add({"role": "user", "content": prompt})

        # Run agent
        response = await self.agent.run(prompt, **kwargs)

        # Add response to memory
        self.memory_system.add({"role": "assistant", "content": response})

        self.is_running = False

        return {
            "success": True,
            "response": response,
            "tool_calls": tools_used,
        }


@pytest.fixture
def orchestrator(agent_config, tool_registry, memory_system):
    """Fixture providing an orchestrator."""
    # Agent is already imported at top of file
    agent = Agent("TestAgent", "You are a helpful test assistant.", config=agent_config)
    return MockOrchestrator(agent, tool_registry, memory_system)


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def temp_env_vars(monkeypatch):
    """Fixture for temporarily setting environment variables."""
    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return _set_env


@pytest.fixture
def mock_api_key(monkeypatch):
    """Fixture that sets a mock API key in environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123456789")


# ============================================================================
# Skip Markers
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: mark test as requiring valid API key"
    )
