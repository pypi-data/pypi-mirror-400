"""
Quick integration test to verify the package works.
Tests all core components without making real API calls.
"""

print("=" * 70)
print("INTEGRATION TEST - indus-agents")
print("=" * 70)

# Test 1: Import package
print("\n[1/7] Testing package import...")
try:
    import indusagi
    print(f"[OK] Package imported successfully")
    print(f"  Version: {indusagi.__version__}")
except Exception as e:
    print(f"[FAIL] Failed to import package: {e}")
    exit(1)

# Test 2: Import core components
print("\n[2/7] Testing core component imports...")
try:
    from indusagi import (
        Agent, AgentConfig,
        ToolRegistry, registry,
        MultiAgentOrchestrator, create_orchestrator,
        ConversationMemory, Message
    )
    print(f"[OK] All core components imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import components: {e}")
    exit(1)

# Test 3: Test tool registry
print("\n[3/7] Testing tool registry...")
try:
    tools = registry.list_tools()
    print(f"[OK] Tool registry working")
    print(f"  Found {len(tools)} tools: {', '.join(tools[:3])}...")
except Exception as e:
    print(f"[FAIL] Tool registry failed: {e}")
    exit(1)

# Test 4: Test tool execution (no API needed)
print("\n[4/7] Testing tool execution...")
try:
    result = registry.execute("calculator", expression="25 * 4")
    assert "100" in result, f"Expected 100, got {result}"
    print(f"[OK] Tool execution working")
    print(f"  calculator(25 * 4) = {result}")
except Exception as e:
    print(f"[FAIL] Tool execution failed: {e}")
    exit(1)

# Test 5: Test memory system
print("\n[5/7] Testing memory system...")
try:
    memory = ConversationMemory(max_messages=10)
    memory.add_message("user", "Hello!")
    memory.add_message("assistant", "Hi there!")
    messages = memory.get_messages()
    assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
    print(f"[OK] Memory system working")
    print(f"  Stored {len(messages)} messages")
except Exception as e:
    print(f"[FAIL] Memory system failed: {e}")
    exit(1)

# Test 6: Test Agent creation (without API call)
print("\n[6/7] Testing agent creation...")
try:
    import os
    # Set dummy API key for testing (not used in this test)
    os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key-for-testing"

    config = AgentConfig(model="gpt-4o", max_tokens=100)
    agent = Agent("TestBot", "Test assistant", config=config)
    print(f"[OK] Agent creation working")
    print(f"  Agent: {agent.name}")
    print(f"  Model: {agent.config.model}")
except Exception as e:
    print(f"[FAIL] Agent creation failed: {e}")
    exit(1)

# Test 7: Test CLI imports
print("\n[7/7] Testing CLI module...")
try:
    from indusagi import cli
    print(f"[OK] CLI module imported successfully")
except Exception as e:
    print(f"[FAIL] CLI import failed: {e}")
    exit(1)

# Summary
print("\n" + "=" * 70)
print("INTEGRATION TEST PASSED")
print("=" * 70)
print("\n>>> All core components are working correctly!")
print("\nNext steps:")
print("  1. Set your OPENAI_API_KEY in .env")
print("  2. Run: indusagi test-connection")
print("  3. Try: indusagi run 'What is 25 * 48?'")
print("  4. Or: indusagi interactive")
print("\n" + "=" * 70)
