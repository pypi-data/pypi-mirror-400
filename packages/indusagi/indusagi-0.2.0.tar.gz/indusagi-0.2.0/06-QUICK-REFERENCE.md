# Quick Reference: Code Snippets & Troubleshooting

## ⚡ Fast Command Reference

### Setup Commands
```bash
# Create project
uv init --package indusagi && cd indusagi

# Install dependencies
uv add anthropic typer rich pydantic && uv add --dev pytest

# Editable install
uv pip install -e .

# Test CLI
indusagi --help
```

### Development Commands
```bash
# Run tests
pytest tests/ -v

# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Build package
uv build

# Run agent
indusagi run "your query"
indusagi interactive
```

---

## 🔧 Essential Code Snippets

### Minimal Agent (10 lines)

```python
from anthropic import Anthropic

class Agent:
    def __init__(self):
        self.client = Anthropic()

    def run(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

# Usage
agent = Agent()
print(agent.run("Hello!"))
```

---

### Agent with Tools (30 lines)

```python
from anthropic import Anthropic
import json

client = Anthropic()

def calculator(expression: str) -> str:
    return str(eval(expression))

tools = [{
    "name": "calculator",
    "description": "Calculate math expressions",
    "input_schema": {
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"]
    }
}]

messages = [{"role": "user", "content": "What is 25 * 4?"}]

for _ in range(3):
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        for block in response.content:
            if block.type == "tool_use":
                result = calculator(**block.input)
                messages.append({"role": "user", "content": [{
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                }]})
    else:
        print(response.content[0].text)
        break
```

---

### Simple Tool Registry (20 lines)

```python
tools = {}

def tool(func):
    tools[func.__name__] = func
    return func

@tool
def add(a: int, b: int) -> int:
    return a + b

@tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Execute
print(tools["add"](5, 3))  # 8
print(tools["greet"]("Alice"))  # Hello, Alice!
```

---

### Multi-Agent Router (25 lines)

```python
from indusagi import Agent

agents = {
    "math": Agent("MathBot", "Math specialist"),
    "general": Agent("GenBot", "General helper")
}

def route(query: str) -> str:
    # Simple keyword routing
    if any(word in query.lower() for word in ["calculate", "math", "+"]):
        agent = agents["math"]
    else:
        agent = agents["general"]

    print(f"Routing to: {agent.name}")
    return agent.process(query)

# Usage
print(route("Calculate 10 + 5"))  # Uses MathBot
print(route("Tell me a joke"))    # Uses GenBot
```

---

### CLI with Typer (15 lines)

```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def run(prompt: str):
    """Run agent with prompt."""
    console.print(f"Processing: {prompt}")
    # ... agent logic ...

if __name__ == "__main__":
    app()
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Command not found: my-agent"

**Cause**: Package not installed in editable mode

**Solution**:
```bash
# Reinstall in editable mode
uv pip install -e .

# Verify
which indusagi  # Should show path in .venv/bin/
```

---

### Issue 2: "ANTHROPIC_API_KEY not set"

**Cause**: Environment variable not configured

**Solution**:
```bash
# Linux/Mac
export ANTHROPIC_API_KEY="your-key-here"

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-key-here"

# Verify
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY')[:10])"
```

**Permanent Solution** (.env file):
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Load in code
from dotenv import load_dotenv
load_dotenv()
```

---

### Issue 3: "Module not found: indusagi"

**Cause**: Python can't find your package

**Solution**:
```bash
# Check PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall
uv pip uninstall indusagi
uv pip install -e .

# Verify
python -c "import indusagi; print('OK')"
```

---

### Issue 4: "Tool not found" or tool not executing

**Cause**: Tool not registered properly

**Solution**:
```python
# Check registered tools
from indusagi.tools import registry
print(registry.list_tools())

# Verify schemas
print(len(registry.schemas))  # Should match tool count

# Test execution
result = registry.execute("calculator", expression="2+2")
print(result)
```

---

### Issue 5: Agent not using tools

**Cause**: Using `process()` instead of `process_with_tools()`

**Solution**:
```python
# Wrong
agent.process("Calculate 2+2")

# Correct
agent.process_with_tools("Calculate 2+2")
```

---

### Issue 6: "Rate limit exceeded"

**Cause**: Too many API calls too quickly

**Solution**:
```python
import time

# Add delay between calls
for query in queries:
    response = agent.process(query)
    time.sleep(1)  # Wait 1 second

# Or implement retry with backoff
from functools import wraps

def retry_with_backoff(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "rate_limit" in str(e).lower():
                        time.sleep(2 ** i)  # Exponential backoff
                    else:
                        raise
        return wrapper
    return decorator
```

---

### Issue 7: Tests failing with "ANTHROPIC_API_KEY not set"

**Cause**: Tests run in clean environment

**Solution**:
```python
# Option 1: Skip tests if no API key
import pytest
import os

@pytest.fixture(autouse=True)
def check_api_key():
    if not os.getenv("ANTHROPIC_API_KEY"):
        pytest.skip("API key not set")

# Option 2: Mock API calls
from unittest.mock import Mock, patch

@patch('anthropic.Anthropic')
def test_agent_mocked(mock_anthropic):
    mock_client = Mock()
    mock_anthropic.return_value = mock_client
    # ... test logic ...
```

---

### Issue 8: "AttributeError: 'NoneType' object has no attribute 'text'"

**Cause**: Response format changed or error in API response

**Solution**:
```python
# Defensive coding
response = self.client.messages.create(...)

# Check response structure
if not response or not response.content:
    return "Error: Empty response"

# Safe extraction
text = ""
for block in response.content:
    if hasattr(block, "text"):
        text += block.text

return text or "No text in response"
```

---

### Issue 9: Changes not reflected after editing code

**Cause**: Not using editable install OR Python caching

**Solution**:
```bash
# Verify editable install
pip show indusagi | grep Location
# Should show your project directory

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Reinstall if needed
uv pip install -e . --force-reinstall
```

---

### Issue 10: "Tool execution timeout"

**Cause**: Long-running tool or infinite loop

**Solution**:
```python
import signal

class TimeoutError(Exception):
    pass

def timeout(seconds):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(f"Timeout after {seconds}s")

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
        return wrapper
    return decorator

@registry.register
@timeout(5)  # 5 second timeout
def slow_tool(input: str) -> str:
    # ... tool logic ...
    pass
```

---

## 💡 Pro Tips

### Tip 1: Use Rich for Beautiful Output

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# Pretty print
console.print("[bold green]Success![/bold green]")

# Table
table = Table(title="Agents")
table.add_column("Name")
table.add_column("Role")
table.add_row("MathBot", "Math specialist")
console.print(table)

# Panel
console.print(Panel("Important message", border_style="red"))

# Markdown
console.print(Markdown("# Heading\n- Item 1\n- Item 2"))
```

---

### Tip 2: Debug with Print Statements

```python
# Strategic debug prints
def process_with_tools(self, user_input: str, max_turns: int = 5) -> str:
    print(f"[DEBUG] Input: {user_input}")

    for turn in range(max_turns):
        print(f"[DEBUG] Turn {turn+1}/{max_turns}")

        response = self.client.messages.create(...)

        print(f"[DEBUG] Stop reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            for content in response.content:
                if content.type == "tool_use":
                    print(f"[DEBUG] Tool: {content.name}")
                    print(f"[DEBUG] Input: {content.input}")
                    result = registry.execute(content.name, **content.input)
                    print(f"[DEBUG] Result: {result}")

    print(f"[DEBUG] Final response generated")
    return response.content[0].text
```

---

### Tip 3: Use Python REPL for Quick Testing

```python
# Start Python in project directory
python

# Import and test
from indusagi import Agent, registry

# Check tools
print(registry.list_tools())

# Test agent
agent = Agent("Test", "Tester")
result = agent.process_with_tools("What is 2+2?")
print(result)

# Check message history
print(agent.messages)
```

---

### Tip 4: Hot Reload for Development

```bash
# Install watchdog
pip install watchdog

# Create reload script (reload.py)
cat > reload.py << 'EOF'
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"\n[RELOAD] {event.src_path} changed")
            subprocess.run(["pytest", "tests/", "-v"])

observer = Observer()
observer.schedule(ReloadHandler(), "src/", recursive=True)
observer.start()
print("[WATCHING] src/ for changes...")
observer.join()
EOF

# Run watcher
python reload.py
```

---

### Tip 5: Environment-Specific Configuration

```python
# config.py
import os
from enum import Enum

class Environment(Enum):
    DEV = "development"
    STAGING = "staging"
    PROD = "production"

class Config:
    def __init__(self):
        self.env = Environment(os.getenv("ENV", "development"))

    @property
    def model(self):
        if self.env == Environment.PROD:
            return "claude-sonnet-4-5-20250929"
        return "claude-sonnet-4-5-20250929"  # Same for dev

    @property
    def max_tokens(self):
        return 1024 if self.env == Environment.PROD else 512

    @property
    def verbose(self):
        return self.env != Environment.PROD

# Usage
config = Config()
agent = Agent("Bot", "Helper", max_tokens=config.max_tokens)
```

---

## 📚 Useful Commands Collection

### Git Commands
```bash
# Initialize repo
git init
git add .
git commit -m "Initial commit"

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.venv/
dist/
.env
EOF

# Tag release
git tag -a v0.1.0 -m "Version 0.1.0"
git push origin v0.1.0
```

---

### Package Management
```bash
# Show installed packages
uv pip list

# Show package info
uv pip show indusagi

# Uninstall
uv pip uninstall indusagi

# Upgrade dependencies
uv add anthropic --upgrade
```

---

### Testing Commands
```bash
# Run all tests
pytest

# Run with output
pytest -v

# Run specific test
pytest tests/test_agent.py::test_agent_creation

# Run with coverage
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
```

---

### Development Workflow
```bash
# 1. Create feature branch
git checkout -b feature/new-tool

# 2. Edit code
vim src/indusagi/tools.py

# 3. Test changes
pytest tests/test_tools.py -v

# 4. Format code
black src/ tests/

# 5. Commit
git add .
git commit -m "Add new tool"

# 6. Push and create PR
git push origin feature/new-tool
```

---

## 🔍 Debugging Checklist

When things go wrong, check:

- [ ] API key is set: `echo $ANTHROPIC_API_KEY`
- [ ] Package installed: `pip show indusagi`
- [ ] Editable mode: `pip show indusagi | grep Location`
- [ ] CLI registered: `which my-agent`
- [ ] Tools registered: `python -c "from indusagi.tools import registry; print(registry.list_tools())"`
- [ ] Python path: `python -c "import sys; print(sys.path)"`
- [ ] No syntax errors: `python -m py_compile src/indusagi/*.py`
- [ ] Tests pass: `pytest tests/ -v`

---

## 📖 Additional Resources

### Official Documentation
- **Anthropic API**: https://docs.anthropic.com/
- **Typer**: https://typer.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **Rich**: https://rich.readthedocs.io/
- **UV**: https://docs.astral.sh/uv/

### Tutorials
- **Python Packaging**: https://packaging.python.org/
- **Pytest**: https://docs.pytest.org/
- **FastAPI** (for web APIs): https://fastapi.tiangolo.com/

### Tools
- **Black** (formatter): https://black.readthedocs.io/
- **Ruff** (linter): https://docs.astral.sh/ruff/
- **MyPy** (type checker): https://mypy.readthedocs.io/

---

## 🎯 Cheat Sheet Summary

### Must-Know Commands
```bash
# Setup
uv init --package PROJECT && cd PROJECT
uv add anthropic typer rich pydantic
uv pip install -e .

# Development
indusagi run "query"
pytest tests/ -v
black src/ tests/

# Build & Deploy
uv build
pip install dist/*.whl
```

### Must-Have Code
```python
# Minimal agent
from anthropic import Anthropic
agent = Anthropic().messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)

# Tool registration
@registry.register
def my_tool(param: str) -> str:
    return f"Result: {param}"

# CLI command
@app.command()
def run(prompt: str):
    console.print(agent.process(prompt))
```

---

## 🆘 Emergency Recovery

### Nuclear Option (when everything breaks)

```bash
# 1. Delete everything
rm -rf .venv dist build *.egg-info __pycache__

# 2. Fresh start
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Reinstall
pip install uv
uv pip install -e .

# 4. Test
indusagi --help
pytest tests/ -v
```

---

**End of Quick Reference** - You now have everything needed to build, test, and deploy your indus-agents!

Happy coding! 🚀
