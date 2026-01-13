"""Comprehensive tests for Tool system and Tool Registry."""

import pytest

from indusagi.tools.base import BaseTool

# Import compatibility classes from conftest
import sys
sys.path.insert(0, 'tests')
from conftest import ToolConfig, ToolResult


class TestToolResult:
    """Test suite for ToolResult model."""

    def test_tool_result_success(self):
        """Test creating a successful ToolResult."""
        result = ToolResult(
            success=True,
            result="Operation completed",
        )

        assert result.success is True
        assert result.result == "Operation completed"
        assert result.error is None
        assert result.metadata == {}

    def test_tool_result_failure(self):
        """Test creating a failed ToolResult."""
        result = ToolResult(
            success=False,
            result=None,
            error="Operation failed",
        )

        assert result.success is False
        assert result.result is None
        assert result.error == "Operation failed"

    def test_tool_result_with_metadata(self):
        """Test ToolResult with metadata."""
        result = ToolResult(
            success=True,
            result=42,
            metadata={"operation": "add", "operands": [20, 22]},
        )

        assert result.success is True
        assert result.result == 42
        assert result.metadata["operation"] == "add"
        assert result.metadata["operands"] == [20, 22]

    def test_tool_result_dict_conversion(self):
        """Test ToolResult can be converted to dict."""
        result = ToolResult(
            success=True,
            result="test",
            metadata={"key": "value"},
        )

        result_dict = result.model_dump()

        assert result_dict["success"] is True
        assert result_dict["result"] == "test"
        assert result_dict["metadata"]["key"] == "value"


class TestToolConfig:
    """Test suite for ToolConfig model."""

    def test_tool_config_basic(self):
        """Test creating a basic ToolConfig."""
        config = ToolConfig(
            name="test_tool",
            description="A test tool",
        )

        assert config.name == "test_tool"
        assert config.description == "A test tool"
        assert config.parameters == {}

    def test_tool_config_with_parameters(self):
        """Test ToolConfig with parameters schema."""
        config = ToolConfig(
            name="calculator",
            description="Math calculator",
            parameters={
                "operation": {"type": "string"},
                "x": {"type": "number"},
                "y": {"type": "number"},
            },
        )

        assert config.name == "calculator"
        assert "operation" in config.parameters
        assert config.parameters["x"]["type"] == "number"

    def test_tool_config_dict_conversion(self):
        """Test ToolConfig can be converted to dict."""
        config = ToolConfig(
            name="test_tool",
            description="Test description",
            parameters={"param": {"type": "string"}},
        )

        config_dict = config.model_dump()

        assert config_dict["name"] == "test_tool"
        assert config_dict["description"] == "Test description"


class TestBaseTool:
    """Test suite for BaseTool abstract class."""

    def test_base_tool_is_abstract(self):
        """Test that BaseTool cannot be instantiated directly."""
        config = ToolConfig(name="test", description="test")

        with pytest.raises(TypeError):
            BaseTool(config)

    @pytest.mark.asyncio
    async def test_concrete_tool_initialization(self, calculator_tool):
        """Test that a concrete tool initializes correctly."""
        assert calculator_tool.name == "calculator"
        assert calculator_tool.description == "Perform basic arithmetic operations"
        assert calculator_tool.config.name == "calculator"

    @pytest.mark.asyncio
    async def test_tool_name_property(self, calculator_tool):
        """Test tool.name property."""
        assert calculator_tool.name == calculator_tool.config.name

    @pytest.mark.asyncio
    async def test_tool_description_property(self, calculator_tool):
        """Test tool.description property."""
        assert calculator_tool.description == calculator_tool.config.description

    @pytest.mark.asyncio
    async def test_tool_to_dict(self, calculator_tool):
        """Test tool.to_dict() method."""
        tool_dict = calculator_tool.to_dict()

        assert tool_dict["name"] == "calculator"
        assert tool_dict["description"] == "Perform basic arithmetic operations"
        assert "parameters" in tool_dict

    @pytest.mark.asyncio
    async def test_tool_validate_input_default(self, calculator_tool):
        """Test default validate_input implementation."""
        # Default implementation always returns True
        is_valid = calculator_tool.validate_input(operation="add", x=1, y=2)

        assert is_valid is True


class TestCalculatorTool:
    """Test suite for the calculator tool."""

    @pytest.mark.asyncio
    async def test_calculator_add(self, calculator_tool):
        """Test calculator addition."""
        result = await calculator_tool.execute(operation="add", x=5, y=3)

        assert result.success is True
        assert result.result == 8
        assert result.error is None

    @pytest.mark.asyncio
    async def test_calculator_subtract(self, calculator_tool):
        """Test calculator subtraction."""
        result = await calculator_tool.execute(operation="subtract", x=10, y=4)

        assert result.success is True
        assert result.result == 6

    @pytest.mark.asyncio
    async def test_calculator_multiply(self, calculator_tool):
        """Test calculator multiplication."""
        result = await calculator_tool.execute(operation="multiply", x=6, y=7)

        assert result.success is True
        assert result.result == 42

    @pytest.mark.asyncio
    async def test_calculator_divide(self, calculator_tool):
        """Test calculator division."""
        result = await calculator_tool.execute(operation="divide", x=15, y=3)

        assert result.success is True
        assert result.result == 5

    @pytest.mark.asyncio
    async def test_calculator_divide_by_zero(self, calculator_tool):
        """Test calculator handles division by zero."""
        result = await calculator_tool.execute(operation="divide", x=10, y=0)

        assert result.success is False
        assert result.result is None
        assert "Division by zero" in result.error

    @pytest.mark.asyncio
    async def test_calculator_invalid_operation(self, calculator_tool):
        """Test calculator handles invalid operation."""
        result = await calculator_tool.execute(operation="power", x=2, y=3)

        assert result.success is False
        assert "Unknown operation" in result.error

    @pytest.mark.asyncio
    async def test_calculator_metadata(self, calculator_tool):
        """Test calculator includes metadata in result."""
        result = await calculator_tool.execute(operation="add", x=5, y=3)

        assert result.success is True
        assert result.metadata["operation"] == "add"
        assert result.metadata["x"] == 5
        assert result.metadata["y"] == 3

    @pytest.mark.asyncio
    async def test_calculator_float_numbers(self, calculator_tool):
        """Test calculator with float numbers."""
        result = await calculator_tool.execute(operation="divide", x=7, y=2)

        assert result.success is True
        assert result.result == 3.5

    @pytest.mark.asyncio
    async def test_calculator_negative_numbers(self, calculator_tool):
        """Test calculator with negative numbers."""
        result = await calculator_tool.execute(operation="add", x=-5, y=3)

        assert result.success is True
        assert result.result == -2


class TestWeatherTool:
    """Test suite for the weather tool."""

    @pytest.mark.asyncio
    async def test_weather_basic(self, weather_tool):
        """Test basic weather tool execution."""
        result = await weather_tool.execute(location="New York")

        assert result.success is True
        assert result.result["location"] == "New York"
        assert "temperature" in result.result
        assert "condition" in result.result

    @pytest.mark.asyncio
    async def test_weather_different_locations(self, weather_tool):
        """Test weather tool with different locations."""
        locations = ["London", "Tokyo", "Sydney"]

        for location in locations:
            result = await weather_tool.execute(location=location)

            assert result.success is True
            assert result.result["location"] == location

    @pytest.mark.asyncio
    async def test_weather_metadata(self, weather_tool):
        """Test weather tool includes metadata."""
        result = await weather_tool.execute(location="Paris")

        assert result.success is True
        assert result.metadata["source"] == "mock"

    @pytest.mark.asyncio
    async def test_weather_no_location(self, weather_tool):
        """Test weather tool with no location provided."""
        result = await weather_tool.execute()

        assert result.success is True
        assert result.result["location"] == "Unknown"


class TestFailingTool:
    """Test suite for the failing tool (error handling)."""

    @pytest.mark.asyncio
    async def test_failing_tool_always_fails(self, failing_tool):
        """Test that failing tool always returns failure."""
        result = await failing_tool.execute()

        assert result.success is False
        assert result.result is None
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_failing_tool_with_args(self, failing_tool):
        """Test failing tool still fails with any arguments."""
        result = await failing_tool.execute(arg1="value", arg2=42)

        assert result.success is False


class TestToolRegistry:
    """Test suite for the Tool Registry."""

    def test_tool_registry_initialization(self, empty_tool_registry):
        """Test tool registry initializes empty."""
        assert len(empty_tool_registry.list_tools()) == 0

    def test_tool_registry_register_tool(self, empty_tool_registry, calculator_tool):
        """Test registering a tool."""
        empty_tool_registry.register(calculator_tool)

        assert len(empty_tool_registry.list_tools()) == 1
        assert empty_tool_registry.get_tool("calculator") == calculator_tool

    def test_tool_registry_register_multiple_tools(
        self, empty_tool_registry, calculator_tool, weather_tool
    ):
        """Test registering multiple tools."""
        empty_tool_registry.register(calculator_tool)
        empty_tool_registry.register(weather_tool)

        assert len(empty_tool_registry.list_tools()) == 2

    def test_tool_registry_get_tool(self, tool_registry):
        """Test getting a tool by name."""
        tool = tool_registry.get_tool("calculator")

        assert tool is not None
        assert tool.name == "calculator"

    def test_tool_registry_get_nonexistent_tool(self, tool_registry):
        """Test getting a tool that doesn't exist."""
        tool = tool_registry.get_tool("nonexistent")

        assert tool is None

    def test_tool_registry_list_tools(self, tool_registry):
        """Test listing all tools."""
        tools = tool_registry.list_tools()

        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "calculator" in tool_names
        assert "weather" in tool_names

    def test_tool_registry_unregister_tool(self, tool_registry):
        """Test unregistering a tool."""
        assert len(tool_registry.list_tools()) == 2

        tool_registry.unregister("calculator")

        assert len(tool_registry.list_tools()) == 1
        assert tool_registry.get_tool("calculator") is None

    def test_tool_registry_unregister_nonexistent_tool(self, tool_registry):
        """Test unregistering a tool that doesn't exist (should not error)."""
        initial_count = len(tool_registry.list_tools())

        tool_registry.unregister("nonexistent")

        assert len(tool_registry.list_tools()) == initial_count

    def test_tool_registry_clear(self, tool_registry):
        """Test clearing all tools."""
        assert len(tool_registry.list_tools()) > 0

        tool_registry.clear()

        assert len(tool_registry.list_tools()) == 0

    def test_tool_registry_replace_tool(
        self, empty_tool_registry, calculator_tool
    ):
        """Test replacing a tool with the same name."""
        # Register original tool
        empty_tool_registry.register(calculator_tool)

        # Create new tool with same name
        new_config = ToolConfig(
            name="calculator",
            description="New calculator",
        )

        from tests.conftest import MockCalculatorTool

        new_tool = MockCalculatorTool(new_config)

        # Register new tool (should replace)
        empty_tool_registry.register(new_tool)

        # Should still only have one tool
        assert len(empty_tool_registry.list_tools()) == 1

        # Should be the new tool
        tool = empty_tool_registry.get_tool("calculator")
        assert tool.description == "New calculator"


class TestToolEdgeCases:
    """Test suite for tool edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_tool_with_no_parameters(self):
        """Test tool execution with no parameters."""
        config = ToolConfig(
            name="simple_tool",
            description="Simple tool with no params",
        )

        from tests.conftest import MockWeatherTool

        tool = MockWeatherTool(config)
        result = await tool.execute()

        assert result.success is True

    @pytest.mark.asyncio
    async def test_tool_with_unexpected_parameters(self, calculator_tool):
        """Test tool execution with unexpected parameters."""
        # Tool should handle gracefully
        result = await calculator_tool.execute(
            operation="add",
            x=5,
            y=3,
            unexpected_param="value",
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_tool_with_missing_parameters(self, calculator_tool):
        """Test tool execution with missing parameters."""
        # Should use defaults (x=0, y=0)
        result = await calculator_tool.execute(operation="add")

        assert result.success is True
        assert result.result == 0

    @pytest.mark.asyncio
    async def test_tool_result_with_complex_data(self):
        """Test ToolResult with complex nested data."""
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
            "metadata": {
                "count": 2,
                "nested": {"deep": True},
            },
        }

        result = ToolResult(
            success=True,
            result=complex_data,
        )

        assert result.success is True
        assert len(result.result["users"]) == 2
        assert result.result["metadata"]["nested"]["deep"] is True


class TestToolIntegration:
    """Integration tests for tool system."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tool_chain_execution(self, calculator_tool, weather_tool):
        """Test executing multiple tools in sequence."""
        # Execute calculator
        calc_result = await calculator_tool.execute(operation="add", x=10, y=5)
        assert calc_result.success is True

        # Use calculator result in weather tool (just for testing)
        weather_result = await weather_tool.execute(location="City")
        assert weather_result.success is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tool_registry_full_workflow(
        self, empty_tool_registry, calculator_tool, weather_tool, failing_tool
    ):
        """Test complete tool registry workflow."""
        # Register tools
        empty_tool_registry.register(calculator_tool)
        empty_tool_registry.register(weather_tool)
        empty_tool_registry.register(failing_tool)

        assert len(empty_tool_registry.list_tools()) == 3

        # Execute tools
        calc = empty_tool_registry.get_tool("calculator")
        calc_result = await calc.execute(operation="multiply", x=6, y=7)
        assert calc_result.success is True

        weather = empty_tool_registry.get_tool("weather")
        weather_result = await weather.execute(location="Tokyo")
        assert weather_result.success is True

        # Handle failing tool
        failing = empty_tool_registry.get_tool("failing_tool")
        fail_result = await failing.execute()
        assert fail_result.success is False

        # Unregister failing tool
        empty_tool_registry.unregister("failing_tool")
        assert len(empty_tool_registry.list_tools()) == 2

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tool_error_recovery(self, calculator_tool):
        """Test tool can recover from errors."""
        # Cause an error
        error_result = await calculator_tool.execute(operation="divide", x=10, y=0)
        assert error_result.success is False

        # Tool should still work after error
        success_result = await calculator_tool.execute(operation="add", x=5, y=3)
        assert success_result.success is True
        assert success_result.result == 8
