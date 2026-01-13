"""Simple test for OpenAI provider backward compatibility."""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from indusagi.agent import Agent, AgentConfig

load_dotenv()

print("="* 70)
print("OpenAI Provider Backward Compatibility Test")
print("=" * 70)

# Test 1: Provider auto-detection
print("\n[TEST 1] Provider auto-detection...")
try:
    agent = Agent(
        name="Test_Agent",
        role="Test assistant"
    )
    print(f"Provider: {agent.provider.get_provider_name()}")
    print(f"Model: {agent.config.model}")
    print("[PASS] Provider initialized successfully\n")
except Exception as e:
    print(f"[FAIL] {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Basic completion
print("[TEST 2] Basic completion...")
try:
    response = agent.process("Say 'Hello!' in one sentence.")
    print(f"Response: {response[:100]}")
    print("[PASS] Basic completion works\n")
except Exception as e:
    print(f"[FAIL] {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Tool calling
print("[TEST 3] Tool calling...")
try:
    class SimpleRegistry:
        def execute(self, name, **kwargs):
            if name == "calculator":
                expr = kwargs.get("expression", "")
                try:
                    return str(eval(expr))
                except:
                    return "Error"
            return "Unknown tool"

    tools = [{
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate math expressions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"]
            }
        }
    }]

    registry = SimpleRegistry()
    response = agent.process_with_tools(
        "What is 25 times 4?",
        tools=tools,
        tool_executor=registry,
        max_turns=5
    )
    print(f"Response: {response[:150]}")
    print("[PASS] Tool calling works\n")
except Exception as e:
    print(f"[FAIL] {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("ALL TESTS PASSED - OpenAI provider is working correctly!")
print("=" * 70)
