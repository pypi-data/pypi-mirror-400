# Custom Tools - Quick Reference

## What Are Custom Tools?

Custom tools let you extend indus-agents with your own functionality. The agent can then autonomously use your tools to complete tasks!

---

## Quick Start (30 Seconds)

### 1. Create Your Tool

```python
from indusagi import registry

@registry.register
def my_tool(param: str) -> str:
    """What your tool does."""
    return f"Processed: {param}"
```

### 2. Use It

```python
import custom_tools  # Your tools file

from indusagi import Agent
agent = Agent("Bot", "Assistant")
response = agent.process_with_tools("Use my_tool with 'hello'")
```

**Done!** The agent now knows about your tool.

---

## Example Tools Available

The framework includes 9 example custom tools in `custom_tools.py`:

| Tool | What It Does | Example |
|------|--------------|---------|
| `get_weather` | Get weather for a city | "What's the weather in Tokyo?" |
| `random_number` | Generate random number | "Pick a random number 1-100" |
| `generate_password` | Create secure password | "Generate a 16-char password" |
| `text_stats` | Analyze text statistics | "Get stats for 'Hello World'" |
| `date_calculator` | Calculate future dates | "What's the date in 30 days?" |
| `pick_random_item` | Pick from a list | "Pick from: red,blue,green" |
| `build_search_url` | Build search URLs | "Google search URL for AI" |
| `create_file` | Create a text file | "Create file notes.txt" |
| `read_file` | Read a text file | "Read file notes.txt" |

---

## Run the Demo

### Quick Test (No API Key Needed)

```bash
python test_custom_tools_quick.py
```

**Expected:** All 5 tests pass ✅

### Full Demo (Requires OpenAI API Key)

```bash
python demo_custom_tools.py
```

**Expected:**
- 9 custom tools loaded
- Direct tool execution works
- Agent uses custom tools autonomously
- 5 test queries completed

---

## How to Create Your Own Tool

### Requirements

Your tool needs:
1. ✅ Type hints for all parameters
2. ✅ Docstring describing what it does
3. ✅ Return type annotation (`-> str`)
4. ✅ `@registry.register` decorator

### Template

```python
from indusagi import registry

@registry.register
def your_tool_name(param1: str, param2: int = 10) -> str:
    """
    Brief description of what your tool does.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter (optional)

    Returns:
        Description of what is returned
    """
    # Your logic here
    result = f"{param1} processed with {param2}"
    return result
```

### Example: Simple Calculator

```python
@registry.register
def percentage_calculator(value: float, percentage: float) -> str:
    """
    Calculate percentage of a value.

    Args:
        value: The base value
        percentage: Percentage to calculate (e.g., 20 for 20%)

    Returns:
        Result of percentage calculation
    """
    result = (value * percentage) / 100
    return f"{percentage}% of {value} is {result}"
```

**Usage:**
```python
# Direct
result = registry.execute("percentage_calculator", value=200, percentage=15)
# Result: "15% of 200 is 30.0"

# With agent
agent.process_with_tools("What is 15% of 200?")
# Agent uses percentage_calculator and responds: "15% of 200 is 30.0"
```

---

## Tool Types by Use Case

### 1. Data Processing

```python
@registry.register
def sort_numbers(numbers: str) -> str:
    """Sort comma-separated numbers."""
    nums = [float(n) for n in numbers.split(',')]
    sorted_nums = sorted(nums)
    return f"Sorted: {', '.join(map(str, sorted_nums))}"
```

### 2. Text Operations

```python
@registry.register
def word_count(text: str) -> str:
    """Count words in text."""
    count = len(text.split())
    return f"Word count: {count}"
```

### 3. Random Generation

```python
@registry.register
def flip_coin() -> str:
    """Flip a coin."""
    import random
    result = random.choice(["Heads", "Tails"])
    return f"Coin flip: {result}"
```

### 4. Date/Time

```python
@registry.register
def days_between(date1: str, date2: str) -> str:
    """Calculate days between two dates (YYYY-MM-DD format)."""
    from datetime import datetime
    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    days = abs((d2 - d1).days)
    return f"Days between {date1} and {date2}: {days}"
```

### 5. Conversions

```python
@registry.register
def celsius_to_fahrenheit(celsius: float) -> str:
    """Convert Celsius to Fahrenheit."""
    fahrenheit = (celsius * 9/5) + 32
    return f"{celsius}°C = {fahrenheit}°F"
```

---

## Organizing Your Tools

### Option 1: Single File (Recommended for Small Projects)

`my_tools.py`:
```python
from indusagi import registry

@registry.register
def tool1(param: str) -> str:
    """Tool 1."""
    return param

@registry.register
def tool2(param: str) -> str:
    """Tool 2."""
    return param.upper()
```

Usage:
```python
import my_tools  # Registers both tools
```

### Option 2: Multiple Files (Recommended for Large Projects)

```
tools/
├── __init__.py
├── math_tools.py
├── text_tools.py
└── api_tools.py
```

`tools/__init__.py`:
```python
from . import math_tools
from . import text_tools
from . import api_tools
```

Usage:
```python
import tools  # Registers all tools from all files
```

---

## Testing Your Tools

### Method 1: Direct Execution

```python
from indusagi import registry
import my_tools

# Execute directly
result = registry.execute("my_tool", param="test")
print(result)
```

### Method 2: With Agent

```python
from indusagi import Agent
import my_tools

agent = Agent("TestBot", "Test assistant")
response = agent.process_with_tools("Use my_tool with 'test'")
print(response)
```

### Method 3: Verify Registration

```python
# Check if tool exists
tools = registry.list_tools()
print("my_tool" in tools)  # Should be True

# See all tools
print(tools)
```

---

## Common Patterns

### Error Handling

```python
@registry.register
def safe_divide(a: float, b: float) -> str:
    """Divide two numbers safely."""
    if b == 0:
        return "Error: Cannot divide by zero"
    result = a / b
    return f"{a} / {b} = {result}"
```

### Optional Parameters

```python
@registry.register
def greet(name: str, language: str = "english") -> str:
    """Greet someone in different languages."""
    greetings = {
        "english": f"Hello, {name}!",
        "spanish": f"Hola, {name}!",
        "french": f"Bonjour, {name}!"
    }
    return greetings.get(language, greetings["english"])
```

### Input Validation

```python
@registry.register
def validate_email(email: str) -> str:
    """Check if email format is valid."""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if re.match(pattern, email):
        return f"Valid email: {email}"
    else:
        return f"Invalid email: {email}"
```

---

## Security Best Practices

### 1. Validate Inputs

```python
@registry.register
def process_filename(filename: str) -> str:
    """Process a filename."""
    # Only allow specific extensions
    if not filename.endswith('.txt'):
        return "Error: Only .txt files allowed"

    # No directory traversal
    if '/' in filename or '\\' in filename:
        return "Error: Filename cannot contain path separators"

    # Process safely
    return f"Processing: {filename}"
```

### 2. Mark Dangerous Operations

```python
@registry.register(dangerous=True)
def delete_file(filename: str) -> str:
    """Delete a file (dangerous operation)."""
    # Extra validation
    if not filename.endswith('.txt'):
        return "Error: Can only delete .txt files"

    # More validation...
    import os
    if os.path.exists(filename):
        os.remove(filename)
        return f"Deleted: {filename}"
    return "Error: File not found"
```

### 3. Limit Scope

```python
@registry.register
def read_config(key: str) -> str:
    """Read a configuration value."""
    # Whitelist of allowed keys
    allowed_keys = ['app_name', 'version', 'author']

    if key not in allowed_keys:
        return f"Error: Key '{key}' is not allowed"

    config = {
        'app_name': 'MyApp',
        'version': '1.0.0',
        'author': 'Developer'
    }

    return f"{key}: {config.get(key, 'Not found')}"
```

---

## Troubleshooting

### Tool Not Being Used by Agent

**Symptoms:** Agent gives general answer instead of using your tool

**Solutions:**
1. Improve docstring - be very specific
2. Add detailed parameter descriptions
3. Make tool name match common query patterns
4. Test tool directly first

**Example:**
```python
# Vague - Agent might not use it
@registry.register
def process(data: str) -> str:
    """Process data."""
    return data

# Clear - Agent knows when to use it
@registry.register
def reverse_text(text: str) -> str:
    """Reverse the order of characters in a text string."""
    return text[::-1]
```

### Tool Not Found Error

**Error:** `ToolExecutionError: Tool 'my_tool' not found`

**Solutions:**
1. Make sure you imported the file: `import my_tools`
2. Check decorator is present: `@registry.register`
3. Verify registration: `print(registry.list_tools())`

### Type Hint Errors

**Error:** Schema generation fails

**Solution:** Add type hints to ALL parameters
```python
# Missing type hints - FAILS
def tool(param):
    return param

# With type hints - WORKS
def tool(param: str) -> str:
    return param
```

---

## Documentation

### Complete Guides

- **HOW_TO_CREATE_CUSTOM_TOOLS.md** - Comprehensive guide (600+ lines)
- **CUSTOM_TOOLS_FEATURE_COMPLETE.md** - Feature implementation details
- **CUSTOM_TOOLS_README.md** - This quick reference

### Example Files

- **custom_tools.py** - 9 working example tools
- **demo_custom_tools.py** - Full demonstration script
- **test_custom_tools_quick.py** - Automated test suite

---

## Commands Reference

```bash
# Test custom tools (no API needed)
python test_custom_tools_quick.py

# Run full demo (requires API key)
python demo_custom_tools.py

# List all registered tools
python -c "from indusagi import registry; import custom_tools; print(registry.list_tools())"

# Test a specific tool
python -c "from indusagi import registry; import custom_tools; print(registry.execute('get_weather', city='Tokyo', unit='celsius'))"
```

---

## Next Steps

1. **Read examples** - Check `custom_tools.py` for 9 working examples
2. **Create your first tool** - Use the template above
3. **Test it** - Run `test_custom_tools_quick.py`
4. **Use with agent** - Let the agent discover and use your tool
5. **Read full guide** - See `HOW_TO_CREATE_CUSTOM_TOOLS.md` for details

---

## Summary

**Creating a custom tool is simple:**

1. Write function with type hints
2. Add `@registry.register` decorator
3. Import the file
4. Done! Agent can use it

**The agent automatically:**
- Discovers your tools
- Generates OpenAI schemas
- Decides when to use them
- Executes them when needed

**You get:**
- ✅ 9 working examples
- ✅ Comprehensive documentation
- ✅ Automated tests
- ✅ Demo scripts
- ✅ Quick reference (this file)

**Start building your custom tools today!** 🛠️
