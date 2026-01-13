"""
Test script demonstrating OpenAI integration with the tool registry.

This shows how the tool schemas work with OpenAI's function calling API.
"""

from tools import registry
import json


def demonstrate_openai_integration():
    """Demonstrate how to use the registry with OpenAI."""

    print("=" * 70)
    print("OpenAI Integration Demo")
    print("=" * 70)

    # Get all tool schemas
    schemas = registry.schemas

    print(f"\n1. Total tools available: {len(schemas)}")
    print("\nTool names:")
    for schema in schemas:
        print(f"   - {schema['function']['name']}")

    # Show a complete schema example
    print("\n2. Complete OpenAI Schema Example (calculator):")
    print("-" * 70)
    calculator_schema = next(
        s for s in schemas if s['function']['name'] == 'calculator'
    )
    print(json.dumps(calculator_schema, indent=2))

    # Simulate OpenAI function call response
    print("\n3. Simulating OpenAI Function Call:")
    print("-" * 70)

    # This is what OpenAI would return
    simulated_tool_call = {
        "name": "calculator",
        "arguments": '{"expression": "25 * 4"}'
    }

    print(f"Function name: {simulated_tool_call['name']}")
    print(f"Arguments: {simulated_tool_call['arguments']}")

    # Parse and execute
    args = json.loads(simulated_tool_call['arguments'])
    result = registry.execute(simulated_tool_call['name'], **args)

    print(f"Result: {result}")

    # Show how to format for OpenAI response
    print("\n4. OpenAI Tool Result Format:")
    print("-" * 70)
    tool_result = {
        "tool_call_id": "call_abc123",  # Would come from OpenAI
        "role": "tool",
        "name": "calculator",
        "content": result
    }
    print(json.dumps(tool_result, indent=2))

    # Multiple tool calls
    print("\n5. Multiple Tool Calls Example:")
    print("-" * 70)
    multi_calls = [
        {"name": "get_time", "arguments": "{}"},
        {"name": "calculator", "arguments": '{"expression": "100/4"}'},
        {"name": "text_uppercase", "arguments": '{"text": "hello"}'}
    ]

    for i, call in enumerate(multi_calls, 1):
        args = json.loads(call['arguments'])
        result = registry.execute(call['name'], **args)
        print(f"   Call {i}: {call['name']}() -> {result}")

    print("\n" + "=" * 70)
    print("Integration demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_openai_integration()

    print("\n\nCODE EXAMPLE FOR YOUR AGENT:")
    print("-" * 70)
    print("""
# In your agent code:
import openai
from tools import registry

client = openai.OpenAI()

# Get tools
tools = registry.schemas

# Make request
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "What is 25 * 4?"}],
    tools=tools,
    tool_choice="auto"
)

# Process tool calls
message = response.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        # Execute tool
        result = registry.execute(
            tool_call.function.name,
            **json.loads(tool_call.function.arguments)
        )
        print(f"Result: {result}")
""")
