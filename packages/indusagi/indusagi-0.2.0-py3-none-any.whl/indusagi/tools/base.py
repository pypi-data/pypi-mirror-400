"""
Base Tool - Foundation for Agency Swarm-compatible tools.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, ClassVar
from pydantic import BaseModel


class ToolContext:
    """Shared context for tools within an agency."""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._read_files: set = set()

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def mark_file_read(self, path: str) -> None:
        self._read_files.add(path)

    def was_file_read(self, path: str) -> bool:
        return path in self._read_files


# Global context instance
_tool_context = ToolContext()


def get_tool_context() -> ToolContext:
    """Get the global tool context."""
    return _tool_context


class BaseTool(BaseModel, ABC):
    """
    Base class for all tools.

    Tools inherit from this class and implement the execute() method.
    Uses Pydantic for parameter validation and schema generation.

    Example:
        class MyTool(BaseTool):
            name: ClassVar[str] = "my_tool"
            description: ClassVar[str] = "Does something useful"

            param1: str = Field(..., description="First parameter")
            param2: int = Field(10, description="Second parameter")

            def execute(self) -> str:
                return f"Result: {self.param1}, {self.param2}"
    """

    name: ClassVar[str] = "base_tool"
    description: ClassVar[str] = "Base tool class"

    class Config:
        arbitrary_types_allowed = True

    @property
    def context(self) -> ToolContext:
        """Access shared tool context."""
        return _tool_context

    @abstractmethod
    def execute(self) -> str:
        """Execute the tool and return result as string."""
        pass

    def run(self) -> str:
        """Alias for execute() for Agency Swarm compatibility."""
        return self.execute()

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Generate OpenAI function calling schema."""
        schema = cls.model_json_schema()

        properties = {}
        required = []

        # Helper function to clean schema recursively
        def clean_schema_property(prop):
            """Clean a property schema for OpenAI function calling."""
            cleaned = {}

            # Copy type
            if "type" in prop:
                cleaned["type"] = prop["type"]

            # Copy description
            if "description" in prop:
                cleaned["description"] = prop["description"]

            # Handle array items
            if prop.get("type") == "array" and "items" in prop:
                cleaned["items"] = clean_schema_property(prop["items"])

            # Handle object properties
            if "properties" in prop:
                cleaned["properties"] = {}
                for key, value in prop["properties"].items():
                    cleaned["properties"][key] = clean_schema_property(value)

            # Handle required fields
            if "required" in prop:
                cleaned["required"] = prop["required"]

            # Handle enum values
            if "enum" in prop:
                cleaned["enum"] = prop["enum"]

            # Handle allOf, anyOf, oneOf references
            if "$ref" in prop:
                # Resolve the reference from $defs
                ref_name = prop["$ref"].split("/")[-1]
                if "$defs" in schema and ref_name in schema["$defs"]:
                    return clean_schema_property(schema["$defs"][ref_name])

            # Handle minimum/maximum for numbers
            if "minimum" in prop:
                cleaned["minimum"] = prop["minimum"]
            if "maximum" in prop:
                cleaned["maximum"] = prop["maximum"]
            if "minLength" in prop:
                cleaned["minLength"] = prop["minLength"]
            if "maxLength" in prop:
                cleaned["maxLength"] = prop["maxLength"]

            return cleaned

        for prop_name, prop in schema.get("properties", {}).items():
            # Skip class variables
            if prop_name in ["name", "description"]:
                continue

            properties[prop_name] = clean_schema_property(prop)

            # Check if required (not in required list means it has a default)
            if prop_name in schema.get("required", []):
                required.append(prop_name)

        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }
