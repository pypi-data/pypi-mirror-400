# Implementation Guide: Step-by-Step Coding Instructions

## 🎯 This Guide

Follow these step-by-step instructions during your live coding session. Each section has:
- ✅ Clear objectives
- 📝 Complete code to type/paste
- 🧪 Test commands
- ✓ Checkpoint to verify

---

## 📋 Pre-Flight Checklist

Before starting, verify:

```bash
# Check Python version (need 3.9+)
python --version

# Check pip/uv installed
uv --version || pip install uv

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"
# Windows PowerShell: $env:ANTHROPIC_API_KEY="your-api-key-here"

# Verify API key is set
python -c "import os; print('✓ API key set' if os.getenv('ANTHROPIC_API_KEY') else '✗ API key missing')"
```

---

## STEP 1: Project Initialization (5 minutes)

### Create Project Structure

```bash
# Create project with UV
uv init --package indusagi
cd indusagi

# Your structure should look like:
# indusagi/
# ├── pyproject.toml
# ├── README.md
# └── src/
#     └── indusagi/
#         └── __init__.py
```

### Install Dependencies

```bash
# Core dependencies
uv add anthropic typer rich pydantic python-dotenv

# Dev dependencies
uv add --dev pytest pytest-asyncio black ruff

# Verify installation
uv pip list | grep anthropic
```

### Configure pyproject.toml

Edit `pyproject.toml` to add:

```toml
[project]
name = "indusagi"
version = "0.1.0"
description = "AI indus-agents with multi-agent orchestration"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "anthropic>=0.35.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
indusagi = "indusagi.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.black]
line-length = 100
target-version = ['py39']

[tool.ruff]
line-length = 100
target-version = "py39"
```

### Install in Editable Mode

```bash
# This is KEY for fast iteration!
uv pip install -e .

# Test that it worked
indusagi --help
# Should show: "Usage: indusagi [OPTIONS] COMMAND [ARGS]..."
```

### 🧪 Test Checkpoint 1

```bash
# All these should work:
uv pip list | grep anthropic  # Should show anthropic package
indusagi --help               # Should show help (even if empty)
python -c "import indusagi; print('✓ Package imports')"
```

✅ **Checkpoint 1 Complete**: Project structure created, dependencies installed, editable mode working

---

## STEP 2: Core Agent Class (20 minutes)

### Create src/indusagi/agent.py

```python
"""
Core Agent class for LLM interaction.
"""
from typing import Optional, List, Dict
from anthropic import Anthropic
from pydantic import BaseModel, Field
import os


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    model: str = Field(default="claude-sonnet-4-5-20250929")
    max_tokens: int = Field(default=1024, ge=100, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)

    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        return cls(
            model=os.getenv("AGENT_MODEL", "claude-sonnet-4-5-20250929")
        )


class Agent:
    """
    AI Agent that interacts with LLM APIs.

    Attributes:
        name: Agent's identifier
        role: Agent's specialized role/purpose
        config: Configuration settings
        client: Anthropic API client
        messages: Conversation history
    """

    def __init__(
        self,
        name: str,
        role: str,
        config: Optional[AgentConfig] = None,
        system_prompt: Optional[str] = None,
    ):
        self.name = name
        self.role = role
        self.config = config or AgentConfig.from_env()
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.messages: List[Dict[str, str]] = []
        self.system_prompt = system_prompt or f"You are {name}, a helpful AI assistant. Your role is: {role}"

    def process(self, user_input: str) -> str:
        """
        Process user input and return agent response.

        Args:
            user_input: User's query or message

        Returns:
            Agent's response text

        Raises:
            Exception: If API call fails
        """
        # Add user message
        self.messages.append({"role": "user", "content": user_input})

        try:
            # Call API
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.system_prompt,
                messages=self.messages,
            )

            # Extract response text
            assistant_message = response.content[0].text

            # Add to history
            self.messages.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            print(f"[Agent {self.name}] {error_msg}")
            return error_msg

    def clear_history(self):
        """Clear conversation history."""
        self.messages = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.messages.copy()


# Quick test when run directly
if __name__ == "__main__":
    agent = Agent(name="TestAgent", role="Testing assistant")
    response = agent.process("Say 'Hello, world!' and nothing else.")
    print(f"Agent response: {response}")
```

### 🧪 Test Agent

```bash
# Test directly
python src/indusagi/agent.py

# Should output something like:
# Agent response: Hello, world!

# Test in Python REPL
python -c "
from indusagi.agent import Agent
agent = Agent('Test', 'Helper')
print(agent.process('What is 2+2?'))
"
```

✅ **Checkpoint 2 Complete**: Agent class works, can communicate with LLM

---

## STEP 3: Tool Registry System (20 minutes)

### Create src/indusagi/tools.py

```python
"""
Tool registry and management system.
"""
from typing import Callable, Dict, Any, List
import inspect
from datetime import datetime


class ToolRegistry:
    """
    Registry for agent tools with auto-schema generation.

    Tools are functions that agents can call to perform actions.
    The registry automatically generates JSON schemas from function
    signatures for LLM function calling.
    """

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._schemas: List[dict] = []

    def register(self, func: Callable) -> Callable:
        """
        Decorator to register a function as a tool.

        Usage:
            @registry.register
            def my_tool(param: str) -> str:
                '''Tool description.'''
                return f"Result: {param}"

        Args:
            func: Function to register as tool

        Returns:
            The original function (unchanged)
        """
        self.tools[func.__name__] = func

        # Generate schema from function signature
        schema = self._generate_schema(func)
        self._schemas.append(schema)

        return func

    def _generate_schema(self, func: Callable) -> dict:
        """
        Generate Anthropic tool schema from function signature.

        Args:
            func: Function to generate schema for

        Returns:
            Tool schema dict compatible with Anthropic API
        """
        sig = inspect.signature(func)
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Determine type
            param_type = "string"  # default
            if param.annotation != inspect.Parameter.empty:
                param_type = type_map.get(param.annotation, "string")

            properties[param_name] = {"type": param_type}

            # Check if required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "name": func.__name__,
            "description": inspect.getdoc(func) or f"Execute {func.__name__}",
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    @property
    def schemas(self) -> List[dict]:
        """Get all tool schemas for API calls."""
        return self._schemas

    def execute(self, name: str, **kwargs) -> Any:
        """
        Execute a tool by name with given arguments.

        Args:
            name: Name of tool to execute
            **kwargs: Arguments to pass to tool

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found. Available: {list(self.tools.keys())}")

        try:
            return self.tools[name](**kwargs)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"

    def list_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self.tools.keys())


# Global registry instance
registry = ToolRegistry()


# ============ Built-in Tools ============


@registry.register
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.

    SAFE for basic math. DO NOT use for arbitrary code execution.

    Args:
        expression: Mathematical expression like "2+2" or "10*5"

    Returns:
        Result of calculation as string
    """
    try:
        # Basic safety: only allow numbers and operators
        allowed_chars = set("0123456789+-*/() .")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"

        result = eval(expression)  # Safe for math only!
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"


@registry.register
def get_time() -> str:
    """
    Get the current time.

    Returns:
        Current time in HH:MM:SS format
    """
    return datetime.now().strftime("%H:%M:%S")


@registry.register
def get_date() -> str:
    """
    Get the current date.

    Returns:
        Current date in YYYY-MM-DD format
    """
    return datetime.now().strftime("%Y-%m-%d")


# Quick test
if __name__ == "__main__":
    print("Registered tools:", registry.list_tools())
    print("\nTesting calculator:", registry.execute("calculator", expression="25 * 4"))
    print("Testing get_time:", registry.execute("get_time"))
    print("Testing get_date:", registry.execute("get_date"))
    print("\nTool schemas generated:")
    for schema in registry.schemas:
        print(f"  - {schema['name']}: {schema['description']}")
```

### 🧪 Test Tools

```bash
# Test directly
python src/indusagi/tools.py

# Expected output:
# Registered tools: ['calculator', 'get_time', 'get_date']
# Testing calculator: 100
# Testing get_time: 14:23:45
# Testing get_date: 2025-01-07
# Tool schemas generated:
#   - calculator: Evaluate a mathematical expression...
#   - get_time: Get the current time...
#   - get_date: Get the current date...
```

✅ **Checkpoint 3 Complete**: Tools register, schemas generate, execution works

---

## STEP 4: Agent + Tools Integration (15 minutes)

### Update src/indusagi/agent.py

Add this method to the `Agent` class:

```python
    def process_with_tools(self, user_input: str, max_turns: int = 5) -> str:
        """
        Process user input with tool support.

        The agent can use tools iteratively to solve problems.

        Args:
            user_input: User's query
            max_turns: Maximum tool-calling iterations

        Returns:
            Final agent response
        """
        from .tools import registry

        # Add user message
        self.messages.append({"role": "user", "content": user_input})

        for turn in range(max_turns):
            try:
                # Call API with tools
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    system=self.system_prompt,
                    tools=registry.schemas,
                    messages=self.messages,
                )

                # Check stop reason
                if response.stop_reason == "end_turn":
                    # Final answer - no tools needed
                    text_content = [
                        block.text for block in response.content if hasattr(block, "text")
                    ]
                    final_text = " ".join(text_content)
                    self.messages.append({"role": "assistant", "content": final_text})
                    return final_text

                elif response.stop_reason == "tool_use":
                    # Agent wants to use tools
                    self.messages.append({"role": "assistant", "content": response.content})

                    # Execute all requested tools
                    tool_results = []
                    for content in response.content:
                        if content.type == "tool_use":
                            print(f"[{self.name}] Using tool: {content.name}")
                            result = registry.execute(content.name, **content.input)
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": str(result),
                                }
                            )

                    # Add tool results as user message
                    self.messages.append({"role": "user", "content": tool_results})

                else:
                    # Unexpected stop reason
                    return f"Unexpected stop reason: {response.stop_reason}"

            except Exception as e:
                error_msg = f"Error in tool loop: {str(e)}"
                print(f"[Agent {self.name}] {error_msg}")
                return error_msg

        return "Maximum turns reached without final answer"
```

### 🧪 Test Agent with Tools

Create `test_agent_tools.py` in project root:

```python
"""Quick test script for agent + tools."""
from indusagi.agent import Agent

def test_calculator():
    agent = Agent("MathBot", "Mathematical assistant")
    result = agent.process_with_tools("What is 144 divided by 12?")
    print(f"Math test: {result}")
    assert "12" in result

def test_time():
    agent = Agent("TimeBot", "Time assistant")
    result = agent.process_with_tools("What time is it?")
    print(f"Time test: {result}")
    # Should contain time in some format

def test_multi_tool():
    agent = Agent("MultiBot", "General assistant")
    result = agent.process_with_tools("What's the date today and what's 50 times 2?")
    print(f"Multi-tool test: {result}")

if __name__ == "__main__":
    print("Testing agent with tools...\n")
    test_calculator()
    print()
    test_time()
    print()
    test_multi_tool()
    print("\n✓ All tests passed!")
```

```bash
python test_agent_tools.py
```

✅ **Checkpoint 4 Complete**: Agent successfully uses tools to answer questions

---

## STEP 5: Multi-Agent Orchestrator (20 minutes)

### Create src/indusagi/orchestrator.py

```python
"""
Multi-agent orchestration and routing.
"""
from typing import Dict
from .agent import Agent, AgentConfig


class Orchestrator:
    """
    Orchestrates multiple specialized agents.

    Routes user queries to the most appropriate agent based on content analysis.
    """

    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.agents: Dict[str, Agent] = {}
        self._setup_agents()

    def _setup_agents(self):
        """Initialize specialized agents."""

        # General purpose agent
        self.agents["general"] = Agent(
            name="GeneralAgent",
            role="General purpose assistant for varied queries",
            config=self.config,
            system_prompt="""You are a helpful general-purpose AI assistant.
You can answer questions, have conversations, and help with various tasks.""",
        )

        # Math specialist
        self.agents["math"] = Agent(
            name="MathExpert",
            role="Mathematical calculations and problem solving",
            config=self.config,
            system_prompt="""You are a mathematical expert assistant.
You excel at calculations, math problems, and quantitative analysis.
Use the calculator tool for precise calculations.""",
        )

        # Time/date specialist
        self.agents["time"] = Agent(
            name="TimeKeeper",
            role="Time and date information",
            config=self.config,
            system_prompt="""You are a time and date specialist.
You provide current time, date, and calendar information.
Use the get_time and get_date tools to provide accurate information.""",
        )

    def route(self, user_input: str, verbose: bool = False) -> str:
        """
        Route user input to appropriate agent.

        Uses keyword-based routing to select specialist agents.

        Args:
            user_input: User's query
            verbose: Print routing information

        Returns:
            Agent's response
        """
        # Analyze input
        input_lower = user_input.lower()
        selected_agent = self._select_agent(input_lower)

        if verbose:
            print(f"[Orchestrator] Routing to: {selected_agent.name}")

        # Process with selected agent
        return selected_agent.process_with_tools(user_input)

    def _select_agent(self, input_text: str) -> Agent:
        """
        Select best agent based on input content.

        Args:
            input_text: Lowercased user input

        Returns:
            Selected agent instance
        """
        # Math keywords
        math_keywords = [
            "calculate",
            "math",
            "compute",
            "multiply",
            "divide",
            "add",
            "subtract",
            "+",
            "-",
            "*",
            "/",
            "equation",
            "solve",
        ]

        # Time keywords
        time_keywords = [
            "time",
            "date",
            "clock",
            "today",
            "now",
            "when",
            "day",
            "hour",
            "minute",
        ]

        # Score each agent
        math_score = sum(1 for kw in math_keywords if kw in input_text)
        time_score = sum(1 for kw in time_keywords if kw in input_text)

        # Select based on scores
        if math_score > 0 and math_score >= time_score:
            return self.agents["math"]
        elif time_score > 0:
            return self.agents["time"]
        else:
            return self.agents["general"]

    def list_agents(self) -> list[str]:
        """Get list of available agent names."""
        return list(self.agents.keys())


# Quick test
if __name__ == "__main__":
    orchestrator = Orchestrator()

    print("Available agents:", orchestrator.list_agents())
    print("\nTest 1: Math query")
    result1 = orchestrator.route("What is 25 multiplied by 4?", verbose=True)
    print(f"Result: {result1}\n")

    print("Test 2: Time query")
    result2 = orchestrator.route("What time is it?", verbose=True)
    print(f"Result: {result2}\n")

    print("Test 3: General query")
    result3 = orchestrator.route("Tell me a fun fact", verbose=True)
    print(f"Result: {result3}")
```

### 🧪 Test Orchestrator

```bash
python src/indusagi/orchestrator.py

# Should show:
# [Orchestrator] Routing to: MathExpert
# Result: 100
# [Orchestrator] Routing to: TimeKeeper
# Result: The current time is...
```

✅ **Checkpoint 5 Complete**: Orchestrator routes to appropriate agents

---

## STEP 6: CLI Interface (20 minutes)

### Create src/indusagi/cli.py

```python
"""
Command-line interface for indus-agents.
"""
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from typing import Optional
import os

from .orchestrator import Orchestrator
from .agent import AgentConfig

app = typer.Typer(
    help="indus-agents - Multi-agent system with tool support",
    add_completion=False,
)
console = Console()


def check_api_key() -> bool:
    """Check if API key is configured."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print(
            Panel(
                "[red]Error: ANTHROPIC_API_KEY environment variable not set[/red]\n\n"
                "Please set your API key:\n"
                "  export ANTHROPIC_API_KEY='your-key-here'\n\n"
                "Or on Windows PowerShell:\n"
                "  $env:ANTHROPIC_API_KEY='your-key-here'",
                title="API Key Missing",
                border_style="red",
            )
        )
        return False
    return True


@app.command()
def run(
    prompt: str = typer.Argument(..., help="Prompt for the agent"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show routing information"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model"),
):
    """
    Run a single query through indus-agents.

    Example:
        indusagi run "What is 50 * 2?"
    """
    if not check_api_key():
        raise typer.Exit(1)

    try:
        # Create config
        config = AgentConfig()
        if model:
            config.model = model

        # Create orchestrator
        orchestrator = Orchestrator(config)

        # Process query
        with console.status("[bold green]Processing..."):
            response = orchestrator.route(prompt, verbose=verbose)

        # Display response
        console.print("\n[bold cyan]Response:[/bold cyan]")
        console.print(Panel(Markdown(response), border_style="cyan"))

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def interactive(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show routing information"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model"),
):
    """
    Start an interactive chat session.

    Example:
        indusagi interactive
    """
    if not check_api_key():
        raise typer.Exit(1)

    # Welcome message
    console.print(
        Panel(
            "[bold green]Welcome to indus-agents Interactive Mode[/bold green]\n\n"
            "Type your queries and press Enter.\n"
            "Commands:\n"
            "  • 'quit' or 'exit' - Exit the session\n"
            "  • 'clear' - Clear conversation history\n"
            "  • 'agents' - List available agents",
            title="Interactive Session",
            border_style="green",
        )
    )

    try:
        # Create config
        config = AgentConfig()
        if model:
            config.model = model

        # Create orchestrator
        orchestrator = Orchestrator(config)

        # Main loop
        while True:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")

            # Handle commands
            if user_input.lower() in ["quit", "exit"]:
                console.print("[dim]Goodbye![/dim]")
                break
            elif user_input.lower() == "clear":
                for agent in orchestrator.agents.values():
                    agent.clear_history()
                console.print("[dim]Conversation history cleared[/dim]")
                continue
            elif user_input.lower() == "agents":
                console.print("\n[bold]Available Agents:[/bold]")
                for name in orchestrator.list_agents():
                    console.print(f"  • {name}")
                continue

            # Process query
            try:
                with console.status("[bold green]Thinking..."):
                    response = orchestrator.route(user_input, verbose=verbose)

                console.print(f"\n[bold green]Agent:[/bold green] {response}")

            except Exception as e:
                console.print(f"\n[red]Error:[/red] {str(e)}")

    except KeyboardInterrupt:
        console.print("\n\n[dim]Session interrupted. Goodbye![/dim]")
        raise typer.Exit(0)


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"\n[bold]indusagi[/bold] v{__version__}")
    console.print("Python indus-agents with multi-agent orchestration\n")


@app.command()
def list_tools():
    """List all available tools."""
    from .tools import registry

    console.print("\n[bold]Available Tools:[/bold]\n")
    for schema in registry.schemas:
        console.print(f"  [cyan]•[/cyan] [bold]{schema['name']}[/bold]")
        console.print(f"    {schema['description']}")
    console.print()


@app.command()
def test_connection():
    """Test API connection."""
    if not check_api_key():
        raise typer.Exit(1)

    try:
        with console.status("[bold green]Testing connection..."):
            from .agent import Agent

            agent = Agent("TestAgent", "Connection tester")
            response = agent.process("Respond with just 'OK' if you can read this.")

        if response:
            console.print("\n[green]✓ API connection successful[/green]")
            console.print(f"Response: {response}\n")
        else:
            console.print("\n[red]✗ API connection failed[/red]\n")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"\n[red]✗ Error:[/red] {str(e)}\n")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
```

### Update src/indusagi/__init__.py

```python
"""
indus-agents - Multi-agent indus-agents with tool support.
"""

__version__ = "0.1.0"

from .agent import Agent, AgentConfig
from .tools import registry
from .orchestrator import Orchestrator

__all__ = ["Agent", "AgentConfig", "registry", "Orchestrator", "__version__"]
```

### 🧪 Test CLI

```bash
# Reinstall to register CLI commands
uv pip install -e .

# Test all commands
indusagi version
indusagi list-tools
indusagi test-connection
indusagi run "What is 100 divided by 4?"
indusagi interactive

# In interactive mode, try:
# > What time is it?
# > Calculate 25 * 4
# > agents
# > clear
# > quit
```

✅ **Checkpoint 6 Complete**: Full CLI working with all commands

---

## STEP 7: Testing (15 minutes)

### Create tests/test_agent.py

```python
"""Tests for Agent class."""
import pytest
from indusagi.agent import Agent, AgentConfig


def test_agent_creation():
    """Test agent can be created."""
    agent = Agent(name="TestAgent", role="Tester")
    assert agent.name == "TestAgent"
    assert agent.role == "Tester"
    assert len(agent.messages) == 0


def test_agent_config():
    """Test agent configuration."""
    config = AgentConfig(model="test-model", max_tokens=500)
    agent = Agent("Test", "Tester", config=config)
    assert agent.config.model == "test-model"
    assert agent.config.max_tokens == 500


def test_clear_history():
    """Test clearing conversation history."""
    agent = Agent("Test", "Tester")
    agent.messages = [{"role": "user", "content": "test"}]
    assert len(agent.messages) == 1
    agent.clear_history()
    assert len(agent.messages) == 0
```

### Create tests/test_tools.py

```python
"""Tests for tool system."""
import pytest
from indusagi.tools import registry


def test_tool_registration():
    """Test tools are registered."""
    assert "calculator" in registry.tools
    assert "get_time" in registry.tools
    assert "get_date" in registry.tools


def test_calculator_tool():
    """Test calculator tool."""
    result = registry.execute("calculator", expression="2+2")
    assert "4" in result

    result = registry.execute("calculator", expression="10*5")
    assert "50" in result


def test_time_tools():
    """Test time and date tools."""
    time_result = registry.execute("get_time")
    assert ":" in time_result  # Should have time format

    date_result = registry.execute("get_date")
    assert "-" in date_result  # Should have date format


def test_invalid_tool():
    """Test error handling for invalid tool."""
    with pytest.raises(ValueError):
        registry.execute("nonexistent_tool")


def test_calculator_safety():
    """Test calculator rejects dangerous input."""
    result = registry.execute("calculator", expression="import os")
    assert "Error" in result or "invalid" in result.lower()
```

### Create tests/test_orchestrator.py

```python
"""Tests for orchestrator."""
import pytest
from indusagi.orchestrator import Orchestrator


def test_orchestrator_creation():
    """Test orchestrator can be created."""
    orchestrator = Orchestrator()
    assert len(orchestrator.agents) == 3
    assert "general" in orchestrator.agents
    assert "math" in orchestrator.agents
    assert "time" in orchestrator.agents


def test_list_agents():
    """Test listing agents."""
    orchestrator = Orchestrator()
    agents = orchestrator.list_agents()
    assert isinstance(agents, list)
    assert len(agents) == 3
```

### Create tests/conftest.py

```python
"""Pytest configuration and fixtures."""
import pytest
import os


@pytest.fixture(autouse=True)
def check_api_key():
    """Ensure API key is set for tests."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")
```

### 🧪 Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/indusagi --cov-report=term-missing

# Expected output:
# tests/test_agent.py::test_agent_creation PASSED
# tests/test_agent.py::test_agent_config PASSED
# tests/test_tools.py::test_tool_registration PASSED
# tests/test_tools.py::test_calculator_tool PASSED
# ...
```

✅ **Checkpoint 7 Complete**: Test suite passes

---

## STEP 8: Documentation & Packaging (10 minutes)

### Update README.md

```markdown
# indus-agents

indus-agents with multi-agent orchestration and tool support.

## Features

- 🤖 Multiple specialized agents (General, Math, Time)
- 🛠️ Extensible tool system with auto-schema generation
- 💬 Conversation memory management
- 🎨 Beautiful CLI with Rich formatting
- ✅ Type-safe with Pydantic
- 🧪 Comprehensive test suite

## Installation

\`\`\`bash
pip install -e .
\`\`\`

## Quick Start

\`\`\`bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run a query
indusagi run "What is 50 * 2?"

# Interactive mode
indusagi interactive

# List available tools
indusagi list-tools
\`\`\`

## Usage Examples

\`\`\`python
from indusagi import Agent, Orchestrator

# Single agent
agent = Agent("Helper", "General assistant")
response = agent.process("Hello!")

# With tools
response = agent.process_with_tools("Calculate 25 * 4")

# Multi-agent orchestration
orchestrator = Orchestrator()
response = orchestrator.route("What time is it?")
\`\`\`

## CLI Commands

- `indusagi run "query"` - Single query
- `indusagi interactive` - Interactive chat
- `indusagi list-tools` - Show available tools
- `indusagi test-connection` - Test API
- `indusagi version` - Version info

## Development

\`\`\`bash
# Install in editable mode
pip install -e .

# Run tests
pytest tests/ -v

# Format code
black src/ tests/

# Lint
ruff check src/ tests/
\`\`\`

## License

MIT
```

### Create .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Environment
.env
.env.local
```

### 🧪 Final Validation

```bash
# Complete system test
indusagi test-connection
indusagi run "What's 144 / 12 and what time is it?"
pytest tests/ -v

# Build package
uv build

# Check dist/
ls dist/
# Should see: indusagi-0.1.0.tar.gz and .whl file
```

✅ **Checkpoint 8 Complete**: Fully packaged and documented!

---

## 🎉 Congratulations!

You've built a complete indus-agents with:
- ✅ Multi-agent orchestration
- ✅ Tool calling system
- ✅ Professional CLI
- ✅ Test suite
- ✅ Package ready for distribution

---

## 📚 Next Steps

### Immediate Enhancements:
1. Add more tools (weather, web search, file operations)
2. Implement conversation memory persistence
3. Add configuration file support
4. Create more specialized agents

### Week 1:
- Add async/await support
- Implement streaming responses
- Add retry logic and error handling
- Create comprehensive documentation

### Month 1:
- Vector memory with embeddings
- RAG (Retrieval Augmented Generation)
- Web interface with FastAPI
- Deploy to production

---

**Next**: See **06-QUICK-REFERENCE.md** for code snippets and troubleshooting
