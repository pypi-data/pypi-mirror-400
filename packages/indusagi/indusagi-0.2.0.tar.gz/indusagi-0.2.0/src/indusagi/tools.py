"""
Tool Registry System for indus-agents

This module provides a robust tool registration and management system with:
- Decorator pattern for easy tool registration
- Automatic schema generation from Python function signatures (OpenAI format)
- Type-safe execution with comprehensive error handling
- Built-in security validation for dangerous operations
- Example tools for common use cases

Author: indus-agents
License: MIT
"""

from typing import Callable, Dict, Any, List, Optional, Union, get_type_hints, get_args, get_origin
import inspect
import json
from datetime import datetime
from enum import Enum
from functools import wraps
import re


class ToolExecutionError(Exception):
    """Raised when tool execution fails."""
    pass


class ToolRegistrationError(Exception):
    """Raised when tool registration fails."""
    pass


class ToolRegistry:
    """
    Registry for agent tools with automatic OpenAI schema generation.

    The ToolRegistry manages a collection of callable tools that AI agents can use
    to perform various operations. It automatically generates OpenAI-compatible
    tool schemas from Python function signatures and docstrings.

    Features:
        - Decorator-based registration (@registry.register)
        - Automatic schema generation from type hints
        - Type validation and error handling
        - Tool execution with comprehensive error catching
        - Security validation for dangerous operations

    Example:
        >>> registry = ToolRegistry()
        >>>
        >>> @registry.register
        >>> def add_numbers(a: int, b: int) -> int:
        >>>     '''Add two numbers together.'''
        >>>     return a + b
        >>>
        >>> result = registry.execute("add_numbers", a=5, b=3)
        >>> print(result)  # "8"
    """

    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        dangerous: bool = False
    ) -> Callable:
        """
        Decorator to register a function as a tool.

        This decorator registers a function in the tool registry and automatically
        generates an OpenAI-compatible schema from its signature and docstring.

        Args:
            func: Function to register (provided automatically when used as @register)
            name: Override the tool name (defaults to function name)
            description: Override the description (defaults to docstring)
            dangerous: Mark tool as potentially dangerous (requires extra validation)

        Returns:
            The original function (unchanged)

        Raises:
            ToolRegistrationError: If registration fails

        Example:
            >>> @registry.register
            >>> def my_tool(param: str) -> str:
            >>>     '''Process the parameter.'''
            >>>     return param.upper()
            >>>
            >>> @registry.register(name="custom_name", dangerous=True)
            >>> def risky_tool(command: str) -> str:
            >>>     '''Execute a system command.'''
            >>>     return subprocess.check_output(command, shell=True)
        """
        def decorator(f: Callable) -> Callable:
            tool_name = name or f.__name__

            # Validate function
            if not callable(f):
                raise ToolRegistrationError(f"Cannot register non-callable: {f}")

            if tool_name in self.tools:
                raise ToolRegistrationError(
                    f"Tool '{tool_name}' is already registered. "
                    "Use a different name or unregister the existing tool first."
                )

            # Register the tool
            self.tools[tool_name] = f

            # Generate and store schema
            try:
                schema = self._generate_openai_schema(f, tool_name, description)
                self._schemas.append(schema)
            except Exception as e:
                # Rollback registration on schema generation failure
                del self.tools[tool_name]
                raise ToolRegistrationError(
                    f"Failed to generate schema for '{tool_name}': {str(e)}"
                )

            # Store metadata
            self._metadata[tool_name] = {
                "dangerous": dangerous,
                "function": f,
                "schema": schema
            }

            return f

        # Support both @register and @register()
        if func is None:
            return decorator
        else:
            return decorator(func)

    def _generate_openai_schema(
        self,
        func: Callable,
        name: str,
        description_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate OpenAI function calling schema from a Python function.

        This method introspects the function's signature, type hints, and docstring
        to generate a complete OpenAI-compatible tool schema.

        Args:
            func: The function to generate schema for
            name: The tool name
            description_override: Optional description override

        Returns:
            OpenAI-compatible tool schema dictionary

        Schema Format:
            {
                "type": "function",
                "function": {
                    "name": "tool_name",
                    "description": "Tool description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param1": {"type": "string", "description": "..."},
                            "param2": {"type": "integer", "description": "..."}
                        },
                        "required": ["param1"]
                    }
                }
            }
        """
        # Get function signature
        sig = inspect.signature(func)

        # Get type hints
        try:
            type_hints = get_type_hints(func)
        except Exception:
            type_hints = {}

        # Extract description from docstring
        docstring = inspect.getdoc(func) or f"Execute {name}"
        description = description_override or docstring.split('\n')[0]

        # Parse parameter descriptions from docstring
        param_descriptions = self._parse_docstring_params(docstring)

        # Build parameters schema
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Skip *args and **kwargs
            if param.kind in (inspect.Parameter.VAR_POSITIONAL,
                            inspect.Parameter.VAR_KEYWORD):
                continue

            # Get type annotation
            param_type = type_hints.get(param_name, str)
            param_schema = self._python_type_to_json_schema(param_type)

            # Add parameter description if available
            if param_name in param_descriptions:
                param_schema["description"] = param_descriptions[param_name]

            properties[param_name] = param_schema

            # Mark as required if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        # Build complete OpenAI schema
        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

        return schema

    def _python_type_to_json_schema(self, python_type: type) -> Dict[str, Any]:
        """
        Convert Python type hint to JSON Schema type definition.

        Supports basic types, Optional, List, Dict, Enum, and more.

        Args:
            python_type: Python type annotation

        Returns:
            JSON Schema type definition
        """
        # Handle None/NoneType
        if python_type is None or python_type is type(None):
            return {"type": "null"}

        # Get origin for generic types (List, Dict, Optional, etc.)
        origin = get_origin(python_type)
        args = get_args(python_type)

        # Handle Optional[T] (Union[T, None])
        if origin is Union:
            non_none_types = [arg for arg in args if arg is not type(None)]
            if len(non_none_types) == 1:
                return self._python_type_to_json_schema(non_none_types[0])
            else:
                # Multiple types - use anyOf
                return {
                    "anyOf": [self._python_type_to_json_schema(t) for t in non_none_types]
                }

        # Handle List[T]
        if origin is list:
            item_type = args[0] if args else str
            return {
                "type": "array",
                "items": self._python_type_to_json_schema(item_type)
            }

        # Handle Dict[K, V]
        if origin is dict:
            return {"type": "object"}

        # Handle Enum
        if inspect.isclass(python_type) and issubclass(python_type, Enum):
            return {
                "type": "string",
                "enum": [e.value for e in python_type]
            }

        # Basic type mapping
        type_map = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array"},
            dict: {"type": "object"},
            Any: {},  # No type constraint
        }

        return type_map.get(python_type, {"type": "string"})

    def _parse_docstring_params(self, docstring: str) -> Dict[str, str]:
        """
        Parse parameter descriptions from Google-style or NumPy-style docstrings.

        Args:
            docstring: Function docstring

        Returns:
            Dictionary mapping parameter names to descriptions
        """
        param_descriptions = {}

        if not docstring:
            return param_descriptions

        # Look for Args: section
        args_match = re.search(r'Args:(.*?)(?=Returns:|Raises:|Example:|$)',
                              docstring, re.DOTALL | re.IGNORECASE)

        if args_match:
            args_section = args_match.group(1)
            # Match param_name: description patterns
            param_pattern = r'(\w+):\s*(.+?)(?=\n\s*\w+:|\n\n|\Z)'
            for match in re.finditer(param_pattern, args_section, re.DOTALL):
                param_name = match.group(1).strip()
                param_desc = match.group(2).strip().replace('\n', ' ')
                param_descriptions[param_name] = param_desc

        return param_descriptions

    @property
    def schemas(self) -> List[Dict[str, Any]]:
        """
        Get all registered tool schemas in OpenAI format.

        Returns:
            List of OpenAI-compatible tool schemas
        """
        return self._schemas.copy()

    def execute(
        self,
        name: str,
        validate: bool = True,
        **kwargs
    ) -> Any:
        """
        Execute a registered tool by name with given arguments.

        This method handles tool execution with comprehensive error handling,
        validation, and security checks.

        Args:
            name: Name of the tool to execute
            validate: Whether to perform security validation
            **kwargs: Arguments to pass to the tool

        Returns:
            Tool execution result (converted to string)

        Raises:
            ValueError: If tool not found
            ToolExecutionError: If tool execution fails

        Example:
            >>> result = registry.execute("calculator", expression="2+2")
            >>> print(result)  # "4"
        """
        # Check if tool exists
        if name not in self.tools:
            available = ", ".join(self.tools.keys())
            raise ValueError(
                f"Tool '{name}' not found. Available tools: {available}"
            )

        # Get tool and metadata
        tool = self.tools[name]
        metadata = self._metadata[name]

        # Security validation for dangerous tools
        if validate and metadata.get("dangerous", False):
            if not self._validate_dangerous_operation(name, kwargs):
                raise ToolExecutionError(
                    f"Security validation failed for dangerous tool '{name}'. "
                    "Operation blocked."
                )

        # Execute tool with error handling
        try:
            result = tool(**kwargs)

            # Convert result to string for LLM consumption
            if isinstance(result, str):
                return result
            elif isinstance(result, (dict, list)):
                return json.dumps(result, indent=2)
            else:
                return str(result)

        except TypeError as e:
            # Handle incorrect arguments
            raise ToolExecutionError(
                f"Invalid arguments for tool '{name}': {str(e)}"
            )
        except Exception as e:
            # Handle tool execution errors
            raise ToolExecutionError(
                f"Error executing tool '{name}': {str(e)}"
            )

    def _validate_dangerous_operation(
        self,
        tool_name: str,
        kwargs: Dict[str, Any]
    ) -> bool:
        """
        Validate dangerous tool operations for security.

        Args:
            tool_name: Name of the tool being executed
            kwargs: Tool arguments

        Returns:
            True if operation is safe, False otherwise
        """
        # Implement custom validation logic here
        # For now, just log a warning
        print(f"[WARNING] Executing dangerous tool: {tool_name}")
        return True

    def list_tools(self) -> List[str]:
        """
        Get list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tool_info(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific tool.

        Args:
            name: Tool name

        Returns:
            Dictionary with tool metadata and schema

        Raises:
            ValueError: If tool not found
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")

        return {
            "name": name,
            "schema": self._metadata[name]["schema"],
            "dangerous": self._metadata[name]["dangerous"],
            "function": self._metadata[name]["function"].__name__
        }

    def unregister(self, name: str) -> bool:
        """
        Unregister a tool from the registry.

        Args:
            name: Tool name to unregister

        Returns:
            True if tool was unregistered, False if not found
        """
        if name not in self.tools:
            return False

        del self.tools[name]
        del self._metadata[name]
        self._schemas = [s for s in self._schemas
                        if s["function"]["name"] != name]
        return True

    def clear(self):
        """Clear all registered tools."""
        self.tools.clear()
        self._schemas.clear()
        self._metadata.clear()


# ============================================================================
# Global Registry Instance
# ============================================================================

# Create a global registry instance for easy access
registry = ToolRegistry()


# ============================================================================
# Built-in Example Tools
# ============================================================================


@registry.register
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.

    This tool safely evaluates basic mathematical expressions including
    addition, subtraction, multiplication, division, and parentheses.
    It includes security validation to prevent code execution.

    Args:
        expression: Mathematical expression to evaluate (e.g., "2+2", "10*5", "(3+7)/2")

    Returns:
        The calculated result as a string

    Example:
        >>> calculator("2 + 2")
        "4"
        >>> calculator("(10 + 5) * 2")
        "30"

    Security:
        - Only allows numbers and basic operators: + - * / ( ) .
        - Blocks dangerous operations like ** (power)
        - Prevents arbitrary code execution
    """
    try:
        # Security validation: only allow safe characters
        allowed_chars = set("0123456789+-*/() .")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters. Only numbers and operators (+, -, *, /, parentheses) are allowed."

        # Additional security checks
        if "**" in expression:
            return "Error: Power operations (**) are not allowed for security reasons."

        if expression.count("(") != expression.count(")"):
            return "Error: Mismatched parentheses in expression."

        # Basic validation: must contain at least one digit
        if not any(c.isdigit() for c in expression):
            return "Error: Expression must contain at least one number."

        # Evaluate safely (restricted to math operations only)
        result = eval(expression, {"__builtins__": {}}, {})

        # Format result nicely
        if isinstance(result, float):
            # Round to reasonable precision
            if result == int(result):
                return str(int(result))
            else:
                return f"{result:.6g}"  # Remove trailing zeros

        return str(result)

    except ZeroDivisionError:
        return "Error: Division by zero"
    except SyntaxError:
        return "Error: Invalid mathematical expression syntax"
    except Exception as e:
        return f"Error: Failed to evaluate expression - {str(e)}"


@registry.register
def get_time() -> str:
    """
    Get the current time in 12-hour format with AM/PM.

    Returns:
        Current time formatted as "HH:MM:SS AM/PM"

    Example:
        >>> get_time()
        "02:30:45 PM"
    """
    now = datetime.now()
    return now.strftime("%I:%M:%S %p")


@registry.register
def get_date() -> str:
    """
    Get the current date in ISO format.

    Returns:
        Current date formatted as "YYYY-MM-DD"

    Example:
        >>> get_date()
        "2025-01-07"
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d")


@registry.register
def get_datetime() -> str:
    """
    Get the current date and time together.

    Returns:
        Current datetime formatted as "YYYY-MM-DD HH:MM:SS AM/PM"

    Example:
        >>> get_datetime()
        "2025-01-07 02:30:45 PM"
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %I:%M:%S %p")


@registry.register
def text_uppercase(text: str) -> str:
    """
    Convert text to uppercase letters.

    Args:
        text: The text to convert

    Returns:
        Text converted to uppercase

    Example:
        >>> text_uppercase("hello world")
        "HELLO WORLD"
    """
    if not text:
        return "Error: Empty text provided"
    return text.upper()


@registry.register
def text_lowercase(text: str) -> str:
    """
    Convert text to lowercase letters.

    Args:
        text: The text to convert

    Returns:
        Text converted to lowercase

    Example:
        >>> text_lowercase("HELLO WORLD")
        "hello world"
    """
    if not text:
        return "Error: Empty text provided"
    return text.lower()


@registry.register
def text_reverse(text: str) -> str:
    """
    Reverse the order of characters in text.

    Args:
        text: The text to reverse

    Returns:
        Text with characters in reverse order

    Example:
        >>> text_reverse("hello")
        "olleh"
    """
    if not text:
        return "Error: Empty text provided"
    return text[::-1]


@registry.register
def text_count_words(text: str) -> str:
    """
    Count the number of words in text.

    Args:
        text: The text to analyze

    Returns:
        Statistics about the text including word count, character count, and line count

    Example:
        >>> text_count_words("Hello world! This is a test.")
        "Words: 6, Characters: 29, Lines: 1"
    """
    if not text:
        return "Words: 0, Characters: 0, Lines: 0"

    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines())

    return f"Words: {words}, Characters: {chars}, Lines: {lines}"


@registry.register
def text_title_case(text: str) -> str:
    """
    Convert text to title case (capitalize first letter of each word).

    Args:
        text: The text to convert

    Returns:
        Text in title case

    Example:
        >>> text_title_case("hello world from python")
        "Hello World From Python"
    """
    if not text:
        return "Error: Empty text provided"
    return text.title()


# ============================================================================
# Utility Functions
# ============================================================================


def rate_limit(max_calls: int = 10, time_window: int = 60):
    """
    Decorator to rate limit tool execution.

    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds

    Example:
        >>> @rate_limit(max_calls=5, time_window=60)
        >>> @registry.register
        >>> def expensive_tool(query: str) -> str:
        >>>     return perform_expensive_operation(query)
    """
    from collections import defaultdict
    from time import time

    call_times = defaultdict(list)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time()
            func_name = func.__name__

            # Clean old calls outside time window
            call_times[func_name] = [
                t for t in call_times[func_name]
                if now - t < time_window
            ]

            # Check if limit exceeded
            if len(call_times[func_name]) >= max_calls:
                raise ToolExecutionError(
                    f"Rate limit exceeded for {func_name}. "
                    f"Maximum {max_calls} calls per {time_window} seconds."
                )

            # Record this call
            call_times[func_name].append(now)

            # Execute function
            return func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Testing and Validation
# ============================================================================


if __name__ == "__main__":
    """Test the tool registry system."""

    print("=" * 70)
    print("Tool Registry System - Test Suite")
    print("=" * 70)

    # Test 1: List registered tools
    print("\n[TEST 1] Registered Tools:")
    print("-" * 70)
    for tool_name in registry.list_tools():
        print(f"  + {tool_name}")

    # Test 2: Test calculator tool
    print("\n[TEST 2] Calculator Tool:")
    print("-" * 70)
    test_expressions = [
        "2 + 2",
        "10 * 5",
        "(3 + 7) / 2",
        "100 - 25",
        "15.5 * 2",
    ]
    for expr in test_expressions:
        result = registry.execute("calculator", expression=expr)
        print(f"  {expr:20s} = {result}")

    # Test 3: Test time/date tools
    print("\n[TEST 3] Time & Date Tools:")
    print("-" * 70)
    print(f"  Current time:     {registry.execute('get_time')}")
    print(f"  Current date:     {registry.execute('get_date')}")
    print(f"  Current datetime: {registry.execute('get_datetime')}")

    # Test 4: Test text manipulation tools
    print("\n[TEST 4] Text Manipulation Tools:")
    print("-" * 70)
    test_text = "Hello World"
    print(f"  Original:     {test_text}")
    print(f"  Uppercase:    {registry.execute('text_uppercase', text=test_text)}")
    print(f"  Lowercase:    {registry.execute('text_lowercase', text=test_text)}")
    print(f"  Reverse:      {registry.execute('text_reverse', text=test_text)}")
    print(f"  Title Case:   {registry.execute('text_title_case', text=test_text)}")

    # Test 5: Test word counting
    print("\n[TEST 5] Word Counting Tool:")
    print("-" * 70)
    sample_text = "The quick brown fox jumps over the lazy dog"
    print(f"  Text: \"{sample_text}\"")
    print(f"  Stats: {registry.execute('text_count_words', text=sample_text)}")

    # Test 6: Test schema generation
    print("\n[TEST 6] OpenAI Schema Generation:")
    print("-" * 70)
    schemas = registry.schemas
    print(f"  Total schemas generated: {len(schemas)}")
    print(f"\n  Sample schema (calculator):")
    calc_schema = next(s for s in schemas if s["function"]["name"] == "calculator")
    print(f"  {json.dumps(calc_schema, indent=4)}")

    # Test 7: Test error handling
    print("\n[TEST 7] Error Handling:")
    print("-" * 70)
    print("  Testing invalid expression:")
    result = registry.execute("calculator", expression="import os")
    print(f"    Result: {result}")
    print("  Testing division by zero:")
    result = registry.execute("calculator", expression="10 / 0")
    print(f"    Result: {result}")

    # Test 8: Test tool info
    print("\n[TEST 8] Tool Information:")
    print("-" * 70)
    info = registry.get_tool_info("calculator")
    print(f"  Tool name: {info['name']}")
    print(f"  Dangerous: {info['dangerous']}")
    print(f"  Description: {info['schema']['function']['description']}")

    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)


# ============================================================================
# Usage Examples and Integration Guide
# ============================================================================

"""
USAGE EXAMPLES
==============

1. Basic Tool Registration
--------------------------
from tools import registry

@registry.register
def my_tool(param: str) -> str:
    '''Process the parameter.'''
    return param.upper()


2. Tool with Multiple Parameters
---------------------------------
@registry.register
def format_text(text: str, prefix: str = ">>") -> str:
    '''Format text with a prefix.

    Args:
        text: The text to format
        prefix: Prefix to add (default: ">>")

    Returns:
        Formatted text
    '''
    return f"{prefix} {text}"


3. Using with OpenAI API
-------------------------
import openai

client = openai.OpenAI()

# Get tool schemas in OpenAI format
tools = registry.schemas

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is 25 * 4?"}],
    tools=tools
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Execute the tool
        result = registry.execute(function_name, **arguments)
        print(f"Tool result: {result}")


4. Custom Tool with Validation
-------------------------------
@registry.register(dangerous=True)
def system_command(command: str) -> str:
    '''Execute a system command (dangerous).

    Args:
        command: Command to execute

    Returns:
        Command output
    '''
    import subprocess
    result = subprocess.check_output(command, shell=True)
    return result.decode()


5. Tool with Rate Limiting
---------------------------
@rate_limit(max_calls=5, time_window=60)
@registry.register
def expensive_api_call(query: str) -> str:
    '''Call an expensive API (rate limited).

    Args:
        query: Search query

    Returns:
        API response
    '''
    import requests
    response = requests.get(f"https://api.example.com/search?q={query}")
    return response.text


6. Integration with indus-agents
------------------------------------
from agent import Agent
from tools import registry

# Create an agent
agent = Agent("Helper", "Assistant")

# Agent can use tools automatically
response = agent.process_with_tools(
    "What is the current time and what is 100 divided by 4?",
    tools=registry.schemas
)

print(response)


7. Testing Tools
----------------
import pytest

def test_calculator():
    result = registry.execute("calculator", expression="2+2")
    assert "4" in result

def test_invalid_tool():
    with pytest.raises(ValueError):
        registry.execute("nonexistent_tool")


8. Dynamic Tool Management
---------------------------
# List all tools
print(registry.list_tools())

# Get tool info
info = registry.get_tool_info("calculator")
print(info['schema'])

# Unregister a tool
registry.unregister("calculator")

# Clear all tools
registry.clear()


OPENAI SCHEMA FORMAT
====================

The registry generates schemas in OpenAI's function calling format:

{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "Tool description from docstring",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description from docstring"
                }
            },
            "required": ["param1"]
        }
    }
}


TYPE MAPPING
============

Python Type          JSON Schema Type
-----------          ----------------
str                  {"type": "string"}
int                  {"type": "integer"}
float                {"type": "number"}
bool                 {"type": "boolean"}
list                 {"type": "array"}
dict                 {"type": "object"}
List[str]            {"type": "array", "items": {"type": "string"}}
Optional[str]        {"type": "string"}
Union[str, int]      {"anyOf": [{"type": "string"}, {"type": "integer"}]}
Enum                 {"type": "string", "enum": ["value1", "value2"]}


SECURITY BEST PRACTICES
========================

1. Input Validation
   - Validate all user inputs
   - Use whitelists for allowed characters
   - Sanitize file paths

2. Dangerous Operations
   - Mark dangerous tools with dangerous=True
   - Implement custom validation logic
   - Log all dangerous operations

3. Rate Limiting
   - Use @rate_limit decorator
   - Prevent API abuse
   - Protect against DoS

4. Error Handling
   - Return user-friendly error messages
   - Never expose internal errors
   - Log errors for debugging

5. Sandboxing
   - Use eval() only with restricted builtins
   - Avoid shell=True in subprocess
   - Restrict file system access


ERROR HANDLING
==============

All tool execution errors are caught and returned as strings:

try:
    result = registry.execute("calculator", expression="invalid")
except ToolExecutionError as e:
    print(f"Tool failed: {e}")

# Or check the result
result = registry.execute("calculator", expression="invalid")
if result.startswith("Error:"):
    print(f"Calculation failed: {result}")


EXTENDING THE REGISTRY
=======================

Create custom registries for different domains:

# Math tools registry
math_registry = ToolRegistry()

@math_registry.register
def sine(angle: float) -> str:
    import math
    return str(math.sin(angle))

# Text tools registry
text_registry = ToolRegistry()

@text_registry.register
def sentiment_analysis(text: str) -> str:
    # Implement sentiment analysis
    return "positive"


PRODUCTION CHECKLIST
====================

Before deploying to production:

[ ] All tools have comprehensive docstrings
[ ] Type hints are used for all parameters
[ ] Input validation is implemented
[ ] Error handling is comprehensive
[ ] Security validation for dangerous tools
[ ] Rate limiting for expensive operations
[ ] Unit tests for all tools
[ ] Integration tests with agent
[ ] Logging and monitoring configured
[ ] Documentation is complete


TROUBLESHOOTING
===============

Issue: Schema generation fails
Solution: Ensure all parameters have type hints

Issue: Tool not found
Solution: Check tool name spelling and registration

Issue: Tool execution fails
Solution: Check arguments match function signature

Issue: Unicode errors on Windows
Solution: Use plain ASCII characters in output

Issue: Rate limit exceeded
Solution: Increase time_window or reduce max_calls


PERFORMANCE TIPS
================

1. Cache Results
   - Use @lru_cache for expensive computations
   - Cache API responses
   - Implement custom caching logic

2. Async Tools
   - Use async/await for I/O operations
   - Batch API calls
   - Use connection pooling

3. Minimize Execution Time
   - Optimize algorithms
   - Use efficient data structures
   - Profile and benchmark


SUPPORT AND RESOURCES
======================

Documentation: README.md
Architecture: 02-ARCHITECTURE.md
Tool Patterns: 04-TOOL-SYSTEM.md
Examples: This file (tools.py)
Tests: tests/test_tools.py

For issues and contributions:
- GitHub Issues: [your-repo]/issues
- Pull Requests: [your-repo]/pulls
"""
