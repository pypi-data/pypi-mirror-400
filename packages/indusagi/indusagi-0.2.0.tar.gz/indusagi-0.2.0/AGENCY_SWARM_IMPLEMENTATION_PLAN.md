# Implementation Plan: Adding Agency Swarm Capabilities to indus-agents

## Executive Summary

This document provides a detailed, actionable plan to transform indus-agents into a full-featured multi-agent framework capable of generating Agency Swarm-style agents with true inter-agent communication, handoffs, and sophisticated tooling.

---

## 1. Current State Analysis

### What indus-agents Has
- ✅ Clean Agent class with OpenAI integration
- ✅ Tool registry with decorator-based registration
- ✅ Multi-agent orchestrator (keyword routing)
- ✅ Comprehensive memory system
- ✅ Professional CLI with Rich formatting
- ✅ Type safety with Pydantic

### What indus-agents Lacks
- ❌ True multi-agent handoffs
- ❌ Agency orchestration class
- ❌ Agent generation/scaffolding CLI
- ❌ Instruction template system
- ❌ Development tools (Bash, Git, Glob, Grep)
- ❌ Hook system for lifecycle events
- ❌ Shared context across agents

---

## 2. Implementation Phases

### Phase 1: Agent Generation System

#### 1.1 Create Agent Template Structure

**New Directory: `src/indusagi/templates/`**

```
templates/
├── __init__.py
├── renderer.py              # Template rendering with placeholders
├── scaffolder.py            # Agent scaffolding logic
└── agent_template/
    ├── __init__.py.template
    ├── {agent_name}.py.template
    └── instructions.md.template
```

#### 1.2 Template Renderer Implementation

**File: `src/indusagi/templates/renderer.py`**

```python
import os
import platform
from datetime import datetime
from typing import Dict, Any, Optional


def render_instructions(
    template_path: str,
    model: str = "gpt-4o",
    extra_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Render instructions template with placeholders replaced.

    Placeholders:
        {cwd} - Current working directory
        {is_git_repo} - Whether current dir is a git repo
        {platform} - OS platform (Linux, Darwin, Windows)
        {os_version} - OS version string
        {today} - Current date (YYYY-MM-DD)
        {model} - Model name being used
    """
    with open(template_path, "r") as f:
        content = f.read()

    placeholders = {
        "{cwd}": os.getcwd(),
        "{is_git_repo}": str(os.path.isdir(os.path.join(os.getcwd(), ".git"))),
        "{platform}": platform.system(),
        "{os_version}": platform.release(),
        "{today}": datetime.now().strftime("%Y-%m-%d"),
        "{model}": model,
    }

    if extra_context:
        for key, value in extra_context.items():
            placeholders[f"{{{key}}}"] = str(value)

    for key, value in placeholders.items():
        content = content.replace(key, value)

    return content
```

#### 1.3 Agent Scaffolder

**File: `src/indusagi/templates/scaffolder.py`**

```python
import os
import re
from typing import Optional
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_class_name(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return ''.join(word.capitalize() for word in name.split('_'))


def scaffold_agent(
    name: str,
    output_dir: str = ".",
    description: str = "A specialized agent",
    tools: Optional[list] = None
) -> str:
    """
    Scaffold a new agent directory with all necessary files.

    Args:
        name: Agent name (e.g., 'qa_tester' or 'QATester')
        output_dir: Where to create the agent directory
        description: Agent description for instructions
        tools: List of tool names to include

    Returns:
        Path to created agent directory
    """
    snake_name = to_snake_case(name)
    class_name = to_class_name(snake_name)

    # Create agent directory
    agent_dir = Path(output_dir) / f"{snake_name}_agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_content = f'''"""
{class_name} Agent - {description}
"""
from .{snake_name}_agent import create_{snake_name}_agent

__all__ = ["create_{snake_name}_agent"]
'''
    (agent_dir / "__init__.py").write_text(init_content)

    # Create agent factory file
    tools_list = tools or ["Read", "Write", "Bash"]
    tools_import = ", ".join(tools_list)

    agent_content = f'''"""
{class_name} Agent Factory

This module provides the factory function for creating {class_name} instances.
"""
import os
from typing import Optional

from indusagi import Agent, AgentConfig
from indusagi.templates import render_instructions
from indusagi.tools.dev import {tools_import}

current_dir = os.path.dirname(os.path.abspath(__file__))


def create_{snake_name}_agent(
    model: str = "gpt-4o",
    config: Optional[AgentConfig] = None,
    reasoning_effort: str = "medium"
) -> Agent:
    """
    Factory that returns a fresh {class_name} instance.

    Args:
        model: The LLM model to use
        config: Optional agent configuration
        reasoning_effort: Reasoning effort level (low, medium, high)

    Returns:
        Configured Agent instance
    """
    instructions = render_instructions(
        os.path.join(current_dir, "instructions.md"),
        model=model
    )

    agent_config = config or AgentConfig.from_env()
    agent_config.model = model

    return Agent(
        name="{class_name}",
        role="{description}",
        config=agent_config,
        system_prompt=instructions,
        tools=[{tools_import}],
    )
'''
    (agent_dir / f"{snake_name}_agent.py").write_text(agent_content)

    # Create instructions.md
    instructions_content = f'''# {class_name} Agent

You are a {class_name} - {description}.

## Role and Objective

[Describe the agent's primary function and mission]

## Instructions

1. Be concise and direct in your responses
2. Use available tools appropriately
3. Follow existing code patterns and conventions
4. Do not create unnecessary files

## Communication Guidelines

- Use GitHub-flavored markdown for formatting
- Provide clear, actionable information
- Ask clarifying questions when requirements are ambiguous

## Handoff Guidelines

When you need assistance from another agent:
- Provide comprehensive context
- Explain what you've tried
- Specify what help you need

## Environment

<env>
Working directory: {{cwd}}
Is directory a git repo: {{is_git_repo}}
Platform: {{platform}}
OS Version: {{os_version}}
Today's date: {{today}}
Model Name: {{model}}
</env>
'''
    (agent_dir / "instructions.md").write_text(instructions_content)

    return str(agent_dir)
```

#### 1.4 CLI Command for Agent Creation

**Add to: `src/indusagi/cli.py`**

```python
@app.command("create-agent")
def create_agent_cmd(
    name: str = typer.Argument(..., help="Name of the agent (e.g., 'qa_tester')"),
    template: str = typer.Option("default", "--template", "-t", help="Template to use"),
    output: str = typer.Option("./agents", "--output", "-o", help="Output directory"),
    description: str = typer.Option("A specialized agent", "--description", "-d"),
):
    """Create a new agent from template."""
    from indusagi.templates.scaffolder import scaffold_agent

    console.print(f"[bold blue]Creating agent: {name}[/bold blue]")

    try:
        agent_path = scaffold_agent(
            name=name,
            output_dir=output,
            description=description
        )
        console.print(f"[green]✓ Agent created at: {agent_path}[/green]")
        console.print("\nNext steps:")
        console.print("  1. Edit instructions.md to customize behavior")
        console.print("  2. Add agent-specific tools if needed")
        console.print("  3. Import in your agency.py")
    except Exception as e:
        console.print(f"[red]Error creating agent: {e}[/red]")
        raise typer.Exit(1)
```

---

### Phase 2: Agency Orchestration System

#### 2.1 Agency Class Implementation

**New File: `src/indusagi/agency.py`**

```python
"""
Agency - Multi-Agent Orchestration System

Provides Agency Swarm-like orchestration for indus-agents.
"""
import os
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from indusagi.agent import Agent


class HandoffType(Enum):
    """Types of agent handoff mechanisms."""
    MESSAGE = "message"
    FULL_CONTEXT = "full_context"


@dataclass
class HandoffResult:
    """Result of an agent handoff."""
    success: bool
    response: str
    from_agent: str
    to_agent: str
    processing_time: float
    error: Optional[str] = None


@dataclass
class AgencyResponse:
    """Response from agency processing."""
    response: str
    agents_used: List[str]
    handoffs: List[HandoffResult]
    total_time: float
    final_agent: str


class Agency:
    """
    Multi-agent orchestration system with defined communication flows.

    Similar to Agency Swarm's Agency class, this manages multiple agents
    and their inter-communication patterns.

    Example:
        >>> planner = create_planner_agent()
        >>> coder = create_coder_agent()
        >>> agency = Agency(
        ...     entry_agent=coder,
        ...     agents=[coder, planner],
        ...     communication_flows=[
        ...         (coder, planner),  # coder can hand off to planner
        ...         (planner, coder),  # planner can hand off to coder
        ...     ],
        ...     name="DevAgency",
        ...     shared_instructions="./project-overview.md"
        ... )
        >>> response = agency.process("Build a REST API")
    """

    def __init__(
        self,
        entry_agent: Agent,
        agents: Optional[List[Agent]] = None,
        communication_flows: Optional[List[Tuple[Agent, Agent]]] = None,
        shared_instructions: Optional[str] = None,
        name: str = "Agency",
        max_handoffs: int = 10,
    ):
        """
        Initialize an Agency.

        Args:
            entry_agent: The agent that receives initial user input
            agents: List of all agents in the agency
            communication_flows: List of (source, target) tuples defining allowed handoffs
            shared_instructions: Path to shared instructions file
            name: Name of this agency
            max_handoffs: Maximum number of handoffs allowed per request
        """
        self.entry_agent = entry_agent
        self.name = name
        self.max_handoffs = max_handoffs

        # Build agent registry
        self.agents = agents or [entry_agent]
        self._agent_map: Dict[str, Agent] = {a.name: a for a in self.agents}

        # Build communication graph
        self._flows: Dict[str, List[str]] = {}
        if communication_flows:
            for source, target in communication_flows:
                if source.name not in self._flows:
                    self._flows[source.name] = []
                self._flows[source.name].append(target.name)

        # Load shared instructions
        self._shared_context = ""
        if shared_instructions and os.path.exists(shared_instructions):
            with open(shared_instructions, "r") as f:
                self._shared_context = f.read()

        # Shared state across all agents
        self._shared_state: Dict[str, Any] = {}

        # Handoff history for current request
        self._handoff_history: List[HandoffResult] = []

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        return self._agent_map.get(name)

    def list_agents(self) -> List[str]:
        """List all agent names in the agency."""
        return list(self._agent_map.keys())

    def can_handoff(self, from_agent: str, to_agent: str) -> bool:
        """Check if handoff is allowed between agents."""
        return to_agent in self._flows.get(from_agent, [])

    def get_allowed_handoffs(self, agent_name: str) -> List[str]:
        """Get list of agents this agent can hand off to."""
        return self._flows.get(agent_name, [])

    def handoff(
        self,
        from_agent: Agent,
        to_agent_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> HandoffResult:
        """
        Execute a handoff from one agent to another.

        Args:
            from_agent: The agent initiating the handoff
            to_agent_name: Name of the target agent
            message: Message to pass to target agent
            context: Optional additional context

        Returns:
            HandoffResult with response and metadata
        """
        start_time = time.time()

        if not self.can_handoff(from_agent.name, to_agent_name):
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=0,
                error=f"Handoff from {from_agent.name} to {to_agent_name} not allowed"
            )

        target = self._agent_map.get(to_agent_name)
        if not target:
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=0,
                error=f"Agent {to_agent_name} not found"
            )

        # Build handoff message with context
        full_message = f"[Handoff from {from_agent.name}]\n\n{message}"

        if self._shared_context:
            full_message = f"[Shared Project Context]\n{self._shared_context}\n\n{full_message}"

        if context:
            context_str = "\n".join(f"- {k}: {v}" for k, v in context.items())
            full_message += f"\n\n[Additional Context]\n{context_str}"

        try:
            response = target.process(full_message)
            processing_time = time.time() - start_time

            result = HandoffResult(
                success=True,
                response=response,
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=processing_time
            )
            self._handoff_history.append(result)
            return result

        except Exception as e:
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def process(self, user_input: str, use_tools: bool = True) -> AgencyResponse:
        """
        Process user input through the agency.

        Starts with entry_agent and handles any handoffs.

        Args:
            user_input: The user's request
            use_tools: Whether to enable tool usage

        Returns:
            AgencyResponse with full processing details
        """
        start_time = time.time()
        self._handoff_history = []
        agents_used = [self.entry_agent.name]

        # Add shared context to initial message
        full_input = user_input
        if self._shared_context:
            full_input = f"[Project Context]\n{self._shared_context}\n\n[User Request]\n{user_input}"

        # Process with entry agent
        response = self.entry_agent.process(full_input)

        return AgencyResponse(
            response=response,
            agents_used=agents_used,
            handoffs=self._handoff_history,
            total_time=time.time() - start_time,
            final_agent=agents_used[-1]
        )

    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """Get a value from shared state."""
        return self._shared_state.get(key, default)

    def set_shared_state(self, key: str, value: Any) -> None:
        """Set a value in shared state."""
        self._shared_state[key] = value

    def clear_shared_state(self) -> None:
        """Clear all shared state."""
        self._shared_state = {}

    def terminal_demo(self, show_reasoning: bool = False):
        """
        Run interactive terminal demo.

        Args:
            show_reasoning: Whether to show agent reasoning
        """
        print(f"\n{'='*60}")
        print(f"  {self.name} - Interactive Demo")
        print(f"  Agents: {', '.join(self.list_agents())}")
        print(f"  Entry: {self.entry_agent.name}")
        print(f"{'='*60}\n")

        print("Commands:")
        print("  /quit, /exit  - Exit the demo")
        print("  /agents       - List all agents")
        print("  /handoffs     - Show allowed handoffs")
        print("  /clear        - Clear conversation history")
        print()

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["/quit", "/exit"]:
                    print("Goodbye!")
                    break

                if user_input.lower() == "/agents":
                    print(f"Agents: {', '.join(self.list_agents())}")
                    continue

                if user_input.lower() == "/handoffs":
                    for agent in self.agents:
                        targets = self.get_allowed_handoffs(agent.name)
                        print(f"  {agent.name} → {targets if targets else '(none)'}")
                    continue

                if user_input.lower() == "/clear":
                    for agent in self.agents:
                        agent.clear_history()
                    print("Conversation history cleared.")
                    continue

                # Process the request
                result = self.process(user_input)

                print(f"\n[{result.final_agent}]: {result.response}")

                if result.handoffs:
                    print(f"\n  (Handoffs: {len(result.handoffs)}, Time: {result.total_time:.2f}s)")

                print()

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\n[Error]: {e}\n")

    def visualize(self) -> str:
        """
        Generate ASCII visualization of the agency structure.

        Returns:
            ASCII art representation of agents and flows
        """
        lines = [
            f"Agency: {self.name}",
            "=" * 40,
            "",
            "Agents:",
        ]

        for agent in self.agents:
            marker = "→" if agent == self.entry_agent else " "
            lines.append(f"  {marker} {agent.name}")

        lines.append("")
        lines.append("Communication Flows:")

        for source, targets in self._flows.items():
            for target in targets:
                lines.append(f"  {source} → {target}")

        if not self._flows:
            lines.append("  (none defined)")

        return "\n".join(lines)
```

#### 2.2 Handoff Tool

**New File: `src/indusagi/tools/handoff.py`**

```python
"""
Handoff Tool - Enables agent-to-agent communication.

This tool allows agents to transfer control to other agents
within an Agency context.
"""
from typing import Optional, TYPE_CHECKING
from indusagi.tools import registry

if TYPE_CHECKING:
    from indusagi.agency import Agency

# Global agency reference (set at runtime)
_current_agency: Optional["Agency"] = None


def set_current_agency(agency: "Agency") -> None:
    """Set the current agency context for handoff tools."""
    global _current_agency
    _current_agency = agency


def get_current_agency() -> Optional["Agency"]:
    """Get the current agency context."""
    return _current_agency


@registry.register
def handoff_to_agent(
    agent_name: str,
    message: str,
    context: Optional[str] = None
) -> str:
    """
    Hand off the current task to another agent.

    Use this tool when:
    - The task requires expertise from a specialized agent
    - Strategic planning is needed (handoff to PlannerAgent)
    - Implementation help is needed (handoff to CoderAgent)
    - The current agent cannot complete the task alone

    Args:
        agent_name: Name of the agent to hand off to
        message: Description of what needs to be done
        context: Additional context to provide

    Returns:
        The target agent's response
    """
    if _current_agency is None:
        return "Error: No agency context available. Handoffs require an Agency."

    # Find current agent (the one calling this tool)
    # This is a simplification - in practice, would need to track this
    current = _current_agency.entry_agent

    if not _current_agency.can_handoff(current.name, agent_name):
        allowed = _current_agency.get_allowed_handoffs(current.name)
        return f"Error: Cannot handoff to {agent_name}. Allowed: {allowed}"

    result = _current_agency.handoff(
        from_agent=current,
        to_agent_name=agent_name,
        message=message,
        context={"additional_context": context} if context else None
    )

    if result.success:
        return result.response
    else:
        return f"Handoff failed: {result.error}"
```

---

### Phase 3: Development Tools

#### 3.1 Base Tool Class

**New File: `src/indusagi/tools/base.py`**

```python
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

        for prop_name, prop in schema.get("properties", {}).items():
            # Skip class variables
            if prop_name in ["name", "description"]:
                continue

            properties[prop_name] = {
                "type": prop.get("type", "string"),
                "description": prop.get("description", ""),
            }

            # Check if required (no default)
            if "default" not in prop:
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
```

#### 3.2 Bash Tool

**New File: `src/indusagi/tools/dev/bash.py`**

```python
"""
Bash Tool - Execute shell commands safely.
"""
import subprocess
import os
import threading
from typing import Optional, ClassVar
from pydantic import Field
from indusagi.tools.base import BaseTool

_bash_lock = threading.Lock()
_bash_busy = False


class Bash(BaseTool):
    """Execute bash commands with timeout and safety measures."""

    name: ClassVar[str] = "bash"
    description: ClassVar[str] = """Execute bash commands in the current working directory.

Use for: running tests, installing packages, git operations, building projects.
Do NOT use for: reading files (use Read), editing files (use Edit), searching (use Grep/Glob)."""

    command: str = Field(..., description="The bash command to execute")
    timeout: int = Field(
        120000,
        description="Timeout in milliseconds (max 600000)",
        ge=5000,
        le=600000
    )
    description_field: Optional[str] = Field(
        None,
        description="Brief description of what this command does",
        alias="command_description"
    )

    def execute(self) -> str:
        global _bash_busy

        if _bash_busy:
            return "Error: Terminal is busy. Wait for current command to complete."

        timeout_seconds = self.timeout / 1000

        with _bash_lock:
            _bash_busy = True
            try:
                result = subprocess.run(
                    ["/bin/bash", "-c", self.command],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=os.getcwd(),
                    env={**os.environ, "TERM": "dumb"},
                )

                output = ""
                if result.stdout:
                    output = result.stdout
                if result.stderr:
                    if output:
                        output += "\n--- STDERR ---\n"
                    output += result.stderr

                if not output.strip():
                    return f"Exit code: {result.returncode}\n(No output)"

                # Truncate long output
                if len(output) > 30000:
                    output = output[-30000:]
                    output = "(truncated)\n" + output

                return f"Exit code: {result.returncode}\n{output.strip()}"

            except subprocess.TimeoutExpired:
                return f"Error: Command timed out after {timeout_seconds}s"
            except Exception as e:
                return f"Error executing command: {str(e)}"
            finally:
                _bash_busy = False
```

#### 3.3 Read Tool

**New File: `src/indusagi/tools/dev/read.py`**

```python
"""
Read Tool - Read file contents with line numbers.
"""
import os
from typing import Optional, ClassVar
from pydantic import Field
from indusagi.tools.base import BaseTool, get_tool_context


class Read(BaseTool):
    """Read file contents with line numbers."""

    name: ClassVar[str] = "read"
    description: ClassVar[str] = """Read a file from the filesystem.

Returns file contents with line numbers. Use this before Edit to see current content.
Supports text files, images (displays visually), and Jupyter notebooks."""

    file_path: str = Field(..., description="Absolute path to the file to read")
    offset: Optional[int] = Field(None, description="Line number to start reading from (1-indexed)")
    limit: Optional[int] = Field(None, description="Maximum number of lines to read")

    def execute(self) -> str:
        abs_path = os.path.abspath(self.file_path)

        # Mark file as read for Edit precondition
        get_tool_context().mark_file_read(abs_path)

        if not os.path.exists(self.file_path):
            return f"Error: File does not exist: {self.file_path}"

        if not os.path.isfile(self.file_path):
            return f"Error: Not a file: {self.file_path}"

        # Try to read file
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(self.file_path, "r", encoding="latin-1") as f:
                    lines = f.readlines()
            except Exception as e:
                return f"Error: Cannot decode file: {self.file_path} ({e})"
        except Exception as e:
            return f"Error reading file: {e}"

        if not lines:
            return f"Warning: File is empty: {self.file_path}"

        # Apply offset and limit
        start = (self.offset - 1) if self.offset else 0
        start = max(0, min(start, len(lines)))
        end = start + (self.limit or 2000)

        selected = lines[start:end]

        # Format with line numbers
        result = []
        for i, line in enumerate(selected, start=start + 1):
            # Truncate very long lines
            if len(line) > 2000:
                line = line[:1997] + "..."
            result.append(f"{i:>6}\t{line.rstrip()}")

        output = "\n".join(result)

        if len(selected) < len(lines):
            output += f"\n\n[Showing lines {start + 1}-{start + len(selected)} of {len(lines)} total]"

        return output
```

#### 3.4 Edit Tool

**New File: `src/indusagi/tools/dev/edit.py`**

```python
"""
Edit Tool - Edit files using string replacement.
"""
import os
from typing import ClassVar
from pydantic import Field
from indusagi.tools.base import BaseTool, get_tool_context


class Edit(BaseTool):
    """Edit files using exact string replacement."""

    name: ClassVar[str] = "edit"
    description: ClassVar[str] = """Replace text in a file using exact string matching.

IMPORTANT: You must Read the file first before editing.
The old_string must match exactly (including indentation).
If old_string appears multiple times, use replace_all or provide more context."""

    file_path: str = Field(..., description="Absolute path to the file to edit")
    old_string: str = Field(..., description="The exact text to replace")
    new_string: str = Field(..., description="The replacement text")
    replace_all: bool = Field(False, description="Replace all occurrences (default: False)")

    def execute(self) -> str:
        abs_path = os.path.abspath(self.file_path)

        # Precondition: file must have been read first
        if not get_tool_context().was_file_read(abs_path):
            return "Error: You must Read the file before editing it. Use the Read tool first."

        if self.old_string == self.new_string:
            return "Error: old_string and new_string must be different"

        if not os.path.exists(self.file_path):
            return f"Error: File does not exist: {self.file_path}"

        # Read current content
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file: {e}"

        # Check if old_string exists
        if self.old_string not in content:
            return "Error: old_string not found in file. Check for exact match including whitespace."

        # Check uniqueness
        count = content.count(self.old_string)
        if count > 1 and not self.replace_all:
            return f"Error: old_string appears {count} times. Set replace_all=True or provide more context to make it unique."

        # Perform replacement
        if self.replace_all:
            new_content = content.replace(self.old_string, self.new_string)
            replaced = count
        else:
            new_content = content.replace(self.old_string, self.new_string, 1)
            replaced = 1

        # Write back
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"Successfully replaced {replaced} occurrence(s) in {self.file_path}"
        except Exception as e:
            return f"Error writing file: {e}"
```

#### 3.5 Additional Tools to Implement

| Tool | Priority | Description |
|------|----------|-------------|
| Write | HIGH | Create new files |
| Glob | HIGH | File pattern matching |
| Grep | HIGH | Content search with regex |
| Git | HIGH | Version control operations |
| LS | MEDIUM | Directory listing |
| MultiEdit | MEDIUM | Multiple edits in one call |
| TodoWrite | MEDIUM | Task management |
| NotebookRead | LOW | Jupyter notebook support |
| NotebookEdit | LOW | Jupyter notebook editing |

---

### Phase 4: Hook System

#### 4.1 Hook Infrastructure

**New File: `src/indusagi/hooks.py`**

```python
"""
Hooks System - Lifecycle management for agents.

Provides hooks for intercepting agent execution at various points.
"""
from abc import ABC
from typing import Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class RunContext:
    """Context passed to hooks during agent execution."""
    agent_name: str
    shared_state: dict = field(default_factory=dict)
    messages: List[dict] = field(default_factory=list)
    tool_calls: int = 0
    pending_reminder: Optional[str] = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.shared_state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.shared_state[key] = value


class AgentHooks(ABC):
    """
    Base class for agent hooks.

    Hooks allow injecting custom behavior at various points:
    - on_start: When agent begins processing
    - on_end: When agent finishes processing
    - on_tool_start: Before each tool execution
    - on_tool_end: After each tool execution
    - on_handoff: When agent receives a handoff
    """

    async def on_start(self, context: RunContext, agent: Any) -> None:
        """Called when agent starts processing."""
        pass

    async def on_end(self, context: RunContext, agent: Any, output: str) -> None:
        """Called when agent finishes processing."""
        pass

    async def on_tool_start(self, context: RunContext, agent: Any, tool: Any) -> None:
        """Called before each tool execution."""
        pass

    async def on_tool_end(
        self, context: RunContext, agent: Any, tool: Any, result: str
    ) -> None:
        """Called after each tool execution."""
        pass

    async def on_handoff(
        self, context: RunContext, agent: Any, source: Any
    ) -> None:
        """Called when agent receives a handoff from another agent."""
        pass


class SystemReminderHook(AgentHooks):
    """
    Injects periodic system reminders.

    Triggers:
    - Every N tool calls (default: 15)
    - After each user message
    """

    def __init__(self, tool_call_interval: int = 15):
        self.tool_call_count = 0
        self.tool_call_interval = tool_call_interval

    async def on_start(self, context: RunContext, agent: Any) -> None:
        """Inject reminder at start."""
        self._inject_reminder(context, "start")

    async def on_tool_end(
        self, context: RunContext, agent: Any, tool: Any, result: str
    ) -> None:
        """Track tool calls and inject reminder periodically."""
        self.tool_call_count += 1
        context.tool_calls = self.tool_call_count

        if self.tool_call_count >= self.tool_call_interval:
            self._inject_reminder(context, "tool_limit")
            self.tool_call_count = 0

    def _inject_reminder(self, context: RunContext, trigger: str) -> None:
        """Build and inject a system reminder."""
        todos = context.get("todos", [])

        reminder = """<system-reminder>
# Important Reminders
- Complete the requested task fully
- Use tools appropriately (Read before Edit)
- Do not create unnecessary files
- Track progress with TodoWrite
"""

        if todos:
            pending = sum(1 for t in todos if t.get("status") == "pending")
            in_progress = sum(1 for t in todos if t.get("status") == "in_progress")
            completed = sum(1 for t in todos if t.get("status") == "completed")
            reminder += f"""
# TODO Status
- Pending: {pending}
- In Progress: {in_progress}
- Completed: {completed}
"""

        reminder += "</system-reminder>"
        context.pending_reminder = reminder


class CompositeHook(AgentHooks):
    """Combines multiple hooks into one."""

    def __init__(self, hooks: List[AgentHooks]):
        self.hooks = hooks

    async def on_start(self, context: RunContext, agent: Any) -> None:
        for hook in self.hooks:
            await hook.on_start(context, agent)

    async def on_end(self, context: RunContext, agent: Any, output: str) -> None:
        for hook in self.hooks:
            await hook.on_end(context, agent, output)

    async def on_tool_start(self, context: RunContext, agent: Any, tool: Any) -> None:
        for hook in self.hooks:
            await hook.on_tool_start(context, agent, tool)

    async def on_tool_end(
        self, context: RunContext, agent: Any, tool: Any, result: str
    ) -> None:
        for hook in self.hooks:
            await hook.on_tool_end(context, agent, tool, result)

    async def on_handoff(
        self, context: RunContext, agent: Any, source: Any
    ) -> None:
        for hook in self.hooks:
            await hook.on_handoff(context, agent, source)
```

---

## 3. New Files Summary

| File | Purpose |
|------|---------|
| `src/indusagi/agency.py` | Agency orchestration class |
| `src/indusagi/hooks.py` | Hook system for lifecycle events |
| `src/indusagi/tools/base.py` | BaseTool class (Pydantic-based) |
| `src/indusagi/tools/handoff.py` | Agent handoff tool |
| `src/indusagi/tools/dev/bash.py` | Bash command execution |
| `src/indusagi/tools/dev/read.py` | File reading with line numbers |
| `src/indusagi/tools/dev/edit.py` | File editing with string replacement |
| `src/indusagi/tools/dev/write.py` | File creation |
| `src/indusagi/tools/dev/glob.py` | File pattern matching |
| `src/indusagi/tools/dev/grep.py` | Content search |
| `src/indusagi/tools/dev/git.py` | Git operations |
| `src/indusagi/tools/dev/todo_write.py` | Task management |
| `src/indusagi/templates/__init__.py` | Template module |
| `src/indusagi/templates/renderer.py` | Template rendering |
| `src/indusagi/templates/scaffolder.py` | Agent scaffolding |

---

## 4. Files to Modify

| File | Changes |
|------|---------|
| `src/indusagi/cli.py` | Add `create-agent`, `create-agency` commands |
| `src/indusagi/agent.py` | Add hooks support, handoff integration |
| `src/indusagi/__init__.py` | Export new classes (Agency, BaseTool, hooks) |
| `pyproject.toml` | Add pyyaml dependency for config |

---

## 5. Example Usage After Implementation

```python
# agency.py - Example multi-agent setup
from indusagi import Agency
from agents.planner_agent import create_planner_agent
from agents.coder_agent import create_coder_agent

# Create agents
planner = create_planner_agent(model="gpt-4o", reasoning_effort="high")
coder = create_coder_agent(model="gpt-4o", reasoning_effort="high")

# Create agency with communication flows
agency = Agency(
    entry_agent=coder,
    agents=[coder, planner],
    communication_flows=[
        (coder, planner),   # Coder can ask Planner for help
        (planner, coder),   # Planner can delegate to Coder
    ],
    shared_instructions="./project-overview.md",
    name="DevAgency"
)

# Run interactive demo
if __name__ == "__main__":
    agency.terminal_demo()
```

```bash
# CLI usage
$ indus-agents create-agent qa_tester --description "QA testing specialist"
Creating agent: qa_tester
✓ Agent created at: ./agents/qa_tester_agent/

$ indus-agents create-agency dev_team --agents coder,planner,qa_tester
Creating agency: dev_team
✓ Agency created at: ./dev_team_agency.py
```

---

## 6. Success Criteria

After implementation, indus-agents should be able to:

1. ✅ **Create new agents** via CLI (`create-agent` command)
2. ✅ **Scaffold agent directories** with instructions.md templates
3. ✅ **Orchestrate multiple agents** via Agency class
4. ✅ **Enable agent handoffs** with SendMessageHandoff-style tools
5. ✅ **Share context** across agents in an agency
6. ✅ **Provide development tools** (Bash, Read, Edit, Git, etc.)
7. ✅ **Support instruction templates** with placeholders
8. ✅ **Enable lifecycle hooks** for monitoring and control
9. ✅ **Track tasks** with TodoWrite tool
10. ✅ **Run terminal demos** like Agency-Code

---

## 7. Conclusion

This implementation plan provides a clear path to transform indus-agents from a basic single-agent framework into a full-featured multi-agent system matching Agency Swarm capabilities while maintaining its clean architecture and excellent CLI.

The phased approach ensures:
- Quick wins with agent generation (Phase 1)
- Core multi-agent capability (Phase 2)
- Production-ready tools (Phase 3)
- Advanced features (Phase 4)

Estimated effort: 3-4 weeks for full implementation.
