# Tool Schema Format Comparison: OpenAI vs Anthropic

## Overview

This document shows the differences between OpenAI's and Anthropic's tool schema formats, and how to adapt the registry for both.

---

## OpenAI Format (Current Implementation)

### Schema Structure
```json
{
  "type": "function",
  "function": {
    "name": "calculator",
    "description": "Evaluate a mathematical expression",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {
          "type": "string",
          "description": "Mathematical expression to evaluate"
        }
      },
      "required": ["expression"]
    }
  }
}
```

### API Usage
```python
import openai

client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    tools=tools  # OpenAI format schemas
)

# Handle tool calls
for tool_call in response.choices[0].message.tool_calls:
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    result = registry.execute(function_name, **arguments)
```

---

## Anthropic Format

### Schema Structure
```json
{
  "name": "calculator",
  "description": "Evaluate a mathematical expression",
  "input_schema": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "Mathematical expression to evaluate"
      }
    },
    "required": ["expression"]
  }
}
```

### API Usage
```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is 2+2?"}],
    tools=tools  # Anthropic format schemas
)

# Handle tool calls
for content in response.content:
    if content.type == "tool_use":
        result = registry.execute(content.name, **content.input)
```

---

## Key Differences

| Aspect | OpenAI | Anthropic |
|--------|--------|-----------|
| **Root Structure** | `{"type": "function", "function": {...}}` | Flat: `{"name": ..., "input_schema": ...}` |
| **Parameters Key** | `parameters` | `input_schema` |
| **Nesting** | Nested under "function" | Top-level |
| **Type Field** | Has "type": "function" | No type field |
| **Properties** | In `function.parameters.properties` | In `input_schema.properties` |

---

## Adapter Pattern for Dual Support

### Method 1: Converter Function
```python
def openai_to_anthropic(openai_schema):
    """Convert OpenAI schema to Anthropic format."""
    return {
        "name": openai_schema["function"]["name"],
        "description": openai_schema["function"]["description"],
        "input_schema": openai_schema["function"]["parameters"]
    }

def anthropic_to_openai(anthropic_schema):
    """Convert Anthropic schema to OpenAI format."""
    return {
        "type": "function",
        "function": {
            "name": anthropic_schema["name"],
            "description": anthropic_schema["description"],
            "parameters": anthropic_schema["input_schema"]
        }
    }
```

### Method 2: Dual Schema Generation
```python
class ToolRegistry:
    def _generate_openai_schema(self, func, name, description):
        """Current implementation."""
        # ... existing code ...

    def _generate_anthropic_schema(self, func, name, description):
        """Generate Anthropic format schema."""
        openai_schema = self._generate_openai_schema(func, name, description)
        return {
            "name": openai_schema["function"]["name"],
            "description": openai_schema["function"]["description"],
            "input_schema": openai_schema["function"]["parameters"]
        }

    @property
    def openai_schemas(self):
        """Get schemas in OpenAI format."""
        return self._schemas

    @property
    def anthropic_schemas(self):
        """Get schemas in Anthropic format."""
        return [self._convert_to_anthropic(s) for s in self._schemas]
```

### Method 3: Format Parameter
```python
@property
def schemas(self, format="openai"):
    """Get schemas in specified format.

    Args:
        format: "openai" or "anthropic"
    """
    if format == "anthropic":
        return [self._to_anthropic(s) for s in self._schemas]
    return self._schemas
```

---

## Usage Examples

### Using OpenAI Format (Current)
```python
from tools import registry

# Works out of the box
tools = registry.schemas

response = openai_client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[...],
    tools=tools
)
```

### Converting to Anthropic Format
```python
from tools import registry

# Convert schemas
anthropic_tools = [
    {
        "name": s["function"]["name"],
        "description": s["function"]["description"],
        "input_schema": s["function"]["parameters"]
    }
    for s in registry.schemas
]

response = anthropic_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[...],
    tools=anthropic_tools
)
```

### Universal Adapter Class
```python
class SchemaAdapter:
    """Adapter for converting between schema formats."""

    @staticmethod
    def to_openai(schema):
        """Convert any format to OpenAI."""
        if "function" in schema:
            return schema  # Already OpenAI format

        return {
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema["input_schema"]
            }
        }

    @staticmethod
    def to_anthropic(schema):
        """Convert any format to Anthropic."""
        if "input_schema" in schema:
            return schema  # Already Anthropic format

        return {
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
            "input_schema": schema["function"]["parameters"]
        }

# Usage
adapter = SchemaAdapter()
openai_schemas = [adapter.to_openai(s) for s in schemas]
anthropic_schemas = [adapter.to_anthropic(s) for s in schemas]
```

---

## Complete Example: Supporting Both APIs

```python
from tools import registry
import openai
from anthropic import Anthropic

class UniversalAgent:
    """Agent that works with both OpenAI and Anthropic."""

    def __init__(self, provider="openai"):
        self.provider = provider
        self.registry = registry

        if provider == "openai":
            self.client = openai.OpenAI()
            self.schemas = registry.schemas
        else:
            self.client = Anthropic()
            self.schemas = self._convert_to_anthropic(registry.schemas)

    def _convert_to_anthropic(self, openai_schemas):
        """Convert OpenAI schemas to Anthropic format."""
        return [
            {
                "name": s["function"]["name"],
                "description": s["function"]["description"],
                "input_schema": s["function"]["parameters"]
            }
            for s in openai_schemas
        ]

    def process(self, prompt):
        """Process prompt with appropriate API."""
        if self.provider == "openai":
            return self._process_openai(prompt)
        else:
            return self._process_anthropic(prompt)

    def _process_openai(self, prompt):
        """Handle OpenAI API call."""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            tools=self.schemas
        )

        message = response.choices[0].message
        if message.tool_calls:
            for tool_call in message.tool_calls:
                result = self.registry.execute(
                    tool_call.function.name,
                    **json.loads(tool_call.function.arguments)
                )
                return result

        return message.content

    def _process_anthropic(self, prompt):
        """Handle Anthropic API call."""
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            tools=self.schemas
        )

        for content in response.content:
            if content.type == "tool_use":
                result = self.registry.execute(
                    content.name,
                    **content.input
                )
                return result

        return response.content[0].text

# Usage
openai_agent = UniversalAgent(provider="openai")
anthropic_agent = UniversalAgent(provider="anthropic")

# Both work the same way
result1 = openai_agent.process("What is 2+2?")
result2 = anthropic_agent.process("What is 2+2?")
```

---

## Recommendation

**For this implementation**: Keep OpenAI format as primary since:
1. It's the industry standard
2. Most compatible with various LLM providers
3. Easy to convert to Anthropic format when needed
4. Cleaner separation of concerns with nested structure

**For future**: Add a simple converter utility when Anthropic support is needed:

```python
# Add to tools.py
def get_anthropic_schemas():
    """Get schemas in Anthropic format for Claude integration."""
    return [
        {
            "name": s["function"]["name"],
            "description": s["function"]["description"],
            "input_schema": s["function"]["parameters"]
        }
        for s in registry.schemas
    ]
```

---

## Testing Both Formats

```python
def test_schema_conversion():
    """Test schema conversion between formats."""
    # Original OpenAI schema
    openai_schema = registry.schemas[0]

    # Convert to Anthropic
    anthropic_schema = {
        "name": openai_schema["function"]["name"],
        "description": openai_schema["function"]["description"],
        "input_schema": openai_schema["function"]["parameters"]
    }

    # Verify structure
    assert "name" in anthropic_schema
    assert "input_schema" in anthropic_schema
    assert anthropic_schema["name"] == openai_schema["function"]["name"]

    print("Schema conversion test passed!")

test_schema_conversion()
```

---

## Summary

- **Current Implementation**: OpenAI format ✓
- **Conversion**: Simple one-liner for Anthropic
- **Both Supported**: Via adapter pattern
- **Future-Proof**: Easy to extend to other formats

The OpenAI format is more widely adopted and easier to convert to other formats when needed.
