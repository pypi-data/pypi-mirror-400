# Agent Class - OpenAI Integration

Complete implementation of the core Agent class for the framework using OpenAI API.

## Features

- **OpenAI Integration**: Uses `gpt-4o` or `gpt-4-turbo` models
- **Pydantic Configuration**: Type-safe configuration with validation
- **Tool Calling Support**: Full OpenAI function calling loop implementation
- **Conversation History**: Automatic message history management
- **Error Handling**: Automatic retries with exponential backoff
- **Type Hints**: Complete type annotations throughout
- **Flexible Configuration**: Environment-based or explicit configuration

## Installation

```bash
pip install openai pydantic python-dotenv
```

## Quick Start

### 1. Set up API Key

```bash
# Linux/Mac
export OPENAI_API_KEY='your-api-key-here'

# Windows PowerShell
$env:OPENAI_API_KEY='your-api-key-here'
```

### 2. Basic Usage

```python
from agent import Agent

# Create an agent
agent = Agent(
    name="Assistant",
    role="Helpful AI assistant"
)

# Process a query
response = agent.process("What is Python?")
print(response)
```

### 3. With Custom Configuration

```python
from agent import Agent, AgentConfig

# Custom configuration
config = AgentConfig(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=2048,
    max_retries=3
)

agent = Agent(
    name="Assistant",
    role="Helpful AI assistant",
    config=config
)
```

### 4. With Tool Calling

```python
from agent import Agent

# Define your tools (functions)
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate mathematical expressions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression like '2+2'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# Create tool executor
class ToolExecutor:
    def execute(self, name, **kwargs):
        if name == "calculator":
            return eval(kwargs["expression"])
        return "Unknown tool"

executor = ToolExecutor()

# Use agent with tools
agent = Agent("MathBot", "Mathematical assistant")
response = agent.process_with_tools(
    "What is 25 * 4?",
    tools=tools,
    tool_executor=executor
)
print(response)
```

## API Reference

### AgentConfig Class

Configuration object for Agent behavior.

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `model` | str | "gpt-4o" | - | OpenAI model identifier |
| `max_tokens` | int | 1024 | 100-4096 | Maximum tokens in response |
| `temperature` | float | 0.7 | 0.0-2.0 | Sampling temperature |
| `top_p` | float | 1.0 | 0.0-1.0 | Nucleus sampling parameter |
| `frequency_penalty` | float | 0.0 | -2.0 to 2.0 | Penalty for token frequency |
| `presence_penalty` | float | 0.0 | -2.0 to 2.0 | Penalty for token presence |
| `max_retries` | int | 3 | 1-10 | Maximum retry attempts |
| `retry_delay` | float | 1.0 | 0.1-10.0 | Delay between retries (seconds) |

**Methods:**

- `from_env()`: Create config from environment variables

**Environment Variables:**

- `OPENAI_MODEL`: Model to use (default: gpt-4o)
- `OPENAI_MAX_TOKENS`: Maximum tokens (default: 1024)
- `OPENAI_TEMPERATURE`: Temperature (default: 0.7)

### Agent Class

Main agent class for LLM interaction.

**Constructor:**

```python
Agent(
    name: str,
    role: str,
    config: Optional[AgentConfig] = None,
    system_prompt: Optional[str] = None
)
```

**Parameters:**

- `name`: Unique identifier for the agent
- `role`: Agent's specialized role or purpose
- `config`: Configuration settings (uses defaults if None)
- `system_prompt`: Custom system prompt (auto-generated if None)

**Methods:**

#### `process(user_input: str) -> str`

Process user input and return agent response (basic mode without tools).

**Parameters:**
- `user_input`: User's query or message

**Returns:**
- Agent's response text

**Example:**
```python
agent = Agent("Helper", "General assistant")
response = agent.process("What is the capital of France?")
```

#### `process_with_tools(user_input, tools, tool_executor, max_turns=10) -> str`

Process user input with tool calling support.

**Parameters:**
- `user_input`: User's query or message
- `tools`: List of tool schemas in OpenAI format (optional)
- `tool_executor`: Object with `execute(name, **kwargs)` method (optional)
- `max_turns`: Maximum iterations of tool calling loop (default: 10)

**Returns:**
- Final agent response after tool usage

**Example:**
```python
response = agent.process_with_tools(
    "Calculate 100 / 4",
    tools=tool_schemas,
    tool_executor=registry,
    max_turns=5
)
```

#### `clear_history() -> None`

Clear the conversation message history.

**Example:**
```python
agent.clear_history()
```

#### `get_history() -> List[Dict[str, Any]]`

Get a copy of the conversation message history.

**Returns:**
- List of message dictionaries

**Example:**
```python
history = agent.get_history()
print(f"Messages: {len(history)}")
```

#### `set_history(messages: List[Dict[str, Any]]) -> None`

Set the conversation message history.

**Parameters:**
- `messages`: List of message dictionaries

**Example:**
```python
old_messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"}
]
agent.set_history(old_messages)
```

#### `get_token_count_estimate() -> int`

Get rough estimate of tokens used in conversation history.

**Returns:**
- Estimated number of tokens

**Example:**
```python
tokens = agent.get_token_count_estimate()
print(f"Estimated tokens: {tokens}")
```

## Advanced Usage

### Custom System Prompt

```python
custom_prompt = """You are an expert Python developer.
Provide clear, well-documented code examples.
Focus on best practices and modern Python features."""

agent = Agent(
    name="PythonExpert",
    role="Python programming assistant",
    system_prompt=custom_prompt
)
```

### Managing Conversation Context

```python
# Start conversation
agent = Agent("ChatBot", "Conversational assistant")

# First exchange
agent.process("My name is Alice")

# Agent remembers context
response = agent.process("What's my name?")
# Response: "Your name is Alice."

# Save conversation
history = agent.get_history()

# Load conversation later
new_agent = Agent("ChatBot", "Conversational assistant")
new_agent.set_history(history)
```

### Environment-Based Configuration

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=2048
OPENAI_TEMPERATURE=0.8
```

Load in Python:

```python
from dotenv import load_dotenv
from agent import Agent, AgentConfig

load_dotenv()

config = AgentConfig.from_env()
agent = Agent("Bot", "Assistant", config=config)
```

### Error Handling

```python
from agent import Agent, AgentConfig

config = AgentConfig(
    max_retries=5,
    retry_delay=2.0
)

agent = Agent("Bot", "Assistant", config=config)

try:
    response = agent.process("Hello!")
    print(response)
except Exception as e:
    print(f"Error: {e}")
```

## Tool Calling Details

### OpenAI Tool Schema Format

Tools must be defined in OpenAI's function calling format:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "tool_name",
            "description": "What the tool does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param1"]
            }
        }
    }
]
```

### Tool Executor Interface

Your tool executor must implement an `execute` method:

```python
class ToolRegistry:
    def execute(self, name: str, **kwargs) -> Any:
        """Execute tool by name with given arguments."""
        if name == "my_tool":
            return my_tool_function(**kwargs)
        raise ValueError(f"Unknown tool: {name}")
```

### Tool Calling Flow

1. User sends query with tools available
2. Agent decides if tools are needed
3. If yes, agent returns tool calls
4. Your executor runs the tools
5. Results are sent back to agent
6. Agent formulates final response
7. Process repeats until agent has final answer (max `max_turns` iterations)

## Model Options

### Recommended Models

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `gpt-4o` | Fast | Medium | General purpose, production |
| `gpt-4-turbo` | Medium | High | Complex reasoning, accuracy |
| `gpt-4o-mini` | Very Fast | Low | Simple tasks, high volume |
| `gpt-3.5-turbo` | Very Fast | Very Low | Basic queries, prototyping |

### Setting Model

```python
config = AgentConfig(model="gpt-4-turbo")
agent = Agent("Bot", "Assistant", config=config)
```

## Testing

### Basic Test

```python
python agent.py
```

Output:
```
Testing Agent class with OpenAI API...

Created: Agent(name='TestAgent', role='Testing assistant', model='gpt-4o', messages=0)
System prompt: You are TestAgent, a helpful AI assistant...

Test 1: Basic processing
Response: Hello, world!

Test 2: History management
Messages in history: 2
Token estimate: 15

After clearing: 0 messages

All tests completed successfully!
```

### Running Examples

```python
python example_usage.py
```

## Common Issues

### API Key Not Set

**Error:** `ValueError: OPENAI_API_KEY environment variable not set`

**Solution:**
```bash
export OPENAI_API_KEY='your-key-here'
```

### Rate Limiting

**Error:** `RateLimitError: You exceeded your current quota`

**Solution:**
- Check your OpenAI account billing
- Reduce request frequency
- Use lower-tier model

### Token Limit Exceeded

**Error:** `InvalidRequestError: maximum context length exceeded`

**Solution:**
```python
# Clear history periodically
if agent.get_token_count_estimate() > 3000:
    agent.clear_history()
```

### Tool Not Executing

**Problem:** Agent tries to call tool but it fails

**Solution:**
- Verify tool schema matches function signature
- Check tool executor's `execute` method
- Add error handling in tool functions

## Performance Tips

1. **Use appropriate models**: `gpt-4o-mini` for simple tasks
2. **Manage history**: Clear old messages to reduce tokens
3. **Configure retries**: Balance reliability vs speed
4. **Temperature settings**: Lower (0.3) for deterministic, higher (0.9) for creative
5. **Max tokens**: Set appropriately for your use case

## Integration with Framework

This Agent class is designed to integrate with:

- **Tool Registry**: For automatic schema generation
- **Orchestrator**: For multi-agent routing
- **CLI**: For command-line interface
- **Memory System**: For persistent conversation storage

See full framework documentation for integration examples.

## Differences from Anthropic Version

Key differences when migrating from Anthropic's Claude:

| Feature | OpenAI | Anthropic |
|---------|--------|-----------|
| Client | `openai.OpenAI()` | `anthropic.Anthropic()` |
| Model | `gpt-4o` | `claude-sonnet-4` |
| Tool format | `tools` parameter | `tools` parameter |
| Tool result | `role: "tool"` | `role: "user"` with tool_result |
| Message format | OpenAI format | Claude format |
| Finish reason | `stop`, `tool_calls` | `end_turn`, `tool_use` |

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check the examples in `example_usage.py`
- Review OpenAI's [function calling guide](https://platform.openai.com/docs/guides/function-calling)
- See framework documentation for integration help
