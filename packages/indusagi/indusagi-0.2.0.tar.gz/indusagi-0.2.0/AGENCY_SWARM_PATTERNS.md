# Agency Swarm Framework Patterns Analysis

## Overview

This document provides a deep analysis of the Agency Swarm framework patterns as implemented in Agency-Code, serving as a reference for implementing similar capabilities in indus-agents.

---

## 1. Core Concepts

### 1.1 Agency

The **Agency** is the central orchestrator that manages multiple agents and their communication.

```python
from agency_swarm import Agency
from agency_swarm.tools import SendMessageHandoff

agency = Agency(
    coder, planner,                    # Agents (first is entry point)
    name="AgencyCode",                 # Agency name
    communication_flows=[              # Who can talk to whom
        (coder, planner, SendMessageHandoff),
        (planner, coder, SendMessageHandoff),
    ],
    shared_instructions="./project-overview.md",  # Shared context
)
```

**Key Responsibilities:**
- Initialize and manage agent instances
- Define allowed communication flows
- Load shared instructions
- Provide entry points (terminal_demo, get_response)

### 1.2 Agent

An **Agent** is an independent AI unit with specific role, tools, and instructions.

```python
from agency_swarm import Agent

agent = Agent(
    name="PlannerAgent",
    description="Strategic planning specialist",
    instructions="./instructions.md",
    model="gpt-4o",
    tools=[Read, Write, Bash],
    hooks=custom_hooks,
    model_settings=model_settings,
)
```

**Agent Configuration:**
| Parameter | Purpose |
|-----------|---------|
| `name` | Unique identifier |
| `description` | Role description for handoffs |
| `instructions` | System prompt (file path or string) |
| `model` | LLM model to use |
| `tools` | List of tool classes |
| `tools_folder` | Directory to auto-load tools from |
| `hooks` | Lifecycle hooks |
| `model_settings` | Model-specific settings |

### 1.3 Tools

**Tools** are functions/classes that agents can invoke to perform actions.

```python
from agency_swarm.tools import BaseTool
from pydantic import Field

class Bash(BaseTool):
    """Execute bash commands."""

    command: str = Field(..., description="Command to execute")
    timeout: int = Field(120000, description="Timeout in ms")

    def run(self):
        # Execute and return result
        return result
```

**Tool Patterns:**
- Inherit from `BaseTool`
- Define parameters with Pydantic `Field`
- Implement `run()` method
- Return strings

### 1.4 Instructions

**Instructions** are markdown templates that define agent behavior.

```markdown
# Role and Objective
You are a PlannerAgent - a strategic planning specialist.

# Instructions
1. Clarify ambiguous requirements
2. Break down complex tasks
3. Create actionable plans

# Environment
<env>
Working directory: {cwd}
Platform: {platform}
Today: {today}
Model: {model}
</env>
```

**Placeholders:**
- `{cwd}` - Current working directory
- `{is_git_repo}` - Git repo status
- `{platform}` - OS platform
- `{today}` - Current date
- `{model}` - Model name

---

## 2. Agent Factory Pattern

Agency Swarm uses **factory functions** to create agents, avoiding singletons and circular imports.

```python
def create_planner_agent(
    model: str = "gpt-4o",
    reasoning_effort: str = "high"
) -> Agent:
    """Factory that returns a fresh PlannerAgent instance."""

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Select instructions based on model
    instructions_file = select_instructions_file(current_dir, model)
    instructions = render_instructions(instructions_file, model)

    # Create hook
    filter_hook = create_message_filter_hook()

    return Agent(
        name="PlannerAgent",
        description="A strategic planning and task breakdown specialist",
        instructions=instructions,
        model=get_model_instance(model),
        hooks=filter_hook,
        model_settings=create_model_settings(model, reasoning_effort),
    )
```

**Benefits:**
- Fresh instances per agency
- Testable (can create multiple)
- Avoids circular imports
- Configurable per use case

---

## 3. Communication Flow Architecture

### 3.1 Flow Definition

Communication flows define which agents can communicate with which.

```python
communication_flows=[
    (coder, planner, SendMessageHandoff),  # Coder → Planner
    (planner, coder, SendMessageHandoff),  # Planner → Coder
]
```

**Components:**
- **Source Agent**: Initiator
- **Target Agent**: Receiver
- **Handoff Tool**: SendMessageHandoff

### 3.2 Handoff Mechanism

When an agent needs help from another, it uses the handoff tool:

```
PlannerAgent: "I've created a detailed plan.
              Now handing off to AgencyCodeAgent for implementation..."

→ SendMessageHandoff(
    to_agent="AgencyCodeAgent",
    message="Here is the implementation plan:..."
  )

→ AgencyCodeAgent receives context and continues
```

### 3.3 Bidirectional Communication

Agents can hand off back and forth:

```
User Request
     │
     ▼
PlannerAgent ──────────────────────────────────┐
     │                                          │
     ├─ Creates plan                            │
     │                                          │
     └─► Handoff to AgencyCodeAgent ────────────│
                    │                           │
                    ├─ Starts implementation    │
                    │                           │
                    ├─ Encounters blocker       │
                    │                           │
                    └─► Handoff back ◄──────────┘
                                │
                         Gets guidance
                                │
                         Continues work
```

---

## 4. Instruction System

### 4.1 Model-Specific Instructions

Agents can have different instructions for different models:

```
planner_agent/
├── instructions.md          # Default
└── instructions-gpt-5.md    # GPT-5 specific
```

**Selection Logic:**
```python
def select_instructions_file(agent_dir: str, model: str) -> str:
    """Select appropriate instructions file for model."""
    if model.startswith("gpt-5"):
        gpt5_path = os.path.join(agent_dir, "instructions-gpt-5.md")
        if os.path.exists(gpt5_path):
            return gpt5_path

    return os.path.join(agent_dir, "instructions.md")
```

### 4.2 Template Rendering

Instructions support placeholders replaced at runtime:

```python
def render_instructions(template_path: str, model: str) -> str:
    """Render instructions with placeholders."""
    with open(template_path, "r") as f:
        content = f.read()

    placeholders = {
        "{cwd}": os.getcwd(),
        "{is_git_repo}": str(os.path.isdir(".git")),
        "{platform}": platform.system(),
        "{today}": datetime.now().strftime("%Y-%m-%d"),
        "{model}": model,
    }

    for key, value in placeholders.items():
        content = content.replace(key, value)

    return content
```

---

## 5. Hook System

### 5.1 Hook Lifecycle

Hooks intercept agent execution at various points:

```
Agent.process()
     │
     ├─► on_start()         # Before processing
     │
     ├─► on_llm_start()     # Before LLM call
     │
     ├─► LLM Response
     │
     ├─► on_tool_start()    # Before each tool
     │
     ├─► Tool Execution
     │
     ├─► on_tool_end()      # After each tool
     │
     ├─► (loop until done)
     │
     └─► on_end()           # After processing
```

### 5.2 SystemReminderHook

Injects periodic reminders about important instructions:

```python
class SystemReminderHook(AgentHooks):
    def __init__(self, tool_call_interval: int = 15):
        self.tool_call_count = 0
        self.tool_call_interval = tool_call_interval

    async def on_tool_end(self, context, agent, tool, result):
        self.tool_call_count += 1
        if self.tool_call_count >= self.tool_call_interval:
            self._inject_reminder(context, "tool_limit")
            self.tool_call_count = 0

    def _inject_reminder(self, context, trigger):
        # Inject system reminder about important instructions
        # Include TODO status if available
        pass
```

### 5.3 MessageFilterHook

Handles message deduplication for model compatibility:

```python
class MessageFilterHook(AgentHooks):
    """Remove duplicates and reorder messages."""

    async def on_start(self, context, agent):
        self._filter_duplicates(context)

    async def on_end(self, context, agent, output):
        self._filter_duplicates(context)

    def _filter_duplicates(self, context):
        # Dedupe by call_id
        # Reorder function_call before function_call_output
        pass
```

---

## 6. Tool Patterns

### 6.1 Tool Structure

```python
from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional

class Read(BaseTool):
    """Read file contents with line numbers."""

    # Tool metadata
    name = "read"
    description = "Read a file from the filesystem"

    # Parameters defined as Pydantic fields
    file_path: str = Field(..., description="Absolute path to file")
    offset: Optional[int] = Field(None, description="Line offset")
    limit: Optional[int] = Field(None, description="Max lines")

    def run(self):
        """Execute and return string result."""
        # Implementation
        return formatted_content
```

### 6.2 Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| **File I/O** | Read, Write, Edit, MultiEdit | File operations |
| **Search** | Glob, Grep | Finding files/content |
| **Execution** | Bash | Running commands |
| **Version Control** | Git | Git operations |
| **Navigation** | LS | Directory listing |
| **Project Mgmt** | TodoWrite | Task tracking |
| **Web** | WebSearch | Internet search |
| **Workflow** | ExitPlanMode | Mode management |

### 6.3 Tool Safety Patterns

**Read-First Requirement:**
```python
# Track what files have been read
_read_files: set = set()

class Edit(BaseTool):
    def run(self):
        if self.file_path not in _read_files:
            return "Error: Must Read file before Edit"
        # Continue with edit
```

**Bash Safety:**
```python
class Bash(BaseTool):
    def run(self):
        # Threading lock prevents parallel execution
        with _bash_lock:
            # Timeout protection
            result = subprocess.run(..., timeout=timeout)

            # Output truncation
            if len(output) > 30000:
                output = output[-30000:]

            return output
```

---

## 7. Model Configuration

### 7.1 Model Detection

```python
def detect_model_type(model: str) -> tuple[bool, bool, bool]:
    """Detect model type for configuration."""
    is_openai = "gpt" in model
    is_claude = "claude" in model
    is_grok = "grok" in model
    return is_openai, is_claude, is_grok
```

### 7.2 Model Settings

```python
def create_model_settings(
    model: str,
    reasoning_effort: str = "medium",
    max_tokens: int = 32000,
) -> ModelSettings:
    """Create model-specific settings."""
    is_openai, is_claude, is_grok = detect_model_type(model)

    return ModelSettings(
        reasoning=(
            Reasoning(effort=reasoning_effort)
            if is_openai or is_claude
            else None
        ),
        truncation="auto",
        max_tokens=max_tokens,
        extra_body=(
            {"search_parameters": {"mode": "on"}}
            if is_grok
            else None
        ),
    )
```

### 7.3 Multi-Model Support

```python
def get_model_instance(model: str):
    """Get model instance for LiteLLM."""
    is_openai, _, _ = detect_model_type(model)

    if is_openai:
        return model  # Direct string for OpenAI
    else:
        return LitellmModel(model=model)  # Wrap others
```

---

## 8. Directory Structure

### 8.1 Agency-Code Structure

```
Agency-Code/
├── agency.py                    # Main orchestrator
├── project-overview.md          # Shared instructions
│
├── planner_agent/               # Planning agent
│   ├── __init__.py
│   ├── planner_agent.py         # Factory function
│   ├── instructions.md          # Default instructions
│   └── instructions-gpt-5.md    # GPT-5 variant
│
├── agency_code_agent/           # Coding agent
│   ├── __init__.py
│   ├── agency_code_agent.py     # Factory function
│   ├── instructions.md
│   ├── instructions-gpt-5.md
│   └── tools/                   # Agent-specific tools
│
├── subagent_example/            # Template for new agents
│   ├── __init__.py
│   ├── subagent_example.py
│   └── instructions.md
│
├── shared/                      # Shared utilities
│   ├── agent_utils.py           # Model config helpers
│   ├── system_hooks.py          # Hook implementations
│   └── utils.py                 # Misc utilities
│
├── tools/                       # Shared tools
│   ├── bash.py
│   ├── read.py
│   ├── edit.py
│   └── ...
│
└── tests/                       # Test suite
    ├── test_agency.py
    ├── test_handoffs.py
    └── ...
```

### 8.2 Agent Directory Convention

Each agent should have:
```
{agent_name}_agent/
├── __init__.py              # Exports create_* function
├── {agent_name}_agent.py    # Factory function
├── instructions.md          # Default instructions
├── instructions-{model}.md  # Model-specific (optional)
└── tools/                   # Agent-specific tools (optional)
```

---

## 9. Testing Patterns

### 9.1 Agent Tests

```python
def test_agent_creation():
    """Test agent can be created."""
    agent = create_planner_agent(model="gpt-4o")
    assert agent.name == "PlannerAgent"
    assert agent.tools is not None

def test_agent_tools():
    """Test agent has expected tools."""
    agent = create_agency_code_agent()
    tool_names = [t.__name__ for t in agent.tools]
    assert "Bash" in tool_names
    assert "Read" in tool_names
```

### 9.2 Handoff Tests

```python
def test_bidirectional_handoff():
    """Test agents can hand off to each other."""
    planner = create_planner_agent()
    coder = create_agency_code_agent()

    agency = Agency(
        coder, planner,
        communication_flows=[
            (coder, planner, SendMessageHandoff),
            (planner, coder, SendMessageHandoff),
        ]
    )

    # Verify flows are set up
    assert agency.can_handoff(coder.name, planner.name)
    assert agency.can_handoff(planner.name, coder.name)
```

### 9.3 Tool Tests

```python
def test_bash_tool():
    """Test bash command execution."""
    tool = Bash(command="echo hello", timeout=5000)
    result = tool.run()
    assert "hello" in result
    assert "Exit code: 0" in result

def test_read_edit_flow():
    """Test read-first requirement."""
    # Read first
    read = Read(file_path="/tmp/test.txt")
    read.run()

    # Now edit should work
    edit = Edit(
        file_path="/tmp/test.txt",
        old_string="foo",
        new_string="bar"
    )
    result = edit.run()
    assert "Successfully" in result
```

---

## 10. Best Practices

### 10.1 Agent Design

| Practice | Reason |
|----------|--------|
| Use factory functions | Fresh instances, no circular imports |
| Keep instructions in files | Easy to modify without code changes |
| Use model-specific variants | Optimize for each model's strengths |
| Add hooks for monitoring | Track execution, inject reminders |
| Document handoff conditions | Clear when to transfer control |

### 10.2 Tool Design

| Practice | Reason |
|----------|--------|
| Return strings | Consistent output format |
| Include exit codes | Easy error detection |
| Truncate long output | Prevent token overflow |
| Track state (read files) | Enable safety checks |
| Use threading locks | Prevent race conditions |

### 10.3 Communication Design

| Practice | Reason |
|----------|--------|
| Define explicit flows | Clear who can talk to whom |
| Use bidirectional flows | Enable back-and-forth |
| Include context in handoffs | Target has full picture |
| Document handoff points | Clear expectations |

---

## 11. Summary

Agency Swarm provides a powerful framework for multi-agent systems:

1. **Agency** orchestrates agents and communication
2. **Agents** are specialists with roles and tools
3. **Tools** extend agent capabilities
4. **Instructions** define behavior via templates
5. **Hooks** enable lifecycle management
6. **Handoffs** allow agent collaboration

These patterns can be adapted for indus-agents to enable:
- True multi-agent collaboration
- Agent generation via CLI
- Production-grade development tools
- Sophisticated instruction system
- Lifecycle hooks for monitoring
