# Tool Registry Quick Reference Card

## Import
```python
from tools import registry
```

## Register a Tool
```python
@registry.register
def my_tool(param: str) -> str:
    """Tool description."""
    return result
```

## Execute a Tool
```python
result = registry.execute("tool_name", param="value")
```

## Get All Schemas (for OpenAI)
```python
tools = registry.schemas
```

## List Tools
```python
tools = registry.list_tools()
```

## OpenAI Integration (Complete Example)
```python
import openai
import json
from tools import registry

client = openai.OpenAI()

# 1. Get schemas
tools = registry.schemas

# 2. Make request
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "What is 25 * 4?"}],
    tools=tools
)

# 3. Handle tool calls
if response.choices[0].message.tool_calls:
    for call in response.choices[0].message.tool_calls:
        result = registry.execute(
            call.function.name,
            **json.loads(call.function.arguments)
        )
        print(f"Result: {result}")
```

## Built-in Tools

| Tool | Description | Example |
|------|-------------|---------|
| `calculator` | Evaluate math expressions | `calculator(expression="2+2")` |
| `get_time` | Get current time | `get_time()` |
| `get_date` | Get current date | `get_date()` |
| `get_datetime` | Get date and time | `get_datetime()` |
| `text_uppercase` | Convert to uppercase | `text_uppercase(text="hello")` |
| `text_lowercase` | Convert to lowercase | `text_lowercase(text="HELLO")` |
| `text_reverse` | Reverse text | `text_reverse(text="hello")` |
| `text_count_words` | Count words/chars | `text_count_words(text="...")` |
| `text_title_case` | Title case | `text_title_case(text="hello")` |

## Advanced Features

### Dangerous Tools
```python
@registry.register(dangerous=True)
def risky_tool(param: str) -> str:
    """This tool is marked as dangerous."""
    return result
```

### Rate Limiting
```python
@rate_limit(max_calls=5, time_window=60)
@registry.register
def limited_tool(query: str) -> str:
    """Rate limited to 5 calls/minute."""
    return result
```

### Custom Name
```python
@registry.register(name="custom_name")
def my_function(param: str) -> str:
    """Uses custom_name instead of my_function."""
    return result
```

## Type Hints Supported

```python
str, int, float, bool, list, dict
List[T], Dict[K,V], Optional[T], Union[A,B]
Enum (auto-converted to enum values)
```

## Error Handling

```python
try:
    result = registry.execute("tool_name", param="value")
except ValueError:
    print("Tool not found")
except ToolExecutionError as e:
    print(f"Tool failed: {e}")
```

## Testing

Run comprehensive tests:
```bash
python tools.py
```

Run OpenAI integration demo:
```bash
python test_openai_integration.py
```

## Common Patterns

### Tool with Optional Parameters
```python
@registry.register
def format_text(text: str, uppercase: bool = False) -> str:
    """Optional parameters with defaults."""
    return text.upper() if uppercase else text
```

### Tool Returning JSON
```python
@registry.register
def search_data(query: str) -> str:
    """Returns JSON string."""
    results = [{"id": 1, "name": "Item"}]
    return json.dumps(results)
```

### Tool with Validation
```python
@registry.register
def validate_email(email: str) -> str:
    """Validate and return result."""
    if "@" not in email:
        return "Error: Invalid email"
    return f"Valid email: {email}"
```

## Schema Format (OpenAI)

```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "Tool description",
    "parameters": {
      "type": "object",
      "properties": {
        "param": {"type": "string", "description": "..."}
      },
      "required": ["param"]
    }
  }
}
```

## Tips

1. **Always use type hints** - Required for schema generation
2. **Write clear docstrings** - Used as tool descriptions
3. **Validate inputs** - Check parameters before processing
4. **Return strings** - LLMs work best with string results
5. **Handle errors gracefully** - Return error messages, don't raise
6. **Test tools independently** - Use `registry.execute()` directly
7. **Mark dangerous tools** - Use `dangerous=True` flag
8. **Document parameters** - Use Args: section in docstring

## Files

- **tools.py** - Main implementation (1,177 lines)
- **test_openai_integration.py** - Integration demo (116 lines)
- **TOOLS_IMPLEMENTATION_SUMMARY.md** - Full documentation (340 lines)
