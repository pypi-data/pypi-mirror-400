# Framework Architecture

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Interface                        │
│                      (Typer + Rich)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                            │
│              (Routes to Specialized Agents)                  │
└─────┬──────────────────┬────────────────────┬───────────────┘
      │                  │                    │
      ▼                  ▼                    ▼
┌──────────┐      ┌──────────┐        ┌──────────┐
│  Agent 1 │      │  Agent 2 │        │  Agent 3 │
│ (General)│      │  (Math)  │        │  (Time)  │
└────┬─────┘      └────┬─────┘        └────┬─────┘
     │                 │                    │
     └─────────────────┴────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │      Tool Registry          │
         │  (Functions + Schemas)      │
         └─────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
   ┌──────────┐              ┌──────────┐
   │ LLM API  │              │  Memory  │
   │ (Claude) │              │ (History)│
   └──────────┘              └──────────┘
```

## 🎯 Core Components

### 1. Agent Class

**Purpose**: Core reasoning engine that interacts with LLM

**Responsibilities**:
- Send prompts to LLM API
- Handle tool calling
- Maintain conversation context
- Return formatted responses

**Key Methods**:
```python
class Agent:
    def __init__(self, name, role, config)
    def process(self, user_input) -> str
    def process_with_tools(self, user_input, max_turns) -> str
```

**Design Decisions**:
- Uses composition (has-a) for memory and client
- Stateful: maintains message history
- Synchronous by default (async optional for 3-hour version)

**Why This Design?**
- Simple to understand and test
- Easy to extend with new capabilities
- Minimal dependencies

---

### 2. Tool Registry

**Purpose**: Manages available tools and their schemas

**Responsibilities**:
- Register tools via decorator pattern
- Auto-generate JSON schemas from function signatures
- Execute tools by name
- Validate tool parameters

**Key Methods**:
```python
class ToolRegistry:
    def register(self, func) -> Callable  # Decorator
    def execute(self, name, **kwargs) -> Any
    @property
    def schemas(self) -> List[dict]
```

**Schema Generation**:
```python
# From this:
@registry.register
def calculator(expression: str) -> str:
    """Evaluate mathematical expression."""
    ...

# Generates this:
{
    "name": "calculator",
    "description": "Evaluate mathematical expression.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string"}
        },
        "required": ["expression"]
    }
}
```

**Why This Design?**
- Automatic schema generation reduces boilerplate
- Type hints provide validation
- Decorator pattern is pythonic and intuitive

---

### 3. Orchestrator

**Purpose**: Routes user queries to appropriate specialized agents

**Responsibilities**:
- Maintain registry of specialized agents
- Analyze user input
- Select best agent for task
- Return unified response

**Routing Strategies**:

**Option A: Keyword-Based (Simple, Fast)**
```python
def route(self, user_input: str) -> str:
    if "math" in user_input.lower():
        return self.agents["math"].process(user_input)
    return self.agents["general"].process(user_input)
```

**Option B: Scoring-Based (More Accurate)**
```python
def route(self, user_input: str) -> str:
    scores = {
        "math": self._score_math(user_input),
        "time": self._score_time(user_input),
        "general": 0.5  # baseline
    }
    best_agent = max(scores, key=scores.get)
    return self.agents[best_agent].process(user_input)
```

**Option C: LLM-Based (Most Flexible)**
```python
def route(self, user_input: str) -> str:
    routing_prompt = f"""
    Given the user query: "{user_input}"
    Which agent should handle this?
    Options: math, time, general
    """
    agent_name = self.routing_llm.complete(routing_prompt)
    return self.agents[agent_name].process(user_input)
```

**Recommendation for 2-3 Hour Session**: Use Option A or B

---

### 4. Memory System

**Purpose**: Store and retrieve conversation history

**Responsibilities**:
- Track user and assistant messages
- Limit memory size (prevent context overflow)
- Save/load conversations
- Provide context for agents

**Architecture**:
```python
class ConversationMemory:
    messages: deque[dict]  # Fixed size circular buffer
    max_messages: int = 20

    def add(role, content)
    def get_messages() -> List[dict]
    def clear()
    def save(filepath)
    def load(filepath)
```

**Memory Strategies**:

**Level 1: In-Memory Only** (2-hour session)
- Simple list/deque
- Lost on restart
- Fast and sufficient for demos

**Level 2: File-Based** (3-hour session)
- JSON persistence
- Manual load/save
- Good for development

**Level 3: Database** (Post-session enhancement)
- SQLite or PostgreSQL
- Automatic persistence
- Supports multiple users

**Level 4: Vector Memory** (Advanced)
- Embeddings + vector DB
- Semantic search
- Long-term knowledge

---

### 5. CLI Interface

**Purpose**: User-friendly command-line interface

**Responsibilities**:
- Parse command-line arguments
- Format output beautifully
- Handle errors gracefully
- Provide help and documentation

**Commands**:
```bash
indusagi run "prompt"       # Single query
indusagi interactive        # Chat mode
indusagi version           # Version info
indusagi list-tools        # Show available tools
indusagi test-connection   # Verify API
```

**Why Typer + Rich?**
- **Typer**: Automatic CLI from type hints (less code)
- **Rich**: Beautiful terminal output (professional UX)
- Both are modern Python standards

---

## 🔄 Data Flow

### Typical Request Flow:

```
1. User Input
   ↓
2. CLI receives command
   ↓
3. Orchestrator analyzes input
   ↓
4. Routes to appropriate Agent
   ↓
5. Agent sends to LLM with tools
   ↓
6. LLM decides: Final answer OR use tool
   ↓
7a. If tool needed:
    - Agent calls Tool Registry
    - Tool executes
    - Result sent back to LLM
    - Repeat from step 6
   ↓
7b. If final answer:
    - Agent adds to memory
    - Returns to CLI
   ↓
8. CLI formats and displays
   ↓
9. User sees response
```

### Tool Calling Flow:

```
Agent → LLM API (with tool schemas)
         ↓
    LLM Returns:
    stop_reason: "tool_use"
    content: [
        {type: "text", text: "I'll calculate that"},
        {type: "tool_use", name: "calculator", input: {...}}
    ]
         ↓
Agent → Tool Registry.execute("calculator", **input)
         ↓
Tool Registry → calculator function
         ↓
Result → Agent
         ↓
Agent → LLM API (with tool result)
         ↓
    LLM Returns:
    stop_reason: "end_turn"
    content: [{type: "text", text: "The answer is 100"}]
         ↓
Agent → CLI → User
```

---

## 🎯 Design Patterns Used

### 1. **Decorator Pattern** (Tool Registration)
```python
@registry.register
def my_tool(param: str) -> str:
    ...
```
**Why**: Clean, pythonic way to register tools

### 2. **Registry Pattern** (Tool Management)
```python
registry = ToolRegistry()
result = registry.execute("tool_name", **kwargs)
```
**Why**: Centralized tool management, easy discovery

### 3. **Composition Over Inheritance**
```python
class Agent:
    def __init__(self):
        self.memory = ConversationMemory()  # Has-a
        self.client = Anthropic()           # Has-a
```
**Why**: More flexible than inheritance

### 4. **Strategy Pattern** (Routing)
```python
strategies = {
    "keyword": KeywordRouter(),
    "scoring": ScoringRouter(),
    "llm": LLMRouter()
}
```
**Why**: Easy to swap routing algorithms

### 5. **Builder Pattern** (Configuration)
```python
config = AgentConfig.from_env()
agent = Agent(name="Bot", role="Helper", config=config)
```
**Why**: Flexible configuration, clear defaults

---

## 🔐 Security Considerations

### For 2-3 Hour Session:

**DO implement**:
- API key from environment variables (never hardcode)
- Basic input validation
- Try/except around LLM calls
- Tool execution in try/except

**DON'T worry about yet**:
- Sandboxing (just avoid dangerous tools)
- Rate limiting (use API defaults)
- User authentication (local development)
- Code execution (too risky for quick session)

### Production Security (Post-Session):

**Critical**:
- Sandbox tool execution (Docker containers)
- Rate limiting per user
- Input sanitization
- Output filtering (prevent prompt injection)
- Audit logging
- Secrets management (Vault, AWS Secrets Manager)

---

## 📊 Scalability Considerations

### Current Design (2-3 Hour Session):
- **Synchronous**: One request at a time
- **In-memory**: Lost on restart
- **Single-process**: No parallelization
- **Stateful**: Each agent maintains state

**Suitable For**:
- Development and testing
- Single user scenarios
- Low-traffic demos
- Learning and prototyping

### Scaling Path (Post-Session):

**Phase 1: Async Support**
```python
async def process_async(self, user_input: str) -> str:
    response = await self.client.messages.create(...)
    return response.content[0].text
```
**Benefit**: Handle multiple concurrent requests

**Phase 2: Stateless Agents**
```python
def process(self, user_input: str, session_id: str) -> str:
    memory = self.memory_store.get(session_id)
    # ... process ...
    self.memory_store.save(session_id, memory)
```
**Benefit**: Horizontal scaling, load balancing

**Phase 3: Message Queue**
```python
# User request → Queue → Worker Pool → Response
from celery import Celery
app = Celery('tasks')

@app.task
def process_agent_task(user_input: str, session_id: str):
    return orchestrator.route(user_input)
```
**Benefit**: Reliable, distributed processing

**Phase 4: Microservices**
```python
# Orchestrator → Agent Service 1
#             → Agent Service 2
#             → Tool Service
#             → Memory Service
```
**Benefit**: Independent scaling, fault isolation

---

## 🧪 Testing Strategy

### Unit Tests (Test Individual Components):
```python
def test_tool_registration():
    registry = ToolRegistry()
    @registry.register
    def test_tool(x: int) -> int:
        return x * 2

    assert "test_tool" in registry.tools
    assert registry.execute("test_tool", x=5) == 10
```

### Integration Tests (Test Component Interactions):
```python
def test_agent_with_tools():
    agent = Agent("Test", "Tester")
    result = agent.process_with_tools("Calculate 2+2")
    assert "4" in result
```

### End-to-End Tests (Test Complete Flow):
```python
def test_cli_command():
    result = runner.invoke(app, ["run", "What is 10*5?"])
    assert "50" in result.stdout
```

### Mock Tests (Fast, No External Calls):
```python
@patch('anthropic.Anthropic')
def test_agent_mocked(mock_anthropic):
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    agent = Agent("Test", "Tester")
    # Test logic without real API calls
```

---

## 🎨 Code Style & Conventions

### Naming Conventions:
- **Classes**: PascalCase (`Agent`, `ToolRegistry`)
- **Functions**: snake_case (`process_with_tools`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_TOKENS`)
- **Private methods**: `_internal_method`

### Type Hints:
```python
def process(self, user_input: str) -> str:
    ...

messages: List[dict]
tools: Dict[str, Callable]
config: Optional[AgentConfig] = None
```

### Docstrings:
```python
def process(self, user_input: str) -> str:
    """
    Process user input and return agent response.

    Args:
        user_input: User's query or command

    Returns:
        Agent's response text

    Raises:
        APIError: If LLM API call fails
    """
```

### Error Handling:
```python
try:
    response = self.client.messages.create(...)
except APIError as e:
    logger.error(f"API error: {e}")
    return "Sorry, I encountered an error. Please try again."
```

---

## 📦 Package Structure

```
indusagi/
├── src/
│   └── indusagi/
│       ├── __init__.py           # Package exports
│       ├── agent.py              # Agent class
│       ├── tools.py              # Tool registry
│       ├── memory.py             # Memory system
│       ├── orchestrator.py       # Multi-agent orchestration
│       ├── config.py             # Configuration
│       └── cli.py                # CLI interface
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   ├── test_memory.py
│   └── conftest.py               # Pytest fixtures
├── .gitignore
├── pyproject.toml                # Package configuration
├── README.md
└── LICENSE
```

### Key Files:

**pyproject.toml**:
```toml
[project]
name = "indusagi"
version = "0.1.0"
dependencies = ["anthropic", "typer", "rich", "pydantic"]

[project.scripts]
indusagi = "indusagi.cli:app"
```

**__init__.py**:
```python
from .agent import Agent, AgentConfig
from .tools import registry
from .orchestrator import Orchestrator

__version__ = "0.1.0"
__all__ = ["Agent", "AgentConfig", "registry", "Orchestrator"]
```

---

## 🚀 Performance Optimization

### For 2-3 Hour Session (Don't Optimize Prematurely):
- Keep it simple
- Measure before optimizing
- Focus on working code first

### Post-Session Optimizations:

**1. Cache LLM Responses**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def process_cached(self, user_input: str) -> str:
    return self.process(user_input)
```

**2. Batch Tool Calls**
```python
# Instead of: tool1() → LLM → tool2() → LLM
# Do: [tool1(), tool2()] → LLM once
```

**3. Streaming for Long Responses**
```python
with self.client.messages.stream(...) as stream:
    for text in stream.text_stream:
        yield text  # Show immediately
```

**4. Async/Await for Concurrency**
```python
async def process_batch(self, inputs: List[str]) -> List[str]:
    tasks = [self.process_async(inp) for inp in inputs]
    return await asyncio.gather(*tasks)
```

---

## 🔄 Future Enhancements

### Week 1:
- Add configuration file (YAML/JSON)
- Implement async/await
- Add more tools (weather, news, etc.)
- Create comprehensive test suite

### Month 1:
- Add vector memory (embeddings + Pinecone)
- Implement streaming responses
- Create web interface (FastAPI)
- Add user authentication

### Month 3:
- Multi-modal support (images, audio)
- Plugin system for third-party tools
- Distributed execution
- Production monitoring

---

**Next**: Open **03-IMPLEMENTATION-GUIDE.md** for step-by-step coding instructions
