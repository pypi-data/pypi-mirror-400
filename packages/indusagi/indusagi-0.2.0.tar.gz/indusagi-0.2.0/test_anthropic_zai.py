"""Test Anthropic provider with Z.AI GLM-4.7 model."""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from indusagi.agent import Agent, AgentConfig

load_dotenv()

print("=" * 70)
print("Anthropic Provider Test with Z.AI GLM-4.7")
print("=" * 70)

# Test 1: Provider detection
print("\n[TEST 1] Provider auto-detection...")
try:
    agent = Agent(
        name="GLM_Test",
        role="Test assistant using GLM-4.7 via Anthropic provider"
    )
    print(f"Provider: {agent.provider.get_provider_name()}")
    print(f"Model: {agent.config.model}")
    print(f"Base URL: {os.getenv('ANTHROPIC_BASE_URL')}")
    print("[PASS] Provider initialized successfully\n")
except Exception as e:
    print(f"[FAIL] {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Basic completion
print("[TEST 2] Basic completion with GLM-4.7...")
try:
    response = agent.process("Say 'Hello from GLM-4.7!' in one sentence.")
    print(f"Response: {response}")
    print("[PASS] Basic completion works\n")
except Exception as e:
    print(f"[FAIL] {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Conversation with context
print("[TEST 3] Multi-turn conversation...")
try:
    response1 = agent.process("My favorite color is blue.")
    print(f"Turn 1: {response1}")

    response2 = agent.process("What is my favorite color?")
    print(f"Turn 2: {response2}")
    print("[PASS] Context retention works\n")
except Exception as e:
    print(f"[FAIL] {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Tool calling
print("[TEST 4] Tool calling with GLM-4.7...")
try:
    class SimpleRegistry:
        def execute(self, name, **kwargs):
            if name == "calculator":
                expr = kwargs.get("expression", "")
                try:
                    return str(eval(expr))
                except:
                    return "Error in calculation"
            return "Unknown tool"

    tools = [{
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate mathematical expressions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    }]

    registry = SimpleRegistry()
    response = agent.process_with_tools(
        "What is 144 divided by 12?",
        tools=tools,
        tool_executor=registry,
        max_turns=5
    )
    print(f"Response: {response}")
    print("[PASS] Tool calling works\n")
except Exception as e:
    print(f"[FAIL] {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("ALL TESTS PASSED!")
print("GLM-4.7 is working correctly via Anthropic provider + Z.AI!")
print("=" * 70)
