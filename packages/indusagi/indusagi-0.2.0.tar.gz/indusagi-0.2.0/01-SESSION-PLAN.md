# Session Plan: 2-3 Hour Timeline

## 🎯 Session Formats

Choose based on your available time and complexity needs:

### **Option A: 2-Hour Intensive** (Core Features Only)
Best for: Quick prototyping, proof of concept, learning basics

### **Option B: 3-Hour Comprehensive** (Production-Ready)
Best for: Complete framework, deployable package, full features

---

## 🚀 OPTION A: 2-HOUR SESSION PLAN

### **Phase 1: Setup & Foundation (60 minutes)**

#### **00:00-00:10 | Environment Setup (10 min)**

**Objectives:**
- ✅ Create project structure
- ✅ Install dependencies
- ✅ Verify API connection

**Commands:**
```bash
# Create project
uv init --package indusagi
cd indusagi

# Add dependencies
uv add typer anthropic rich pydantic

# Add dev dependencies
uv add --dev pytest pytest-asyncio

# Install in editable mode
uv pip install -e .

# Verify installation
python -c "import anthropic; print('✓ Anthropic installed')"
```

**Test:**
```bash
# Should work immediately
indusagi --help
```

**Checkpoint:** ✓ CLI command exists and shows help

---

#### **00:10-00:30 | Core Agent Class (20 min)**

**Objectives:**
- ✅ Create Agent class with config
- ✅ Integrate LLM API
- ✅ Test basic query

**Create:** `src/indusagi/agent.py`

```python
from anthropic import Anthropic
from pydantic import BaseModel
from typing import Optional

class AgentConfig(BaseModel):
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 1024
    temperature: float = 0.7

class Agent:
    def __init__(self, name: str, role: str, config: Optional[AgentConfig] = None):
        self.name = name
        self.role = role
        self.config = config or AgentConfig()
        self.client = Anthropic()
        self.messages = []

    def process(self, user_input: str) -> str:
        """Process user input and return response."""
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            messages=self.messages
        )

        assistant_message = response.content[0].text
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

# Quick test
if __name__ == "__main__":
    agent = Agent(name="TestAgent", role="Helper")
    result = agent.process("Say hello!")
    print(result)
```

**Test:**
```bash
python src/indusagi/agent.py
# Should print a friendly response
```

**Checkpoint:** ✓ Agent responds to queries

---

#### **00:30-00:50 | Tool System (20 min)**

**Objectives:**
- ✅ Create tool decorator
- ✅ Register 2-3 simple tools
- ✅ Test tool execution

**Create:** `src/indusagi/tools.py`

```python
from typing import Callable, Dict, Any
import inspect
from pydantic import BaseModel

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: list = []

    def register(self, func: Callable) -> Callable:
        """Decorator to register a tool."""
        self.tools[func.__name__] = func

        # Generate schema
        sig = inspect.signature(func)
        properties = {}
        required = []

        for name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"

            properties[name] = {"type": param_type}
            if param.default == inspect.Parameter.empty:
                required.append(name)

        schema = {
            "name": func.__name__,
            "description": inspect.getdoc(func) or "",
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
        self.schemas.append(schema)
        return func

    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return self.tools[name](**kwargs)

# Create global registry
registry = ToolRegistry()

# Example tools
@registry.register
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        result = eval(expression)  # Use safe-eval in production!
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@registry.register
def get_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")

# Test
if __name__ == "__main__":
    print(registry.execute("calculator", expression="2+2"))
    print(registry.execute("get_time"))
    print(f"Registered tools: {list(registry.tools.keys())}")
```

**Test:**
```bash
python src/indusagi/tools.py
# Should show: 4, current time, and tool list
```

**Checkpoint:** ✓ Tools execute successfully

---

#### **00:50-01:00 | Agent + Tools Integration (10 min)**

**Objectives:**
- ✅ Integrate tools with agent
- ✅ Test tool calling

**Update:** `src/indusagi/agent.py`

```python
from .tools import registry

class Agent:
    # ... (previous code)

    def process_with_tools(self, user_input: str, max_turns: int = 3) -> str:
        """Process with tool support."""
        self.messages.append({"role": "user", "content": user_input})

        for turn in range(max_turns):
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                tools=registry.schemas,
                messages=self.messages
            )

            # Check if done
            if response.stop_reason == "end_turn":
                text = response.content[0].text
                self.messages.append({"role": "assistant", "content": text})
                return text

            # Handle tool use
            if response.stop_reason == "tool_use":
                self.messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for content in response.content:
                    if content.type == "tool_use":
                        result = registry.execute(content.name, **content.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": str(result)
                        })

                self.messages.append({"role": "user", "content": tool_results})

        return "Max turns reached"
```

**Test:**
```bash
python -c "
from src.indusagi.agent import Agent
agent = Agent('Test', 'Helper')
print(agent.process_with_tools('What is 25 * 4?'))
"
```

**Checkpoint:** ✓ Agent uses tools to answer questions

---

### **Phase 2: Break & Review (10 minutes)**

#### **01:00-01:10 | Break Time**

**Activities:**
- Stand up and stretch
- Review what you've built
- Test the complete flow
- Adjust timeline if needed

**Quick Demo Test:**
```bash
python -c "
from src.indusagi.agent import Agent
agent = Agent('Demo', 'Assistant')
print('Test 1:', agent.process_with_tools('What time is it?'))
print('Test 2:', agent.process_with_tools('Calculate 100 / 4'))
"
```

---

### **Phase 3: Multi-Agent & CLI (50 minutes)**

#### **01:10-01:30 | Multi-Agent Orchestration (20 min)**

**Objectives:**
- ✅ Create orchestrator class
- ✅ Add 2-3 specialized agents
- ✅ Test routing

**Create:** `src/indusagi/orchestrator.py`

```python
from typing import Dict
from .agent import Agent, AgentConfig

class Orchestrator:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.setup_agents()

    def setup_agents(self):
        """Initialize specialized agents."""
        self.agents["general"] = Agent(
            name="General",
            role="General purpose assistant"
        )

        self.agents["math"] = Agent(
            name="MathExpert",
            role="Mathematical calculations and analysis"
        )

        self.agents["time"] = Agent(
            name="TimeKeeper",
            role="Time and date information"
        )

    def route(self, user_input: str) -> str:
        """Route request to appropriate agent."""
        input_lower = user_input.lower()

        # Simple keyword-based routing
        if any(word in input_lower for word in ["calculate", "math", "compute", "+"]):
            agent = self.agents["math"]
        elif any(word in input_lower for word in ["time", "date", "clock"]):
            agent = self.agents["time"]
        else:
            agent = self.agents["general"]

        print(f"[Routing to: {agent.name}]")
        return agent.process_with_tools(user_input)

# Test
if __name__ == "__main__":
    orchestrator = Orchestrator()
    print(orchestrator.route("What's 50 * 2?"))
    print(orchestrator.route("What time is it?"))
```

**Test:**
```bash
python src/indusagi/orchestrator.py
```

**Checkpoint:** ✓ Different agents handle different queries

---

#### **01:30-01:50 | CLI Interface (20 min)**

**Objectives:**
- ✅ Create Typer CLI
- ✅ Add commands
- ✅ Test CLI

**Create:** `src/indusagi/cli.py`

```python
import typer
from rich.console import Console
from rich.markdown import Markdown
from .orchestrator import Orchestrator
import os

app = typer.Typer(help="AI indus-agents CLI")
console = Console()

@app.command()
def run(
    prompt: str = typer.Argument(..., help="Prompt for the agent"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run the indus-agents with a prompt."""

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
        raise typer.Exit(1)

    if verbose:
        console.print(f"[dim]Processing: {prompt}[/dim]")

    orchestrator = Orchestrator()

    with console.status("[bold green]Thinking..."):
        response = orchestrator.route(prompt)

    console.print("\n[bold cyan]Response:[/bold cyan]")
    console.print(Markdown(response))

@app.command()
def version():
    """Show version information."""
    console.print("[bold]indusagi[/bold] v0.1.0")
    console.print("Python indus-agents with multi-agent orchestration")

@app.command()
def interactive():
    """Start interactive session."""
    console.print("[bold green]Interactive Agent Session[/bold green]")
    console.print("Type 'quit' to exit\n")

    orchestrator = Orchestrator()

    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ")
            if user_input.lower() in ['quit', 'exit']:
                break

            response = orchestrator.route(user_input)
            console.print(f"[bold green]Agent:[/bold green] {response}\n")
        except KeyboardInterrupt:
            break

    console.print("\n[dim]Goodbye![/dim]")

if __name__ == "__main__":
    app()
```

**Update:** `pyproject.toml`

```toml
[project.scripts]
indusagi = "indusagi.cli:app"
```

**Test:**
```bash
indusagi run "What is 10 * 5?"
indusagi version
indusagi interactive
```

**Checkpoint:** ✓ CLI works with all commands

---

#### **01:50-02:00 | Testing & Cleanup (10 min)**

**Objectives:**
- ✅ Write basic tests
- ✅ Run test suite
- ✅ Document usage

**Create:** `tests/test_agent.py`

```python
import pytest
from indusagi.agent import Agent, AgentConfig
from indusagi.tools import registry

def test_agent_creation():
    agent = Agent(name="Test", role="Tester")
    assert agent.name == "Test"
    assert agent.role == "Tester"

def test_tool_registry():
    assert "calculator" in registry.tools
    result = registry.execute("calculator", expression="2+2")
    assert "4" in result

def test_calculator_tool():
    result = registry.execute("calculator", expression="10 * 5")
    assert "50" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run Tests:**
```bash
pytest tests/ -v
```

**Create:** `README.md`

```markdown
# indus-agents

indus-agents with multi-agent orchestration and tool support.

## Installation

\`\`\`bash
pip install -e .
\`\`\`

## Usage

\`\`\`bash
export ANTHROPIC_API_KEY="your-key"
indusagi run "What is 10 * 5?"
indusagi interactive
\`\`\`
```

**Checkpoint:** ✓ Tests pass, documentation exists

---

## ✅ 2-Hour Session Complete!

**You've Built:**
- Core agent with LLM integration
- Tool system with auto-schema generation
- Multi-agent orchestrator
- Professional CLI interface
- Basic tests

---

## 🚀 OPTION B: 3-HOUR SESSION PLAN

### **Phase 1: Setup & Foundation (60 minutes)**

#### **00:00-00:15 | Environment Setup (15 min)**

Same as 2-hour session, plus:
- Set up git repository
- Create .gitignore
- Initial commit

```bash
git init
echo ".venv/\n__pycache__/\n*.pyc\n.env" > .gitignore
git add .
git commit -m "Initial commit: Project structure"
```

---

#### **00:15-00:40 | Core Agent + Config (25 min)**

Same as 2-hour session **00:10-00:30**, plus:

**Enhanced Configuration:**

```python
# src/indusagi/config.py
from pydantic import BaseModel, Field
from typing import Optional
import os

class AgentConfig(BaseModel):
    model: str = Field(default="claude-sonnet-4-5-20250929")
    max_tokens: int = Field(default=1024, ge=100, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    api_key: Optional[str] = Field(default=None)

    @classmethod
    def from_env(cls):
        """Load config from environment variables."""
        return cls(
            model=os.getenv("AGENT_MODEL", "claude-sonnet-4-5-20250929"),
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
```

---

#### **00:40-01:05 | Tool System (25 min)**

Same as 2-hour session **00:30-00:50**, plus additional tools:

```python
@registry.register
def web_search(query: str) -> str:
    """Search the web (mock implementation)."""
    return f"Search results for: {query}"

@registry.register
def file_read(filename: str) -> str:
    """Read a file (safe mock)."""
    return f"Contents of {filename}"
```

---

#### **01:05-01:15 | Agent + Tools Integration (10 min)**

Same as 2-hour session **00:50-01:00**

---

### **Phase 2: Break & Checkpoint (10 minutes)**

#### **01:15-01:25 | First Break**

---

### **Phase 3: Core Features (60 minutes)**

#### **01:25-01:45 | Memory System (20 min)**

**Create:** `src/indusagi/memory.py`

```python
from collections import deque
from typing import List, Dict
import json

class ConversationMemory:
    def __init__(self, max_messages: int = 20):
        self.messages = deque(maxlen=max_messages)
        self.metadata = {}

    def add(self, role: str, content: str):
        """Add message to memory."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp()
        })

    def get_messages(self) -> List[Dict]:
        """Get all messages."""
        return list(self.messages)

    def clear(self):
        """Clear all messages."""
        self.messages.clear()

    def save(self, filepath: str):
        """Save to file."""
        with open(filepath, 'w') as f:
            json.dump(list(self.messages), f, indent=2)

    def load(self, filepath: str):
        """Load from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.messages = deque(data, maxlen=self.messages.maxlen)

    @staticmethod
    def _get_timestamp():
        from datetime import datetime
        return datetime.now().isoformat()
```

**Update Agent to use memory:**

```python
from .memory import ConversationMemory

class Agent:
    def __init__(self, name: str, role: str, config: Optional[AgentConfig] = None):
        self.name = name
        self.role = role
        self.config = config or AgentConfig()
        self.client = Anthropic()
        self.memory = ConversationMemory()
```

---

#### **01:45-02:05 | Enhanced Orchestration (20 min)**

**Enhanced routing with confidence scores:**

```python
class Orchestrator:
    def route(self, user_input: str) -> tuple[str, Agent]:
        """Route with confidence score."""
        scores = {
            "math": self._score_math(user_input),
            "time": self._score_time(user_input),
            "general": 0.5  # default score
        }

        best_agent = max(scores, key=scores.get)
        return scores[best_agent], self.agents[best_agent]

    def _score_math(self, text: str) -> float:
        math_keywords = ["calculate", "math", "compute", "+", "-", "*", "/"]
        score = sum(1 for kw in math_keywords if kw in text.lower())
        return min(score / len(math_keywords), 1.0)
```

---

#### **02:05-02:25 | Enhanced CLI + Tests (20 min)**

**Add more CLI commands:**

```python
@app.command()
def list_tools():
    """List all available tools."""
    from .tools import registry
    console.print("[bold]Available Tools:[/bold]")
    for name in registry.tools.keys():
        console.print(f"  • {name}")

@app.command()
def test_connection():
    """Test API connection."""
    try:
        agent = Agent("Test", "Tester")
        agent.process("Hi")
        console.print("[green]✓ API connection successful[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
```

**More tests:**

```python
def test_memory():
    memory = ConversationMemory(max_messages=5)
    memory.add("user", "Hello")
    memory.add("assistant", "Hi there!")
    assert len(memory.get_messages()) == 2

def test_orchestrator_routing():
    orchestrator = Orchestrator()
    result = orchestrator.route("Calculate 5+5")
    assert "10" in result
```

---

### **Phase 4: Second Break (10 minutes)**

#### **02:25-02:35 | Break & Integration Test**

---

### **Phase 5: Advanced Features (40 minutes)**

#### **02:35-02:55 | Streaming Support (20 min)**

```python
def process_streaming(self, user_input: str):
    """Process with streaming output."""
    with self.client.messages.stream(
        model=self.config.model,
        max_tokens=self.config.max_tokens,
        messages=[{"role": "user", "content": user_input}]
    ) as stream:
        for text in stream.text_stream:
            yield text
```

---

#### **02:55-03:15 | Polish & Documentation (20 min)**

- Add docstrings to all functions
- Create comprehensive README
- Add usage examples
- Create CHANGELOG.md

---

### **Phase 6: Wrap-up (15 minutes)**

#### **03:15-03:30 | Final Testing & Package**

```bash
# Run all tests
pytest tests/ -v --cov=src/indusagi

# Build package
uv build

# Test installation
pip install dist/*.whl

# Final demo
indusagi interactive
```

---

## ✅ 3-Hour Session Complete!

**You've Built:**
- Everything from 2-hour session
- Conversation memory system
- Enhanced routing with scoring
- Streaming support
- Comprehensive tests (80%+ coverage)
- Professional documentation
- Deployable package

---

## 🆘 Contingency Plans

### Running Behind Schedule?

**Priority 1 (Must Have):**
- Agent class with LLM
- Basic tool system
- CLI interface

**Priority 2 (Should Have):**
- Multi-agent orchestration
- Tool integration

**Priority 3 (Nice to Have):**
- Memory system
- Streaming
- Advanced routing

### Running Ahead?

**Enhancement Ideas:**
- Add more tools (weather, news, etc.)
- Implement async/await
- Add configuration file support
- Create web interface with FastAPI
- Add vector memory with embeddings

---

## 📊 Progress Tracking

### Checkpoints:

- [ ] **Checkpoint 1** (30 min): Agent responds to queries
- [ ] **Checkpoint 2** (60 min): Tools work with agent
- [ ] **Checkpoint 3** (90 min): Multi-agent routing works
- [ ] **Checkpoint 4** (120 min): CLI fully functional
- [ ] **Checkpoint 5** (150 min): Memory & advanced features
- [ ] **Checkpoint 6** (180 min): Package ready for deployment

### Success Metrics:

```bash
# All these should work:
indusagi version
indusagi run "Calculate 50 * 2"
indusagi interactive
pytest tests/ -v
```

---

**Next**: Open **02-ARCHITECTURE.md** for design details
