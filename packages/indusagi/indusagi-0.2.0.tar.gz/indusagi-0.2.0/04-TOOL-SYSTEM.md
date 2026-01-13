# Tool System: Patterns and Examples

## 🔧 Tool System Overview

The tool system allows agents to interact with external functions, APIs, and services. This guide covers tool creation patterns, best practices, and examples.

---

## 📚 Tool Creation Patterns

### Pattern 1: Simple Function Tool (Easiest)

```python
from indusagi.tools import registry

@registry.register
def simple_tool(input_text: str) -> str:
    """
    Simple tool that processes text.

    Args:
        input_text: The text to process

    Returns:
        Processed text
    """
    return input_text.upper()
```

**When to use**: Quick, standalone functions with no dependencies

---

### Pattern 2: Tool with Multiple Parameters

```python
@registry.register
def format_text(
    text: str,
    uppercase: bool = False,
    prefix: str = ""
) -> str:
    """
    Format text with various options.

    Args:
        text: The text to format
        uppercase: Convert to uppercase if True
        prefix: String to prepend

    Returns:
        Formatted text
    """
    result = text
    if uppercase:
        result = result.upper()
    if prefix:
        result = f"{prefix}{result}"
    return result
```

**When to use**: Tools that need configuration or options

---

### Pattern 3: Tool with External API

```python
import requests

@registry.register
def get_weather(city: str) -> str:
    """
    Get current weather for a city.

    Args:
        city: City name (e.g., "London", "New York")

    Returns:
        Weather information as text
    """
    try:
        # Example with OpenWeather API
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "Error: API key not configured"

        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]

        return f"Weather in {city}: {temp}°C, {description}"

    except requests.RequestException as e:
        return f"Error fetching weather: {str(e)}"
    except KeyError:
        return "Error: Invalid response format"
```

**When to use**: Integrating with external services

---

### Pattern 4: Tool with File Operations

```python
@registry.register
def read_file(filepath: str) -> str:
    """
    Read contents of a file.

    Args:
        filepath: Path to file (relative or absolute)

    Returns:
        File contents as text
    """
    try:
        # Security: restrict to specific directory
        safe_dir = os.path.abspath("./data")
        requested_path = os.path.abspath(filepath)

        if not requested_path.startswith(safe_dir):
            return "Error: Access denied - file outside allowed directory"

        with open(requested_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content[:1000]  # Limit to first 1000 chars

    except FileNotFoundError:
        return f"Error: File not found: {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

**When to use**: File system operations (with security!)

---

### Pattern 5: Tool with Complex Return Types

```python
import json

@registry.register
def search_database(query: str) -> str:
    """
    Search database and return results.

    Args:
        query: Search query

    Returns:
        JSON string with search results
    """
    # Mock database search
    results = [
        {"id": 1, "title": "Result 1", "relevance": 0.95},
        {"id": 2, "title": "Result 2", "relevance": 0.87},
    ]

    # Filter by query
    filtered = [r for r in results if query.lower() in r["title"].lower()]

    # Return as JSON string (LLMs handle JSON well)
    return json.dumps(filtered, indent=2)
```

**When to use**: Returning structured data to the agent

---

## 🛡️ Security Best Practices

### 1. Input Validation

```python
@registry.register
def execute_calculation(expression: str) -> str:
    """Safe calculator with input validation."""
    # Whitelist allowed characters
    allowed = set("0123456789+-*/() .")

    if not all(c in allowed for c in expression):
        return "Error: Invalid characters in expression"

    # Additional checks
    if "**" in expression:  # Prevent power operations
        return "Error: Power operations not allowed"

    if expression.count("(") != expression.count(")"):
        return "Error: Unmatched parentheses"

    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

### 2. Rate Limiting

```python
from functools import wraps
from time import time
from collections import defaultdict

# Simple rate limiter
call_times = defaultdict(list)
MAX_CALLS = 10
TIME_WINDOW = 60  # seconds

def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        now = time()
        func_name = func.__name__

        # Clean old calls
        call_times[func_name] = [
            t for t in call_times[func_name]
            if now - t < TIME_WINDOW
        ]

        # Check limit
        if len(call_times[func_name]) >= MAX_CALLS:
            return f"Rate limit exceeded for {func_name}"

        # Record this call
        call_times[func_name].append(now)

        return func(*args, **kwargs)

    return wrapper

@registry.register
@rate_limit
def expensive_api_call(query: str) -> str:
    """Tool with rate limiting."""
    # ... API call logic ...
    pass
```

### 3. Timeout Protection

```python
from functools import wraps
import signal

class TimeoutError(Exception):
    pass

def timeout(seconds):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(f"Function timed out after {seconds}s")

        @wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper
    return decorator

@registry.register
@timeout(5)  # 5 second timeout
def slow_operation(data: str) -> str:
    """Tool with timeout protection."""
    # ... potentially slow operation ...
    pass
```

### 4. Error Handling Template

```python
@registry.register
def robust_tool(input_data: str) -> str:
    """
    Template for robust tool with comprehensive error handling.
    """
    try:
        # Validate input
        if not input_data:
            return "Error: Empty input provided"

        if len(input_data) > 10000:
            return "Error: Input too large (max 10000 characters)"

        # Main logic
        result = process_data(input_data)

        # Validate output
        if not result:
            return "Warning: Operation produced no results"

        return result

    except ValueError as e:
        return f"Validation error: {str(e)}"
    except requests.RequestException as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in robust_tool: {str(e)}")
        return "An unexpected error occurred. Please try again."
```

---

## 🎯 Example Tools Library

### Web Scraping Tool

```python
from bs4 import BeautifulSoup
import requests

@registry.register
def fetch_webpage(url: str) -> str:
    """
    Fetch and extract text from a webpage.

    Args:
        url: URL to fetch

    Returns:
        Extracted text content
    """
    try:
        # Validate URL
        if not url.startswith(("http://", "https://")):
            return "Error: Invalid URL format"

        # Fetch with timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # Limit length
        return text[:5000]

    except Exception as e:
        return f"Error fetching webpage: {str(e)}"
```

### JSON/Dictionary Tool

```python
@registry.register
def extract_json_field(json_str: str, field_path: str) -> str:
    """
    Extract field from JSON string using dot notation.

    Args:
        json_str: JSON string
        field_path: Path like "data.user.name"

    Returns:
        Extracted value as string
    """
    try:
        data = json.loads(json_str)

        # Navigate path
        current = data
        for key in field_path.split('.'):
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list):
                current = current[int(key)]
            else:
                return f"Error: Cannot navigate to {field_path}"

            if current is None:
                return f"Error: Field {field_path} not found"

        return json.dumps(current)

    except json.JSONDecodeError:
        return "Error: Invalid JSON"
    except (KeyError, IndexError, ValueError) as e:
        return f"Error: {str(e)}"
```

### Date/Time Tools

```python
from datetime import datetime, timedelta

@registry.register
def date_arithmetic(operation: str, days: int) -> str:
    """
    Perform date arithmetic.

    Args:
        operation: "add" or "subtract"
        days: Number of days

    Returns:
        Resulting date in YYYY-MM-DD format
    """
    try:
        today = datetime.now()

        if operation == "add":
            result_date = today + timedelta(days=days)
        elif operation == "subtract":
            result_date = today - timedelta(days=days)
        else:
            return "Error: Operation must be 'add' or 'subtract'"

        return result_date.strftime("%Y-%m-%d")

    except Exception as e:
        return f"Error: {str(e)}"

@registry.register
def format_date(date_str: str, format: str) -> str:
    """
    Format a date string.

    Args:
        date_str: Date in YYYY-MM-DD format
        format: Output format (e.g., "%B %d, %Y" for "January 07, 2025")

    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime(format)
    except ValueError:
        return "Error: Invalid date format (use YYYY-MM-DD)"
```

### String Manipulation Tools

```python
@registry.register
def text_summary(text: str, max_words: int = 50) -> str:
    """
    Create a summary of text.

    Args:
        text: Text to summarize
        max_words: Maximum words in summary

    Returns:
        Summarized text
    """
    words = text.split()
    if len(words) <= max_words:
        return text

    summary = ' '.join(words[:max_words])
    return f"{summary}..."

@registry.register
def count_words(text: str) -> str:
    """
    Count words in text.

    Args:
        text: Text to analyze

    Returns:
        Word count and other stats
    """
    words = text.split()
    chars = len(text)
    lines = len(text.splitlines())

    return f"Words: {len(words)}, Characters: {chars}, Lines: {lines}"
```

---

## 🧪 Testing Tools

### Unit Test Example

```python
# tests/test_custom_tools.py
import pytest
from indusagi.tools import registry

def test_simple_tool():
    """Test simple tool registration and execution."""
    @registry.register
    def test_tool(x: int) -> str:
        return str(x * 2)

    assert "test_tool" in registry.tools
    result = registry.execute("test_tool", x=5)
    assert result == "10"

def test_tool_error_handling():
    """Test tool handles errors gracefully."""
    result = registry.execute("calculator", expression="invalid")
    assert "Error" in result or "error" in result.lower()

def test_tool_with_optional_params():
    """Test tool with optional parameters."""
    @registry.register
    def optional_tool(required: str, optional: str = "default") -> str:
        return f"{required}-{optional}"

    result1 = registry.execute("optional_tool", required="test")
    assert result1 == "test-default"

    result2 = registry.execute("optional_tool", required="test", optional="custom")
    assert result2 == "test-custom"
```

### Integration Test with Agent

```python
# tests/test_agent_tools_integration.py
import pytest
from indusagi.agent import Agent

@pytest.mark.asyncio
async def test_agent_uses_calculator():
    """Test agent can use calculator tool."""
    agent = Agent("TestAgent", "Math helper")
    result = agent.process_with_tools("What is 144 divided by 12?")

    # Agent should have used calculator
    assert "12" in result

def test_agent_uses_multiple_tools():
    """Test agent can chain multiple tools."""
    agent = Agent("TestAgent", "Multi-tool helper")
    result = agent.process_with_tools(
        "What's the time and what's 25 * 4?"
    )

    # Should contain both results
    assert "100" in result or "25*4" in result
```

---

## 🚀 Advanced Patterns

### Tool with State

```python
class CounterTool:
    """Tool with persistent state."""

    def __init__(self):
        self.count = 0

    @registry.register
    def increment(self, amount: int = 1) -> str:
        """Increment counter."""
        self.count += amount
        return f"Counter: {self.count}"

    @registry.register
    def reset_counter(self) -> str:
        """Reset counter to zero."""
        self.count = 0
        return "Counter reset to 0"

# Create instance
counter_tool = CounterTool()
```

### Async Tool

```python
import asyncio

@registry.register
def async_fetch(url: str) -> str:
    """
    Async fetch (wrapped for sync interface).

    Note: Tool registry expects sync functions,
    so we wrap async operations.
    """
    async def _fetch():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    # Run async function in sync context
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_fetch())
    return result[:1000]
```

### Tool with Caching

```python
from functools import lru_cache

@registry.register
@lru_cache(maxsize=100)
def cached_api_call(query: str) -> str:
    """
    API call with caching.

    Results are cached to avoid redundant API calls.
    """
    # Expensive API call
    response = requests.get(f"https://api.example.com?q={query}")
    return response.text
```

---

## 📊 Tool Schema Examples

### Manual Schema Definition

If you need more control than auto-generation:

```python
def custom_tool(param1: str, param2: int) -> str:
    """Custom tool with manual schema."""
    return f"{param1}: {param2}"

# Manually add to registry
registry.tools["custom_tool"] = custom_tool
registry._schemas.append({
    "name": "custom_tool",
    "description": "Custom tool with detailed schema",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "The first parameter",
                "minLength": 1,
                "maxLength": 100
            },
            "param2": {
                "type": "integer",
                "description": "The second parameter",
                "minimum": 0,
                "maximum": 1000
            }
        },
        "required": ["param1", "param2"]
    }
})
```

---

## 🎨 Tool Best Practices

### DO:
- ✅ Write clear, descriptive docstrings
- ✅ Use type hints for all parameters
- ✅ Validate inputs
- ✅ Handle errors gracefully
- ✅ Return strings (LLMs understand them best)
- ✅ Keep tools focused (single responsibility)
- ✅ Add security checks
- ✅ Test tools independently

### DON'T:
- ❌ Execute arbitrary code
- ❌ Access files outside safe directories
- ❌ Make unbounded API calls
- ❌ Return huge amounts of data
- ❌ Use global state (unless necessary)
- ❌ Ignore errors
- ❌ Trust user input blindly

---

## 🔍 Debugging Tools

### Debug Wrapper

```python
from functools import wraps
import time

def debug_tool(func):
    """Decorator to debug tool execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"[DEBUG] Calling {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            print(f"[DEBUG] {func.__name__} completed in {duration:.2f}s")
            print(f"[DEBUG] Result: {result[:100]}...")
            return result
        except Exception as e:
            duration = time.time() - start
            print(f"[DEBUG] {func.__name__} failed after {duration:.2f}s: {e}")
            raise

    return wrapper

@registry.register
@debug_tool
def monitored_tool(input: str) -> str:
    """Tool with monitoring."""
    return input.upper()
```

---

**Next**: See **05-PACKAGING-DEPLOYMENT.md** for packaging and deployment guide
