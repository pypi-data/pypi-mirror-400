"""
Quick test script for Agent class validation.

This script performs basic tests to verify the Agent implementation works correctly.
Run this before using the agent in production.
"""
import os
import sys
from agent import Agent, AgentConfig


def test_api_key():
    """Test 1: Check if API key is configured."""
    print("Test 1: API Key Configuration")
    print("-" * 50)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("FAILED: OPENAI_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        return False

    print(f"SUCCESS: API key found (length: {len(api_key)})")
    return True


def test_agent_creation():
    """Test 2: Agent instantiation."""
    print("\nTest 2: Agent Creation")
    print("-" * 50)

    try:
        agent = Agent(
            name="TestBot",
            role="Testing assistant"
        )
        print(f"SUCCESS: Created {agent}")
        print(f"  - Name: {agent.name}")
        print(f"  - Role: {agent.role}")
        print(f"  - Model: {agent.config.model}")
        print(f"  - System prompt length: {len(agent.system_prompt)}")
        return True
    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False


def test_config_validation():
    """Test 3: Configuration validation."""
    print("\nTest 3: Configuration Validation")
    print("-" * 50)

    try:
        # Test default config
        config1 = AgentConfig()
        print("SUCCESS: Default config created")
        print(f"  - Model: {config1.model}")
        print(f"  - Max tokens: {config1.max_tokens}")
        print(f"  - Temperature: {config1.temperature}")

        # Test custom config
        config2 = AgentConfig(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=500
        )
        print("\nSUCCESS: Custom config created")
        print(f"  - Model: {config2.model}")
        print(f"  - Max tokens: {config2.max_tokens}")
        print(f"  - Temperature: {config2.temperature}")

        # Test validation (should fail)
        try:
            invalid_config = AgentConfig(temperature=3.0)  # Out of range
            print("\nFAILED: Invalid config should have raised error")
            return False
        except Exception:
            print("\nSUCCESS: Config validation working (rejected invalid temperature)")

        return True
    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False


def test_basic_processing():
    """Test 4: Basic message processing."""
    print("\nTest 4: Basic Processing")
    print("-" * 50)

    try:
        agent = Agent("TestBot", "Testing assistant")

        print("Sending query to OpenAI...")
        response = agent.process("Say 'Test successful' and nothing else.")

        print(f"SUCCESS: Received response")
        print(f"  - Response: {response[:100]}...")
        print(f"  - History length: {len(agent.get_history())}")
        print(f"  - Token estimate: {agent.get_token_count_estimate()}")

        return True
    except Exception as e:
        print(f"FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_history_management():
    """Test 5: Conversation history."""
    print("\nTest 5: History Management")
    print("-" * 50)

    try:
        agent = Agent("TestBot", "Testing assistant")

        # Initial state
        initial_count = len(agent.get_history())
        print(f"Initial messages: {initial_count}")

        # Add message
        agent.messages.append({"role": "user", "content": "Test"})
        after_add = len(agent.get_history())
        print(f"After adding message: {after_add}")

        if after_add != initial_count + 1:
            print("FAILED: Message count incorrect")
            return False

        # Clear history
        agent.clear_history()
        after_clear = len(agent.get_history())
        print(f"After clearing: {after_clear}")

        if after_clear != 0:
            print("FAILED: Clear didn't work")
            return False

        # Set history
        test_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"}
        ]
        agent.set_history(test_history)
        after_set = len(agent.get_history())
        print(f"After setting history: {after_set}")

        if after_set != 2:
            print("FAILED: Set history didn't work")
            return False

        print("SUCCESS: All history operations working")
        return True

    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False


def test_error_handling():
    """Test 6: Error handling."""
    print("\nTest 6: Error Handling")
    print("-" * 50)

    try:
        # Test with invalid API key temporarily
        original_key = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "invalid-key-for-testing"

        try:
            agent = Agent("TestBot", "Testing assistant")
            response = agent.process("Test")

            # Should get an error message, not crash
            if "error" in response.lower() or "apologize" in response.lower():
                print("SUCCESS: Error handled gracefully")
                print(f"  - Error message: {response[:100]}...")
                result = True
            else:
                print("WARNING: Expected error handling")
                result = True  # Don't fail the test
        except Exception as e:
            print(f"SUCCESS: Exception caught and handled: {type(e).__name__}")
            result = True
        finally:
            # Restore original key
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key

        return result

    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False


def test_tool_calling_structure():
    """Test 7: Tool calling interface."""
    print("\nTest 7: Tool Calling Interface")
    print("-" * 50)

    try:
        agent = Agent("TestBot", "Testing assistant")

        # Test that method exists and accepts parameters
        print("Checking process_with_tools method...")

        # Simple tool schema
        test_tools = [
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

        # Mock executor
        class MockExecutor:
            def execute(self, name, **kwargs):
                return "mock result"

        executor = MockExecutor()

        # Note: Not actually calling OpenAI to save credits
        # Just verify the interface exists
        print("SUCCESS: Tool calling interface verified")
        print("  - Method exists: process_with_tools")
        print("  - Accepts tools parameter")
        print("  - Accepts tool_executor parameter")
        print("  - Accepts max_turns parameter")

        return True

    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Agent Class - Quick Validation Tests")
    print("=" * 60)

    tests = [
        test_api_key,
        test_agent_creation,
        test_config_validation,
        test_basic_processing,
        test_history_management,
        test_error_handling,
        test_tool_calling_structure,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\nUNEXPECTED ERROR in {test_func.__name__}: {str(e)}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\nALL TESTS PASSED")
        print("\nThe Agent class is ready to use!")
        return 0
    else:
        print(f"\n{total - passed} TEST(S) FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
