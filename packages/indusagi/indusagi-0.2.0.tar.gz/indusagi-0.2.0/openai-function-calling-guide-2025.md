# OpenAI Function Calling Guide - 2025

A comprehensive guide to function calling (tool use) with the OpenAI Python SDK, including current best practices, complete examples, and comparisons with Anthropic's approach.

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Function Calling Overview](#function-calling-overview)
3. [Complete Working Example](#complete-working-example)
4. [Tool Schema Format](#tool-schema-format)
5. [Request/Response Flow](#requestresponse-flow)
6. [Structured Outputs & Strict Mode](#structured-outputs--strict-mode)
7. [Error Handling Patterns](#error-handling-patterns)
8. [Best Practices](#best-practices)
9. [OpenAI vs Anthropic Differences](#openai-vs-anthropic-differences)
10. [Advanced Features](#advanced-features)

---

## Installation & Setup

### Current Version

**OpenAI Python SDK Version: 2.7.1** (Released November 4, 2025)

### Installation

```bash
# Basic installation
pip install openai

# With async support (recommended)
pip install openai[aiohttp]
```

### Requirements

- Python 3.8 or higher (supports up to Python 3.13)
- OpenAI API key

### Basic Setup

```python
from openai import OpenAI
import os

# Initialize the client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
```

---

## Function Calling Overview

Function calling (also called "tool calling") allows OpenAI models to:

1. Detect when a function should be called based on user input
2. Generate structured JSON with the appropriate arguments
3. Return the function call details to your application
4. Incorporate function results back into the conversation

Key terminology:
- **Tools**: The array of functions you define for the model
- **Tool Calls**: The model's request to execute one or more functions
- **Tool Choice**: Control over whether/when the model calls functions

---

## Complete Working Example

Here's a complete, production-ready example implementing weather lookup with function calling:

```python
import json
from openai import OpenAI
import os

# Initialize client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Step 1: Define your tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            }
        }
    }
]

# Step 2: Define the actual function implementation
def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
    """
    Simulate getting weather data.
    In production, this would call a real weather API.
    """
    # Mock weather data
    weather_data = {
        "San Francisco, CA": {"temperature": 68, "conditions": "sunny"},
        "New York, NY": {"temperature": 55, "conditions": "cloudy"},
        "London, UK": {"temperature": 50, "conditions": "rainy"}
    }

    location_data = weather_data.get(location, {"temperature": 70, "conditions": "unknown"})

    if unit == "celsius":
        location_data["temperature"] = int((location_data["temperature"] - 32) * 5/9)

    return json.dumps(location_data)

# Step 3: Create the initial chat completion request
messages = [
    {
        "role": "user",
        "content": "What's the weather like in San Francisco?"
    }
]

response = client.chat.completions.create(
    model="gpt-4o-mini",  # or gpt-4o, gpt-4-turbo, etc.
    messages=messages,
    tools=tools,
    tool_choice="auto"  # Let the model decide when to call functions
)

# Step 4: Process the response
response_message = response.choices[0].message
messages.append(response_message)

# Check if the model wants to call a function
if response_message.tool_calls:
    # Step 5: Execute the function calls
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print(f"Function called: {function_name}")
        print(f"Arguments: {function_args}")

        # Call the appropriate function
        if function_name == "get_current_weather":
            function_response = get_current_weather(
                location=function_args.get("location"),
                unit=function_args.get("unit", "fahrenheit")
            )

            # Step 6: Add the function response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_response
            })

    # Step 7: Get the final response from the model
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    print("\nFinal Response:")
    print(final_response.choices[0].message.content)
else:
    # No function call was made
    print(response_message.content)
```

### Expected Output

```
Function called: get_current_weather
Arguments: {'location': 'San Francisco, CA'}

Final Response:
The current weather in San Francisco is sunny with a temperature of 68°F.
```

---

## Tool Schema Format

### Basic Structure

Tools are defined using JSON Schema format:

```python
tools = [
    {
        "type": "function",  # Always "function"
        "function": {
            "name": "function_name",  # Must be valid identifier
            "description": "Clear description of what the function does",  # Max 1024 chars
            "parameters": {
                "type": "object",
                "properties": {
                    "param_name": {
                        "type": "string",  # or "number", "boolean", "array", "object"
                        "description": "Description of this parameter",
                        "enum": ["option1", "option2"]  # Optional: restrict values
                    }
                },
                "required": ["param_name"],  # List of required parameters
                "additionalProperties": False  # Recommended for strict mode
            }
        }
    }
]
```

### Supported JSON Schema Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text value | `"San Francisco"` |
| `number` | Numeric value (int or float) | `42`, `3.14` |
| `boolean` | True/false | `true`, `false` |
| `array` | List of items | `["item1", "item2"]` |
| `object` | Nested object | `{"key": "value"}` |
| `null` | Null value | `null` |

### Advanced Schema Example

```python
{
    "type": "function",
    "function": {
        "name": "search_products",
        "description": "Search for products in the inventory database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string"
                },
                "category": {
                    "type": "string",
                    "enum": ["electronics", "clothing", "books", "home"],
                    "description": "Product category to filter by"
                },
                "price_range": {
                    "type": "object",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "Minimum price in USD"
                        },
                        "max": {
                            "type": "number",
                            "description": "Maximum price in USD"
                        }
                    }
                },
                "in_stock": {
                    "type": "boolean",
                    "description": "Only show items in stock"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Filter by product tags"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
}
```

---

## Request/Response Flow

### 1. Initial Request

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What's the weather?"}],
    tools=tools,
    tool_choice="auto"  # "auto", "none", or {"type": "function", "function": {"name": "func_name"}}
)
```

### 2. Response with Tool Call

```python
# Response structure when model wants to call a function
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1699896916,
    "model": "gpt-4o-mini",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": null,
            "tool_calls": [
                {
                    "id": "call_abc123",
                    "type": "function",
                    "function": {
                        "name": "get_current_weather",
                        "arguments": "{\"location\": \"San Francisco, CA\", \"unit\": \"fahrenheit\"}"
                    }
                }
            ]
        },
        "finish_reason": "tool_calls"
    }],
    "usage": {...}
}
```

### 3. Function Execution & Response

```python
# Parse the tool call
tool_call = response.choices[0].message.tool_calls[0]
function_args = json.loads(tool_call.function.arguments)

# Execute your function
result = your_function(**function_args)

# Add to message history
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": tool_call.function.name,
    "content": str(result)  # Must be string
})
```

### 4. Final Response

```python
# Get final answer from model
final_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages  # Includes user msg, assistant tool call, and tool result
)

answer = final_response.choices[0].message.content
```

### Tool Choice Options

```python
# Auto: Let model decide (default)
tool_choice="auto"

# None: Force model NOT to call functions
tool_choice="none"

# Required: Force model to call at least one function
tool_choice="required"

# Specific: Force model to call a specific function
tool_choice={
    "type": "function",
    "function": {"name": "get_current_weather"}
}
```

---

## Structured Outputs & Strict Mode

### Overview

Structured Outputs (introduced August 2024) ensures the model's output **exactly** matches your JSON schema. This is critical for production systems.

### Enabling Strict Mode

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_delivery_date",
            "description": "Get estimated delivery date for an order",
            "strict": True,  # Enable strict mode
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False  # Required for strict mode
            }
        }
    }
]
```

### Using Pydantic Models

The SDK provides a helper to convert Pydantic models to function schemas:

```python
from pydantic import BaseModel
from openai import OpenAI
import openai

class GetDeliveryDate(BaseModel):
    order_id: str

class SearchProducts(BaseModel):
    query: str
    max_results: int = 10
    category: str | None = None

# Convert Pydantic models to tools
tools = [
    openai.pydantic_function_tool(GetDeliveryDate),
    openai.pydantic_function_tool(SearchProducts)
]

# Use in API call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "When will order #12345 arrive?"}],
    tools=tools
)
```

### Parsing Responses with Pydantic

```python
from openai import OpenAI

client = OpenAI()

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

completion = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Extract event information."},
        {"role": "user", "content": "Team meeting tomorrow at 2pm with Alice and Bob"}
    ],
    tools=[openai.pydantic_function_tool(CalendarEvent)]
)

# Automatically parsed into Pydantic model
event = completion.choices[0].message.tool_calls[0].function.parsed_arguments
print(event.name)  # "Team meeting"
print(event.participants)  # ["Alice", "Bob"]
```

### Important Constraints for Strict Mode

1. **Set `additionalProperties: False`** in all object schemas
2. **All fields must have explicit types** (no `any` type)
3. **Cannot use parallel function calls** - set `parallel_tool_calls=False`
4. **Supported models**: gpt-4o-mini, gpt-4o, gpt-4o-2024-08-06 and later

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    parallel_tool_calls=False  # Required for strict mode
)
```

---

## Error Handling Patterns

### Basic Error Handling

```python
import openai
from openai import OpenAI

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    # Process response...

except openai.RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    # Implement exponential backoff

except openai.AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Check API key

except openai.APIConnectionError as e:
    print(f"Connection error: {e}")
    # Retry with backoff

except openai.APITimeoutError as e:
    print(f"Request timed out: {e}")
    # Retry

except openai.BadRequestError as e:
    print(f"Invalid request: {e}")
    # Check parameters

except openai.APIError as e:
    print(f"API error: {e}")
    # General error handling
```

### Production-Ready Error Handling with Retry Logic

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import openai
from openai import OpenAI

client = OpenAI()

@retry(
    retry=retry_if_exception_type((
        openai.RateLimitError,
        openai.APIConnectionError,
        openai.APITimeoutError
    )),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5)
)
def call_openai_with_retry(messages, tools):
    """Make OpenAI API call with automatic retry logic."""
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

# Usage
try:
    response = call_openai_with_retry(messages, tools)
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Function Call Validation

```python
import json
from jsonschema import validate, ValidationError

def execute_function_call(tool_call, available_functions):
    """
    Safely execute a function call with validation.
    """
    function_name = tool_call.function.name

    # Validate function exists
    if function_name not in available_functions:
        return json.dumps({
            "error": f"Function '{function_name}' not found",
            "available_functions": list(available_functions.keys())
        })

    try:
        # Parse arguments
        function_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Invalid JSON arguments: {str(e)}"
        })

    try:
        # Execute function
        function_to_call = available_functions[function_name]
        result = function_to_call(**function_args)
        return json.dumps({"result": result})

    except TypeError as e:
        return json.dumps({
            "error": f"Invalid arguments for {function_name}: {str(e)}"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Function execution failed: {str(e)}"
        })

# Usage
available_functions = {
    "get_current_weather": get_current_weather,
    "search_products": search_products
}

for tool_call in response_message.tool_calls:
    result = execute_function_call(tool_call, available_functions)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": tool_call.function.name,
        "content": result
    })
```

### Handling Model Refusals

```python
response_message = response.choices[0].message

# Check for refusals (when model refuses to call a function)
if hasattr(response_message, 'refusal') and response_message.refusal:
    print(f"Model refused: {response_message.refusal}")
    # Handle refusal case
elif response_message.tool_calls:
    # Process tool calls
    pass
else:
    # Normal text response
    print(response_message.content)
```

---

## Best Practices

### 1. Function Descriptions

Write clear, concise descriptions (max 1024 characters):

```python
# Good: Clear and specific
"description": "Get the current weather conditions for a specified location"

# Bad: Vague or too brief
"description": "Weather"

# Good: Detailed parameter description
"location": {
    "type": "string",
    "description": "City and state/country, e.g., 'Paris, France' or 'Tokyo, Japan'"
}
```

### 2. Tool Quantity Guidelines

Based on OpenAI's recommendations (May 2025):
- **Optimal**: Fewer than 100 tools
- **Optimal arguments**: Fewer than 20 arguments per tool
- **Use flat structures**: Avoid deep nesting when possible

```python
# Good: Flat structure
{
    "user_name": {"type": "string"},
    "user_email": {"type": "string"},
    "user_age": {"type": "number"}
}

# Less optimal: Nested structure
{
    "user": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "age": {"type": "number"}
        }
    }
}
```

### 3. Use Enums for Constrained Values

```python
"unit": {
    "type": "string",
    "enum": ["celsius", "fahrenheit", "kelvin"],
    "description": "Temperature unit"
}
```

### 4. Always Set additionalProperties

```python
"parameters": {
    "type": "object",
    "properties": {...},
    "additionalProperties": False  # Prevents unexpected parameters
}
```

### 5. Handle Parallel Function Calls

Models can call multiple functions simultaneously:

```python
# Enable parallel calls (default)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    parallel_tool_calls=True  # Model can call multiple functions
)

# Process multiple tool calls
if response_message.tool_calls:
    for tool_call in response_message.tool_calls:
        # Execute each function
        result = execute_function(tool_call)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": result
        })
```

### 6. Prevent Hallucinations

Add explicit instructions:

```python
system_message = """
You are a helpful assistant with access to specific functions.
IMPORTANT:
- Only call functions that are actually available
- Never promise to call functions in the future
- If a function doesn't exist, explain what you CAN do instead
- Always use the exact function names provided
"""

messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_input}
]
```

### 7. Model Selection

Choose the right model for your use case:

| Model | Best For | Function Calling Quality |
|-------|----------|-------------------------|
| `gpt-4o` | Production, complex reasoning | Excellent |
| `gpt-4o-mini` | Cost-effective, simple tasks | Very Good |
| `gpt-4-turbo` | Legacy applications | Good |
| `o3-mini`, `o1` | Supports tool_choice parameter | Excellent |

---

## OpenAI vs Anthropic Differences

### Key Architectural Differences

| Aspect | OpenAI | Anthropic Claude |
|--------|--------|------------------|
| **Terminology** | Function Calling / Tool Calling | Tool Use |
| **Message Format** | Separate tool calls from content | Tool use as content items |
| **Tool Types** | Only client-side tools | Client tools + server tools (e.g., built-in web search) |
| **Schema Strictness** | Strict mode available (`strict: true`) | No strict mode - schema compliance not guaranteed |
| **Parallel Calls** | Supported (can be disabled) | Supported |
| **Response Format** | `tool_calls` array in message | `stop_reason: "tool_use"` with content blocks |

### Message Structure Comparison

#### OpenAI Format

```python
# Tool call from model
{
    "role": "assistant",
    "content": null,
    "tool_calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "SF"}'
            }
        }
    ]
}

# Tool response to model
{
    "role": "tool",
    "tool_call_id": "call_abc123",
    "name": "get_weather",
    "content": '{"temperature": 68}'
}
```

#### Anthropic Format

```python
# Tool use from model
{
    "role": "assistant",
    "content": [
        {
            "type": "tool_use",
            "id": "toolu_abc123",
            "name": "get_weather",
            "input": {"location": "SF"}
        }
    ],
    "stop_reason": "tool_use"
}

# Tool result to model
{
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": "toolu_abc123",
            "content": '{"temperature": 68}'
        }
    ]
}
```

### When to Choose Each

**Choose OpenAI if you need:**
- Strict schema validation (guaranteed format compliance)
- Broader ecosystem support
- More model options
- Fine-tuning for function calling

**Choose Anthropic if you need:**
- Content-based architecture
- Built-in server tools (web search, computer use)
- Longer context windows (up to 200K tokens)
- Strong performance on complex reasoning

### Migration Notes

Converting from Anthropic to OpenAI:

```python
# Anthropic style
tools = [{
    "name": "get_weather",
    "description": "Get weather",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}]

# OpenAI style (wrap in function object)
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather",
        "parameters": {  # Changed from input_schema
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]
```

---

## Advanced Features

### 1. Parallel Function Calling

Execute multiple functions in one turn:

```python
messages = [
    {"role": "user", "content": "What's the weather in NYC and London, and search for umbrellas?"}
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    parallel_tool_calls=True
)

# Response may contain multiple tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Calling: {tool_call.function.name}")
        # Execute all functions (potentially in parallel using asyncio)
```

### 2. Async Function Calling

```python
from openai import AsyncOpenAI
import asyncio

async_client = AsyncOpenAI()

async def async_function_calling():
    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    if response.choices[0].message.tool_calls:
        # Execute functions asynchronously
        tasks = []
        for tool_call in response.choices[0].message.tool_calls:
            task = execute_async_function(tool_call)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Add results to messages
        for tool_call, result in zip(response.choices[0].message.tool_calls, results):
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": result
            })

        # Get final response
        final_response = await async_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        return final_response.choices[0].message.content

# Run async function
result = asyncio.run(async_function_calling())
```

### 3. Streaming with Function Calls

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    stream=True
)

tool_calls_buffer = []

for chunk in response:
    delta = chunk.choices[0].delta

    if delta.tool_calls:
        # Buffer tool call chunks
        for tool_call_chunk in delta.tool_calls:
            if len(tool_calls_buffer) <= tool_call_chunk.index:
                tool_calls_buffer.append({
                    "id": "",
                    "type": "function",
                    "function": {"name": "", "arguments": ""}
                })

            tc = tool_calls_buffer[tool_call_chunk.index]

            if tool_call_chunk.id:
                tc["id"] = tool_call_chunk.id
            if tool_call_chunk.function.name:
                tc["function"]["name"] += tool_call_chunk.function.name
            if tool_call_chunk.function.arguments:
                tc["function"]["arguments"] += tool_call_chunk.function.arguments

    if chunk.choices[0].finish_reason == "tool_calls":
        # Process complete tool calls
        for tool_call in tool_calls_buffer:
            print(f"Function: {tool_call['function']['name']}")
            print(f"Arguments: {tool_call['function']['arguments']}")
```

### 4. Fine-Tuning for Function Calling

OpenAI supports fine-tuning models for better function calling performance:

```python
# Prepare training data (JSONL format)
training_data = [
    {
        "messages": [
            {"role": "user", "content": "What's the weather?"},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"location": "current"}'
                        }
                    }
                ]
            }
        ],
        "tools": tools
    }
]

# Create fine-tuning job (requires OpenAI paid account)
# See: https://platform.openai.com/docs/guides/fine-tuning
```

### 5. OpenAI Agents SDK (New in 2025)

OpenAI released a new Agents SDK that simplifies function calling:

```python
from openai import Agent

# Define function with decorator
@function_tool
def fetch_weather(location: str) -> dict:
    """Fetch weather for a location."""
    # Implementation
    return {"temperature": 68, "conditions": "sunny"}

# Create agent with automatic tool registration
agent = Agent(
    model="gpt-4o-mini",
    tools=[fetch_weather]  # Automatically generates schema
)

# Run agent
response = agent.run("What's the weather in SF?")
print(response)
```

---

## Complete Multi-Function Example

Here's a comprehensive example with multiple functions, error handling, and best practices:

```python
import json
import os
from typing import Optional, Dict, Any
from openai import OpenAI
import openai

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define multiple functions
def get_weather(location: str, unit: str = "fahrenheit") -> str:
    """Get current weather for a location."""
    # Mock implementation
    return json.dumps({
        "location": location,
        "temperature": 72,
        "unit": unit,
        "conditions": "sunny"
    })

def search_restaurants(
    location: str,
    cuisine: Optional[str] = None,
    price_range: Optional[str] = None
) -> str:
    """Search for restaurants."""
    # Mock implementation
    results = [
        {"name": "Italian Bistro", "cuisine": "Italian", "rating": 4.5},
        {"name": "Sushi Palace", "cuisine": "Japanese", "rating": 4.8}
    ]
    if cuisine:
        results = [r for r in results if r["cuisine"].lower() == cuisine.lower()]
    return json.dumps({"restaurants": results})

def book_reservation(
    restaurant_name: str,
    date: str,
    time: str,
    party_size: int
) -> str:
    """Book a restaurant reservation."""
    # Mock implementation
    return json.dumps({
        "confirmation_id": "RES-12345",
        "restaurant": restaurant_name,
        "date": date,
        "time": time,
        "party_size": party_size,
        "status": "confirmed"
    })

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specified location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state/country, e.g., 'Paris, France'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "Search for restaurants in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City to search in"
                    },
                    "cuisine": {
                        "type": "string",
                        "description": "Type of cuisine (e.g., 'Italian', 'Japanese')"
                    },
                    "price_range": {
                        "type": "string",
                        "enum": ["$", "$$", "$$$", "$$$$"],
                        "description": "Price range"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_reservation",
            "description": "Book a restaurant reservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {
                        "type": "string",
                        "description": "Name of the restaurant"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time in HH:MM format (24-hour)"
                    },
                    "party_size": {
                        "type": "number",
                        "description": "Number of guests"
                    }
                },
                "required": ["restaurant_name", "date", "time", "party_size"],
                "additionalProperties": False
            }
        }
    }
]

# Map function names to implementations
available_functions = {
    "get_weather": get_weather,
    "search_restaurants": search_restaurants,
    "book_reservation": book_reservation
}

def run_conversation(user_input: str) -> str:
    """
    Run a complete conversation with function calling.
    """
    messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant that can check weather,
            search restaurants, and book reservations. Always be specific and helpful."""
        },
        {"role": "user", "content": user_input}
    ]

    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message

            # Check if we're done
            if not response_message.tool_calls:
                return response_message.content

            # Add assistant's response to messages
            messages.append(response_message)

            # Execute all function calls
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name

                print(f"\n[Function Call] {function_name}")

                try:
                    function_args = json.loads(tool_call.function.arguments)
                    print(f"[Arguments] {function_args}")

                    # Get function to call
                    function_to_call = available_functions.get(function_name)

                    if function_to_call is None:
                        function_response = json.dumps({
                            "error": f"Function {function_name} not found"
                        })
                    else:
                        # Call the function
                        function_response = function_to_call(**function_args)
                        print(f"[Result] {function_response}")

                    # Add function response to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response
                    })

                except json.JSONDecodeError as e:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps({"error": f"Invalid JSON: {str(e)}"})
                    })
                except Exception as e:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps({"error": str(e)})
                    })

        except openai.RateLimitError:
            return "Rate limit exceeded. Please try again later."
        except openai.AuthenticationError:
            return "Authentication error. Please check your API key."
        except openai.APIError as e:
            return f"API error: {str(e)}"

    return "Maximum iterations reached. Please try again with a simpler request."

# Example usage
if __name__ == "__main__":
    # Test single function
    result1 = run_conversation("What's the weather like in San Francisco?")
    print(f"\n[Final Response]\n{result1}\n")

    # Test multiple functions
    result2 = run_conversation(
        "I'm visiting New York tomorrow. What's the weather and can you find Italian restaurants?"
    )
    print(f"\n[Final Response]\n{result2}\n")

    # Test complex multi-step
    result3 = run_conversation(
        "Book a table for 4 at Italian Bistro tomorrow at 7pm"
    )
    print(f"\n[Final Response]\n{result3}\n")
```

---

## Additional Resources

### Official Documentation
- OpenAI Function Calling Guide: https://platform.openai.com/docs/guides/function-calling
- OpenAI API Reference: https://platform.openai.com/docs/api-reference
- OpenAI Cookbook: https://cookbook.openai.com/
- Python SDK GitHub: https://github.com/openai/openai-python

### Related Guides
- Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- Fine-tuning Guide: https://platform.openai.com/docs/guides/fine-tuning

### Best Practices Articles
- Function Calling Best Practices (Jan 2025): https://platform.openai.com/docs/guides/function-calling
- Prompting Guide: https://www.promptingguide.ai/applications/function_calling

---

## Summary

This guide covers the complete OpenAI function calling workflow for 2025:

1. Install OpenAI Python SDK 2.7.1+
2. Define tools with clear JSON schemas
3. Make API calls with `tools` parameter
4. Handle `tool_calls` in responses
5. Execute functions and return results
6. Use strict mode for guaranteed schema compliance
7. Implement proper error handling
8. Follow best practices for production systems

Key differences from Anthropic:
- OpenAI uses `tool_calls` array vs Anthropic's content blocks
- OpenAI offers strict mode for schema validation
- OpenAI has `tool_choice` for explicit control
- Response format differs but workflow is similar

The SDK is actively maintained with excellent documentation and broad ecosystem support.
