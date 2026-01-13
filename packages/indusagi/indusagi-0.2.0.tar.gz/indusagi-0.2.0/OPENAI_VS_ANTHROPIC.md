# OpenAI vs Anthropic Implementation Guide

Comprehensive comparison between OpenAI and Anthropic implementations for the indus-agents.

## Quick Reference Table

| Feature | OpenAI | Anthropic (Claude) |
|---------|--------|-------------------|
| **Client Library** | `openai` | `anthropic` |
| **Client Class** | `OpenAI()` | `Anthropic()` |
| **Default Model** | `gpt-4o` | `claude-sonnet-4-5-20250929` |
| **API Key Env** | `OPENAI_API_KEY` | `ANTHROPIC_API_KEY` |
| **Messages Format** | OpenAI format | Claude format |
| **Tool Parameter** | `tools` | `tools` |
| **Tool Format** | Function calling | Tool use |
| **Finish Reasons** | `stop`, `tool_calls`, `length`, `content_filter` | `end_turn`, `tool_use`, `max_tokens`, `stop_sequence` |

## Installation

### OpenAI
```bash
pip install openai>=1.12.0
```

### Anthropic
```bash
pip install anthropic>=0.35.0
```

## Client Initialization

### OpenAI
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Anthropic
```python
from anthropic import Anthropic
import os

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

## Basic Message Processing

### OpenAI
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=1024,
    temperature=0.7
)

text = response.choices[0].message.content
```

### Anthropic
```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=1024,
    temperature=0.7
)

text = response.content[0].text
```

## Key Differences

### 1. System Prompt Handling

**OpenAI:**
- System prompt is a message with `role: "system"`
- Included in the messages array
- Can have multiple system messages

```python
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hi"}
]
```

**Anthropic:**
- System prompt is a separate parameter
- Not in messages array
- Single system prompt only

```python
system = "You are helpful."
messages = [
    {"role": "user", "content": "Hi"}
]
```

### 2. Message Format

**OpenAI:**
```python
{
    "role": "user" | "assistant" | "system" | "tool",
    "content": "message text",
    "name": "optional_name",  # For tool messages
    "tool_calls": [...]  # For assistant tool calls
}
```

**Anthropic:**
```python
{
    "role": "user" | "assistant",
    "content": "message text" | [content_blocks]
}
```

### 3. Tool Calling

**OpenAI Tool Schema:**
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate math expressions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]
```

**Anthropic Tool Schema:**
```python
tools = [
    {
        "name": "calculator",
        "description": "Calculate math expressions",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression"
                }
            },
            "required": ["expression"]
        }
    }
]
```

### 4. Tool Response Format

**OpenAI:**
```python
# Assistant's tool call
{
    "role": "assistant",
    "content": null,
    "tool_calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "calculator",
                "arguments": '{"expression": "2+2"}'
            }
        }
    ]
}

# Tool result
{
    "role": "tool",
    "tool_call_id": "call_abc123",
    "name": "calculator",
    "content": "4"
}
```

**Anthropic:**
```python
# Assistant's tool use
{
    "role": "assistant",
    "content": [
        {"type": "text", "text": "I'll calculate that."},
        {
            "type": "tool_use",
            "id": "toolu_abc123",
            "name": "calculator",
            "input": {"expression": "2+2"}
        }
    ]
}

# Tool result
{
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": "toolu_abc123",
            "content": "4"
        }
    ]
}
```

### 5. Finish Reasons

**OpenAI:**
- `stop`: Natural completion
- `tool_calls`: Model wants to call tools
- `length`: Max tokens reached
- `content_filter`: Content filtered

**Anthropic:**
- `end_turn`: Natural completion
- `tool_use`: Model wants to use tools
- `max_tokens`: Token limit reached
- `stop_sequence`: Stop sequence encountered

## Code Migration

### Converting OpenAI to Anthropic

```python
# OpenAI version
def process_openai(user_input):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content

# Anthropic version
def process_anthropic(user_input):
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        system=system_prompt,
        messages=messages,
        max_tokens=1024
    )
    return response.content[0].text
```

### Converting Tool Calling Loop

**OpenAI:**
```python
while True:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )

    if response.choices[0].finish_reason == "stop":
        return response.choices[0].message.content

    if response.choices[0].finish_reason == "tool_calls":
        # Add assistant message
        messages.append(response.choices[0].message)

        # Execute tools
        for tool_call in response.choices[0].message.tool_calls:
            result = execute_tool(
                tool_call.function.name,
                json.loads(tool_call.function.arguments)
            )
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": str(result)
            })
```

**Anthropic:**
```python
while True:
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        system=system_prompt,
        messages=messages,
        tools=tools
    )

    if response.stop_reason == "end_turn":
        text = [b.text for b in response.content if hasattr(b, "text")]
        return " ".join(text)

    if response.stop_reason == "tool_use":
        # Add assistant message
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Execute tools
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result)
                })

        messages.append({
            "role": "user",
            "content": tool_results
        })
```

## Model Comparison

### OpenAI Models

| Model | Context | Speed | Cost | Best For |
|-------|---------|-------|------|----------|
| gpt-4o | 128K | Fast | Medium | General purpose, production |
| gpt-4-turbo | 128K | Medium | High | Complex reasoning |
| gpt-4o-mini | 128K | Very Fast | Low | Simple tasks |
| gpt-3.5-turbo | 16K | Very Fast | Very Low | Basic queries |

### Anthropic Models

| Model | Context | Speed | Cost | Best For |
|-------|---------|-------|------|----------|
| claude-sonnet-4-5 | 200K | Fast | Medium | General purpose, production |
| claude-opus-4 | 200K | Slow | High | Complex reasoning |
| claude-haiku-4 | 200K | Very Fast | Low | Simple tasks |

## Configuration Mapping

### OpenAI AgentConfig
```python
class AgentConfig(BaseModel):
    model: str = "gpt-4o"
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
```

### Anthropic AgentConfig
```python
class AgentConfig(BaseModel):
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 1.0
    top_k: int = 0
```

## Error Handling

### OpenAI Exceptions
```python
from openai import (
    OpenAIError,
    APIError,
    RateLimitError,
    InvalidRequestError
)

try:
    response = client.chat.completions.create(...)
except RateLimitError:
    # Rate limit hit
    pass
except InvalidRequestError:
    # Invalid parameters
    pass
except APIError:
    # API error
    pass
```

### Anthropic Exceptions
```python
from anthropic import (
    APIError,
    RateLimitError,
    ValidationError
)

try:
    response = client.messages.create(...)
except RateLimitError:
    # Rate limit hit
    pass
except ValidationError:
    # Invalid parameters
    pass
except APIError:
    # API error
    pass
```

## Pricing Comparison (As of 2025)

### OpenAI
- GPT-4o: $5/1M input, $15/1M output
- GPT-4-turbo: $10/1M input, $30/1M output
- GPT-4o-mini: $0.15/1M input, $0.60/1M output

### Anthropic
- Claude Sonnet 4.5: $3/1M input, $15/1M output
- Claude Opus 4: $15/1M input, $75/1M output
- Claude Haiku 4: $0.25/1M input, $1.25/1M output

## When to Use Each

### Choose OpenAI When:
- You need function calling with complex schemas
- You want more control over token generation (frequency/presence penalties)
- You're building on existing OpenAI integrations
- Cost is primary concern (gpt-4o-mini is very cheap)
- You need faster response times

### Choose Anthropic When:
- You need very long context windows (200K tokens)
- You want more natural, nuanced responses
- You're doing complex reasoning tasks
- You need better instruction following
- You want stronger safety features

## Performance Tips

### OpenAI
1. Use `gpt-4o-mini` for simple tasks
2. Set `frequency_penalty` > 0 to reduce repetition
3. Use `presence_penalty` > 0 for more diverse responses
4. Stream responses for long generations
5. Cache system prompts when possible

### Anthropic
1. Use Claude Haiku for simple tasks
2. Leverage longer context windows effectively
3. Use extended thinking for complex problems
4. Provide clear, detailed instructions
5. Use system prompts effectively

## Migration Checklist

When migrating between providers:

- [ ] Update client initialization
- [ ] Modify API call structure
- [ ] Convert message format
- [ ] Update tool schemas
- [ ] Change tool result format
- [ ] Modify finish reason checks
- [ ] Update error handling
- [ ] Test tool calling loop
- [ ] Verify conversation history
- [ ] Update configuration
- [ ] Test with production data
- [ ] Monitor costs and performance

## Conclusion

Both OpenAI and Anthropic provide excellent APIs for building AI agents. The choice depends on your specific requirements:

- **OpenAI**: Better for cost-sensitive applications, faster responses, and when you have existing OpenAI infrastructure
- **Anthropic**: Better for complex reasoning, long contexts, and when you need the most capable models

The indus-agents supports both with minimal code changes, allowing you to switch or use both based on your needs.
