# How to Create Custom Tools for indus-agents

This guide shows you how to create your own custom tools that agents can use automatically.

---

## Quick Start (3 Steps)

### Step 1: Create Your Tool Function

```python
from indusagi import registry

@registry.register
def my_tool(param: str) -> str:
    """Description of what your tool does."""
    # Your tool logic here
    return f"Processed: {param}"
```

### Step 2: Import Your Tool

```python
import custom_tools  # This auto-registers all tools!
```

### Step 3: Use It!

```python
from indusagi import Agent

agent = Agent("MyAgent", "Helpful assistant")
response = agent.process_with_tools("Use my_tool with value 'test'")
```

That's it! The agent will automatically discover and use your tool.

---

## Complete Guide

### 1. Tool Function Requirements

Your tool function MUST have:
- ✅ **Type hints** for all parameters
- ✅ **Docstring** describing what it does
- ✅ **Return type** annotation
- ✅ **Clear parameter descriptions** (in docstring)

### 2. Example: Simple Tool

```python
from indusagi import registry

@registry.register
def add_numbers(a: int, b: int) -> str:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of the two numbers
    """
    result = a + b
    return f"The sum of {a} and {b} is {result}"
```

**What happens:**
1. `@registry.register` decorator registers the tool
2. Type hints (`int`, `str`) define parameter types
3. Docstring provides description for the AI
4. Function logic implements the tool behavior

### 3. Example: Tool with Optional Parameters

```python
@registry.register
def greet_user(name: str, language: str = "english") -> str:
    """
    Greet a user in different languages.

    Args:
        name: Name of the person to greet
        language: Language to use (english, spanish, french)

    Returns:
        Greeting message
    """
    greetings = {
        "english": f"Hello, {name}!",
        "spanish": f"Hola, {name}!",
        "french": f"Bonjour, {name}!"
    }

    return greetings.get(language.lower(), greetings["english"])
```

**Key points:**
- `language: str = "english"` makes it optional
- Agent can call with or without the parameter
- Default value is used if not provided

### 4. Supported Parameter Types

The framework automatically converts these Python types to OpenAI schemas:

| Python Type | JSON Schema Type | Example |
|-------------|------------------|---------|
| `str` | `string` | `"hello"` |
| `int` | `integer` | `42` |
| `float` | `number` | `3.14` |
| `bool` | `boolean` | `true` |
| `List[str]` | `array` | `["a", "b"]` |
| `Dict[str, Any]` | `object` | `{"key": "value"}` |
| `Optional[str]` | `string` (nullable) | `"hello"` or `null` |

### 5. Example: Tool with Complex Types

```python
from typing import Optional, List

@registry.register
def find_max(numbers: str, return_index: bool = False) -> str:
    """
    Find the maximum number in a list.

    Args:
        numbers: Comma-separated numbers (e.g., "1,5,3,9,2")
        return_index: Whether to return the index of max value

    Returns:
        Maximum value and optionally its index
    """
    num_list = [float(n.strip()) for n in numbers.split(",")]
    max_value = max(num_list)

    if return_index:
        max_index = num_list.index(max_value)
        return f"Max: {max_value} at index {max_index}"

    return f"Max: {max_value}"
```

### 6. Tool Organization

**Option A: Single File (Recommended for small projects)**

Create `custom_tools.py`:

```python
from indusagi import registry

@registry.register
def tool1(param: str) -> str:
    """Tool 1 description."""
    return param

@registry.register
def tool2(param: int) -> str:
    """Tool 2 description."""
    return str(param * 2)
```

Then import:
```python
import custom_tools  # Registers all tools!
```

**Option B: Multiple Files (Recommended for large projects)**

Create `tools/` directory:
```
tools/
├── __init__.py
├── weather_tools.py
├── file_tools.py
└── math_tools.py
```

`tools/__init__.py`:
```python
from . import weather_tools
from . import file_tools
from . import math_tools
```

Then import:
```python
import tools  # Registers all tools from all files!
```

### 7. Error Handling in Tools

**Good practice:**

```python
@registry.register
def divide_numbers(a: float, b: float) -> str:
    """
    Divide two numbers.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Result of division or error message
    """
    if b == 0:
        return "Error: Cannot divide by zero"

    result = a / b
    return f"{a} divided by {b} equals {result}"
```

**Key points:**
- Return error messages as strings (don't raise exceptions)
- Agent can understand and relay error messages to users
- Use clear, descriptive error messages

### 8. Security Best Practices

**Dangerous operations:** Mark tools that perform risky actions

```python
@registry.register(dangerous=True)
def delete_file(filename: str) -> str:
    """Delete a file (dangerous operation)."""
    # Add validation
    if not filename.endswith('.txt'):
        return "Error: Only .txt files can be deleted"

    # Additional safety checks
    if not os.path.exists(filename):
        return "Error: File not found"

    os.remove(filename)
    return f"Deleted: {filename}"
```

**Security checklist:**
- ✅ Validate all inputs
- ✅ Limit file system access
- ✅ Avoid executing arbitrary code
- ✅ Use `dangerous=True` flag for risky operations
- ✅ Return errors instead of raising exceptions

### 9. Testing Your Custom Tools

**Method 1: Direct execution**

```python
from indusagi import registry
import custom_tools  # Register your tools

# Test directly
result = registry.execute("my_tool", param="test")
print(result)
```

**Method 2: With agent**

```python
from indusagi import Agent
import custom_tools

agent = Agent("TestAgent", "Test assistant")
response = agent.process_with_tools("Use my_tool with value 'test'")
print(response)
```

**Method 3: Verification**

```python
# Check if tool is registered
all_tools = registry.list_tools()
print("my_tool" in all_tools)  # Should print True

# Get tool schema
schemas = registry.schemas
print(schemas)  # See OpenAI schema for your tool
```

### 10. Complete Example: Real-World Tool

```python
from indusagi import registry
from datetime import datetime
import re

@registry.register
def validate_email(email: str) -> str:
    """
    Validate an email address format.

    Args:
        email: Email address to validate

    Returns:
        Validation result with details
    """
    # Simple email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(pattern, email):
        # Extract domain
        domain = email.split('@')[1]
        return f"Valid email: {email} (domain: {domain})"
    else:
        return f"Invalid email: {email} does not match email format"
```

**Usage:**
```python
import custom_tools
from indusagi import Agent

agent = Agent("EmailBot", "Email validation assistant")
response = agent.process_with_tools("Is test@example.com a valid email?")
# Agent will use validate_email tool and respond
```

---

## Full Workflow Example

### 1. Create `my_custom_tools.py`

```python
from indusagi import registry
import random

@registry.register
def roll_dice(sides: int = 6, count: int = 1) -> str:
    """
    Roll one or more dice.

    Args:
        sides: Number of sides on each die (default: 6)
        count: Number of dice to roll (default: 1)

    Returns:
        Results of dice rolls
    """
    if sides < 2:
        return "Error: Dice must have at least 2 sides"

    if count < 1:
        return "Error: Must roll at least 1 die"

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)

    if count == 1:
        return f"Rolled 1d{sides}: {rolls[0]}"

    return f"Rolled {count}d{sides}: {rolls} (total: {total})"

@registry.register
def flip_coin(count: int = 1) -> str:
    """
    Flip one or more coins.

    Args:
        count: Number of coins to flip (default: 1)

    Returns:
        Results of coin flips
    """
    if count < 1:
        return "Error: Must flip at least 1 coin"

    flips = [random.choice(["Heads", "Tails"]) for _ in range(count)]

    if count == 1:
        return f"Coin flip: {flips[0]}"

    heads = flips.count("Heads")
    tails = flips.count("Tails")
    return f"Flipped {count} coins: {heads} Heads, {tails} Tails. Results: {flips}"
```

### 2. Create `test_my_tools.py`

```python
from indusagi import Agent
import my_custom_tools  # Auto-registers the tools!

# Create agent
agent = Agent("GameMaster", "Assistant for games and random events")

# Test queries
queries = [
    "Roll 2 dice",
    "Roll a 20-sided die",
    "Flip 5 coins and tell me the results",
    "Roll 3 six-sided dice and flip 1 coin"
]

for query in queries:
    print(f"\nQuery: {query}")
    response = agent.process_with_tools(query)
    print(f"Response: {response}")
```

### 3. Run It!

```bash
python test_my_tools.py
```

**Expected output:**
```
Query: Roll 2 dice
Response: Rolled 2d6: [4, 3] (total: 7)

Query: Roll a 20-sided die
Response: Rolled 1d20: 15

Query: Flip 5 coins and tell me the results
Response: Flipped 5 coins: 3 Heads, 2 Tails. Results: ['Heads', 'Tails', 'Heads', 'Heads', 'Tails']
```

---

## Advanced Features

### Custom Tool Names

```python
@registry.register(name="custom_name")
def my_function(param: str) -> str:
    """Tool with custom name."""
    return param
```

### Custom Descriptions

```python
@registry.register(description="Custom description for AI")
def my_tool(param: str) -> str:
    """Original docstring."""
    return param
```

### Dangerous Tools

```python
@registry.register(dangerous=True)
def risky_operation(param: str) -> str:
    """Potentially dangerous operation."""
    # Extra validation will be performed
    return param
```

---

## Common Patterns

### Pattern 1: API Wrapper Tool

```python
@registry.register
def get_quote() -> str:
    """Get a random inspirational quote."""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs"
    ]
    return random.choice(quotes)
```

### Pattern 2: Data Transformation Tool

```python
@registry.register
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert temperature between Celsius and Fahrenheit.

    Args:
        value: Temperature value
        from_unit: Source unit (celsius or fahrenheit)
        to_unit: Target unit (celsius or fahrenheit)

    Returns:
        Converted temperature
    """
    if from_unit.lower() == "celsius" and to_unit.lower() == "fahrenheit":
        result = (value * 9/5) + 32
        return f"{value}°C = {result}°F"

    elif from_unit.lower() == "fahrenheit" and to_unit.lower() == "celsius":
        result = (value - 32) * 5/9
        return f"{value}°F = {result}°C"

    return f"Error: Unsupported conversion {from_unit} to {to_unit}"
```

### Pattern 3: Stateful Tool

```python
# Store state outside the tool function
_counter = {"value": 0}

@registry.register
def increment_counter(amount: int = 1) -> str:
    """
    Increment a counter.

    Args:
        amount: Amount to increment (default: 1)

    Returns:
        New counter value
    """
    _counter["value"] += amount
    return f"Counter: {_counter['value']}"

@registry.register
def reset_counter() -> str:
    """Reset the counter to zero."""
    _counter["value"] = 0
    return "Counter reset to 0"
```

---

## Troubleshooting

### Tool Not Found

**Problem:** `ToolExecutionError: Tool 'my_tool' not found`

**Solutions:**
1. Make sure you imported the file: `import custom_tools`
2. Check tool is registered: `print(registry.list_tools())`
3. Verify decorator is used: `@registry.register`

### Type Hint Errors

**Problem:** Tool doesn't work correctly with agent

**Solutions:**
1. Add type hints to ALL parameters
2. Add return type annotation
3. Use supported types (str, int, float, bool, List, Dict)

### Agent Doesn't Use Your Tool

**Problem:** Agent uses wrong tool or doesn't use your tool

**Solutions:**
1. Improve docstring - be very specific about what tool does
2. Add parameter descriptions in docstring
3. Test tool directly first: `registry.execute("my_tool", ...)`

---

## Summary

**To create a custom tool:**

1. Write a function with type hints
2. Add a clear docstring
3. Use `@registry.register` decorator
4. Import the file
5. Done! Agent can now use it

**Best practices:**
- ✅ Clear, descriptive names
- ✅ Detailed docstrings
- ✅ Type hints on all parameters
- ✅ Error handling (return errors as strings)
- ✅ Input validation
- ✅ Security checks for dangerous operations

---

## Next Steps

1. Create your first custom tool using the examples above
2. Test it with `demo_custom_tools.py`
3. Add more tools as needed
4. Share your tools with other users!

**Example files:**
- `custom_tools.py` - 8 example custom tools
- `demo_custom_tools.py` - Test custom tools with agent
- `test_integration_quick.py` - Verify framework works

**Happy tool building!** 🛠️
