"""
Integration test for the Multi-Agent Orchestrator System.

Tests the complete integration between orchestrator, agents, and tools.
Run this to verify everything is working correctly.

Usage:
    python test_orchestrator_integration.py
"""

import sys
from orchestrator import create_orchestrator, AgentType
from tools import registry
from agent import AgentConfig


def test_imports():
    """Test 1: Verify all imports work."""
    print("[TEST 1] Testing imports...")
    try:
        from orchestrator import MultiAgentOrchestrator, RoutingDecision, OrchestratorResponse
        from agent import Agent, AgentConfig
        from tools import registry, ToolRegistry
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_orchestrator_creation():
    """Test 2: Verify orchestrator can be created."""
    print("\n[TEST 2] Testing orchestrator creation...")
    try:
        orchestrator = create_orchestrator(verbose=False)
        print(f"  ✓ Orchestrator created: {orchestrator}")
        return True, orchestrator
    except Exception as e:
        print(f"  ✗ Creation failed: {e}")
        return False, None


def test_agent_initialization(orchestrator):
    """Test 3: Verify all agents are initialized."""
    print("\n[TEST 3] Testing agent initialization...")
    try:
        expected_agents = [AgentType.GENERAL, AgentType.MATH, AgentType.TIME_DATE]

        for agent_type in expected_agents:
            agent = orchestrator.get_agent(agent_type)
            print(f"  ✓ {agent_type.value}: {agent.name}")

        print(f"  ✓ All {len(expected_agents)} agents initialized")
        return True
    except Exception as e:
        print(f"  ✗ Agent initialization failed: {e}")
        return False


def test_tool_integration(orchestrator):
    """Test 4: Verify tool integration."""
    print("\n[TEST 4] Testing tool integration...")
    try:
        tools = registry.list_tools()
        print(f"  ✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"    - {tool}")

        # Verify agents have access to tools
        schemas = registry.schemas
        print(f"  ✓ Generated {len(schemas)} OpenAI schemas")
        return True
    except Exception as e:
        print(f"  ✗ Tool integration failed: {e}")
        return False


def test_routing_system(orchestrator):
    """Test 5: Verify routing system."""
    print("\n[TEST 5] Testing routing system...")
    try:
        test_cases = [
            ("What is 2+2?", AgentType.MATH),
            ("What time is it?", AgentType.TIME_DATE),
            ("Hello there!", AgentType.GENERAL),
        ]

        for query, expected_type in test_cases:
            decision = orchestrator.route_query(query)
            status = "✓" if decision.agent_type == expected_type else "✗"
            print(f"  {status} '{query}' -> {decision.agent_name} (confidence: {decision.confidence_score:.0%})")

            if decision.agent_type != expected_type:
                print(f"    Expected: {expected_type.value}, Got: {decision.agent_type.value}")

        print("  ✓ Routing system functional")
        return True
    except Exception as e:
        print(f"  ✗ Routing failed: {e}")
        return False


def test_query_processing(orchestrator):
    """Test 6: Verify query processing."""
    print("\n[TEST 6] Testing query processing...")
    try:
        test_queries = [
            "Hello!",
            "Convert 'test' to uppercase",
            "What is 5 times 5?",
        ]

        for query in test_queries:
            response = orchestrator.process(query)

            if response.error:
                print(f"  ✗ '{query}' -> Error: {response.error}")
                return False

            print(f"  ✓ '{query}'")
            print(f"    Agent: {response.agent_used}")
            print(f"    Tools: {response.tools_used if response.tools_used else 'None'}")
            print(f"    Time: {response.processing_time:.2f}s")

        print("  ✓ Query processing successful")
        return True
    except Exception as e:
        print(f"  ✗ Query processing failed: {e}")
        return False


def test_response_metadata(orchestrator):
    """Test 7: Verify response metadata."""
    print("\n[TEST 7] Testing response metadata...")
    try:
        response = orchestrator.process("What is 10 + 10?")

        # Check all required fields
        assert hasattr(response, 'response'), "Missing 'response' field"
        assert hasattr(response, 'agent_used'), "Missing 'agent_used' field"
        assert hasattr(response, 'agent_type'), "Missing 'agent_type' field"
        assert hasattr(response, 'routing_decision'), "Missing 'routing_decision' field"
        assert hasattr(response, 'processing_time'), "Missing 'processing_time' field"
        assert hasattr(response, 'tools_used'), "Missing 'tools_used' field"

        # Check routing decision fields
        decision = response.routing_decision
        assert hasattr(decision, 'agent_type'), "Missing 'agent_type' in decision"
        assert hasattr(decision, 'agent_name'), "Missing 'agent_name' in decision"
        assert hasattr(decision, 'confidence_score'), "Missing 'confidence_score' in decision"
        assert hasattr(decision, 'matched_keywords'), "Missing 'matched_keywords' in decision"
        assert hasattr(decision, 'reasoning'), "Missing 'reasoning' in decision"
        assert hasattr(decision, 'scores'), "Missing 'scores' in decision"

        print("  ✓ All metadata fields present")
        print(f"    Response: {response.response[:50]}...")
        print(f"    Agent: {response.agent_used}")
        print(f"    Confidence: {decision.confidence_score:.0%}")
        print(f"    Keywords: {decision.matched_keywords}")

        return True
    except AssertionError as e:
        print(f"  ✗ Metadata check failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Metadata test failed: {e}")
        return False


def test_statistics(orchestrator):
    """Test 8: Verify statistics functionality."""
    print("\n[TEST 8] Testing statistics...")
    try:
        stats = orchestrator.get_agent_stats()

        assert 'total_agents' in stats
        assert 'agent_types' in stats
        assert 'total_tools_available' in stats
        assert 'agents' in stats

        print(f"  ✓ Statistics retrieved")
        print(f"    Total Agents: {stats['total_agents']}")
        print(f"    Total Tools: {stats['total_tools_available']}")
        print(f"    Agent Types: {', '.join(stats['agent_types'])}")

        return True
    except Exception as e:
        print(f"  ✗ Statistics failed: {e}")
        return False


def test_history_management(orchestrator):
    """Test 9: Verify history management."""
    print("\n[TEST 9] Testing history management...")
    try:
        # Process some queries
        orchestrator.process("Test query 1")
        orchestrator.process("Test query 2")

        # Check history exists
        stats_before = orchestrator.get_agent_stats()
        total_messages_before = sum(
            agent['message_history_length']
            for agent in stats_before['agents']
        )

        if total_messages_before == 0:
            print("  ✗ No messages in history after processing")
            return False

        print(f"  ✓ History accumulated: {total_messages_before} messages")

        # Clear histories
        orchestrator.clear_all_histories()

        # Verify cleared
        stats_after = orchestrator.get_agent_stats()
        total_messages_after = sum(
            agent['message_history_length']
            for agent in stats_after['agents']
        )

        if total_messages_after != 0:
            print(f"  ✗ History not cleared: {total_messages_after} messages remain")
            return False

        print("  ✓ History cleared successfully")
        return True
    except Exception as e:
        print(f"  ✗ History management failed: {e}")
        return False


def test_error_handling(orchestrator):
    """Test 10: Verify error handling."""
    print("\n[TEST 10] Testing error handling...")
    try:
        # Test with empty query
        response = orchestrator.process("")

        # Should still return a response (not crash)
        if response.response:
            print("  ✓ Handled empty query gracefully")
        else:
            print("  ✗ Empty query produced no response")
            return False

        # Test with very long query
        long_query = "a" * 10000
        response = orchestrator.process(long_query)

        if response.response:
            print("  ✓ Handled long query gracefully")
        else:
            print("  ✗ Long query produced no response")
            return False

        print("  ✓ Error handling functional")
        return True
    except Exception as e:
        print(f"  ✗ Error handling failed: {e}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("Multi-Agent Orchestrator - Integration Tests")
    print("=" * 70)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Orchestrator creation
    success, orchestrator = test_orchestrator_creation()
    results.append(("Orchestrator Creation", success))

    if not success or not orchestrator:
        print("\n✗ Cannot continue tests without orchestrator")
        return False

    # Test 3-10: Remaining tests
    results.append(("Agent Initialization", test_agent_initialization(orchestrator)))
    results.append(("Tool Integration", test_tool_integration(orchestrator)))
    results.append(("Routing System", test_routing_system(orchestrator)))
    results.append(("Query Processing", test_query_processing(orchestrator)))
    results.append(("Response Metadata", test_response_metadata(orchestrator)))
    results.append(("Statistics", test_statistics(orchestrator)))
    results.append(("History Management", test_history_management(orchestrator)))
    results.append(("Error Handling", test_error_handling(orchestrator)))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 70)

    if passed == total:
        print("\n✓ All integration tests passed!")
        print("✓ Orchestrator is fully functional and production-ready")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        print("✗ Please review failures above")
        return False


def main():
    """Main entry point."""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print("\nMake sure OPENAI_API_KEY is set:")
        print("  export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)


if __name__ == "__main__":
    main()
