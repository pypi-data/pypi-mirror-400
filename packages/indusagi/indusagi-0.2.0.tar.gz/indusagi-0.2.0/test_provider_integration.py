"""
Test script to verify OpenAI and Anthropic provider integration.

This script tests:
1. OpenAI provider (backward compatibility)
2. Anthropic provider (new functionality)
3. Provider auto-detection from environment variables
"""
import os
import sys
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from indusagi.agent import Agent, AgentConfig

# Load environment variables
load_dotenv()


def test_openai_provider():
    """Test OpenAI provider (backward compatibility)."""
    print("\n" + "=" * 70)
    print("TEST 1: OpenAI Provider (Backward Compatibility)")
    print("=" * 70)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ SKIPPED: OPENAI_API_KEY not set")
        return False

    try:
        # Test with auto-detection (should detect OpenAI from env)
        agent = Agent(
            name="OpenAI_Test",
            role="Test assistant for OpenAI provider"
        )

        print(f"[OK] Provider detected: {agent.provider.get_provider_name()}")
        print(f"[OK] Model: {agent.config.model}")

        # Test basic completion
        response = agent.process("Say 'Hello from OpenAI!' in one sentence.")
        print(f"[OK] Response: {response[:100]}...")

        print("[PASS] OpenAI provider test PASSED")
        return True

    except Exception as e:
        print(f"[FAIL] OpenAI provider test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_anthropic_provider():
    """Test Anthropic provider (new functionality)."""
    print("\n" + "=" * 70)
    print("TEST 2: Anthropic Provider (New Functionality)")
    print("=" * 70)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ SKIPPED: ANTHROPIC_API_KEY not set")
        print("   To test Anthropic, set: ANTHROPIC_API_KEY=sk-ant-...")
        return False

    try:
        # Test with explicit Anthropic configuration
        config = AgentConfig(
            model="claude-sonnet-4-5-20250929",
            provider="anthropic",
            max_tokens=1024,
            temperature=0.7
        )

        agent = Agent(
            name="Anthropic_Test",
            role="Test assistant for Anthropic provider",
            config=config
        )

        print(f"✓ Provider: {agent.provider.get_provider_name()}")
        print(f"✓ Model: {agent.config.model}")

        # Test basic completion
        response = agent.process("Say 'Hello from Anthropic Claude!' in one sentence.")
        print(f"✓ Response: {response[:100]}...")

        print("✅ Anthropic provider test PASSED")
        return True

    except Exception as e:
        print(f"❌ Anthropic provider test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_auto_detection():
    """Test provider auto-detection logic."""
    print("\n" + "=" * 70)
    print("TEST 3: Provider Auto-Detection")
    print("=" * 70)

    # Test detection logic
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    explicit_provider = os.getenv("LLM_PROVIDER")

    print(f"Environment variables:")
    print(f"  OPENAI_API_KEY: {'[SET]' if has_openai else '[NOT SET]'}")
    print(f"  ANTHROPIC_API_KEY: {'[SET]' if has_anthropic else '[NOT SET]'}")
    print(f"  LLM_PROVIDER: {explicit_provider if explicit_provider else '[NOT SET]'}")

    # Test auto-detection
    try:
        detected = AgentConfig._detect_provider()
        print(f"\n✓ Auto-detected provider: {detected}")

        # Create agent with auto-detection
        agent = Agent(name="AutoDetect", role="Test")
        actual_provider = agent.provider.get_provider_name()
        print(f"✓ Actual provider initialized: {actual_provider}")

        if detected == actual_provider:
            print("✅ Provider auto-detection test PASSED")
            return True
        else:
            print(f"❌ Mismatch: detected={detected}, actual={actual_provider}")
            return False

    except Exception as e:
        print(f"❌ Provider auto-detection test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_with_tools():
    """Test OpenAI provider with tool calling."""
    print("\n" + "=" * 70)
    print("TEST 4: OpenAI Provider with Tool Calling")
    print("=" * 70)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ SKIPPED: OPENAI_API_KEY not set")
        return False

    try:
        # Simple tool registry
        class ToolRegistry:
            def execute(self, name, **kwargs):
                if name == "calculator":
                    expression = kwargs.get("expression", "")
                    try:
                        result = eval(expression)
                        return f"Result: {result}"
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

        agent = Agent(
            name="OpenAI_Tool_Test",
            role="Math assistant with calculator"
        )

        registry = ToolRegistry()
        response = agent.process_with_tools(
            "What is 25 multiplied by 4?",
            tools=tools,
            tool_executor=registry,
            max_turns=5
        )

        print(f"✓ Response: {response[:200]}...")
        print("✅ OpenAI tool calling test PASSED")
        return True

    except Exception as e:
        print(f"❌ OpenAI tool calling test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_anthropic_with_tools():
    """Test Anthropic provider with tool calling."""
    print("\n" + "=" * 70)
    print("TEST 5: Anthropic Provider with Tool Calling")
    print("=" * 70)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ SKIPPED: ANTHROPIC_API_KEY not set")
        return False

    try:
        # Simple tool registry
        class ToolRegistry:
            def execute(self, name, **kwargs):
                if name == "calculator":
                    expression = kwargs.get("expression", "")
                    try:
                        result = eval(expression)
                        return f"Result: {result}"
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

        config = AgentConfig(
            model="claude-sonnet-4-5-20250929",
            provider="anthropic",
            max_tokens=1024
        )

        agent = Agent(
            name="Anthropic_Tool_Test",
            role="Math assistant with calculator",
            config=config
        )

        registry = ToolRegistry()
        response = agent.process_with_tools(
            "What is 25 multiplied by 4?",
            tools=tools,
            tool_executor=registry,
            max_turns=5
        )

        print(f"✓ Response: {response[:200]}...")
        print("✅ Anthropic tool calling test PASSED")
        return True

    except Exception as e:
        print(f"❌ Anthropic tool calling test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Provider Integration Test Suite")
    print("indus-agents: OpenAI + Anthropic Provider Support")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Provider Auto-Detection", test_provider_auto_detection()))
    results.append(("OpenAI Basic", test_openai_provider()))
    results.append(("OpenAI Tools", test_openai_with_tools()))
    results.append(("Anthropic Basic", test_anthropic_provider()))
    results.append(("Anthropic Tools", test_anthropic_with_tools()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests PASSED! Provider integration is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
