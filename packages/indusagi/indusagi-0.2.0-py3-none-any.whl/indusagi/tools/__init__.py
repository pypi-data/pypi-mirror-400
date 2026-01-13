"""
Tools Package - Base tool classes and development tools.
"""
from typing import Dict, List, Any
from .base import BaseTool, ToolContext, get_tool_context
from .dev import Bash, Read, Edit, Write, Glob, Grep, TodoWrite
from .handoff import handoff_to_agent, set_current_agency, get_current_agency, register_handoff_tool


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self):
        self._tools: Dict[str, type[BaseTool]] = {}
        self.context = get_tool_context()  # Shared context for all tools
        self._pending_handoff: Dict[str, Any] | None = None  # For agency handoffs

    def register(self, tool_class: type[BaseTool]) -> None:
        """Register a tool class."""
        self._tools[tool_class.name] = tool_class

    def execute(self, name: str, **kwargs) -> str:
        """Execute a tool by name with given arguments."""
        if name not in self._tools:
            # Check if it's the handoff tool
            if name == "handoff_to_agent":
                return handoff_to_agent(**kwargs)
            raise ValueError(f"Tool '{name}' not found in registry")

        tool_class = self._tools[name]
        tool_instance = tool_class(**kwargs)
        return tool_instance.execute()

    @property
    def schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for OpenAI function calling."""
        schemas = []
        for tool_class in self._tools.values():
            schemas.append(tool_class.get_schema())
        return schemas

    def get_tool_names(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())


# Global registry instance
registry = ToolRegistry()

__all__ = [
    # Base classes
    "BaseTool",
    "ToolContext",
    "get_tool_context",
    # Development tools
    "Bash",
    "Read",
    "Edit",
    "Write",
    "Glob",
    "Grep",
    "TodoWrite",
    # Handoff tools
    "handoff_to_agent",
    "set_current_agency",
    "get_current_agency",
    "register_handoff_tool",
    # Compatibility exports (to be implemented)
    "registry",
    "ToolRegistry",
]
