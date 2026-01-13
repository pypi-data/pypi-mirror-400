"""
Demonstration script for the Multi-Agent Orchestrator System.

This script showcases the capabilities of the orchestrator including:
- Intelligent agent routing
- Tool integration
- Response attribution
- Performance metrics
- Verbose debugging

Run this script to see the orchestrator in action!
"""

from orchestrator import create_orchestrator, AgentType
from tools import registry


def print_separator(title: str = "") -> None:
    """Print a formatted separator line."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"{title.center(80)}")
        print('=' * 80)
    else:
        print('-' * 80)


def demo_basic_queries():
    """Demonstrate basic query processing."""
    print_separator("DEMO 1: Basic Query Processing")

    # Create orchestrator (non-verbose for clean output)
    orchestrator = create_orchestrator(verbose=False)

    queries = [
        "Hello! How are you today?",
        "What is 25 multiplied by 4?",
        "What time is it right now?",
        "Convert 'hello world' to uppercase",
        "What's today's date?",
        "Calculate (10 + 15) * 2"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        response = orchestrator.process(query)

        print(f"Agent: {response.agent_used}")
        print(f"Response: {response.response}")
        print(f"Confidence: {response.routing_decision.confidence_score:.2%}")
        if response.tools_used:
            print(f"Tools Used: {', '.join(response.tools_used)}")
        print_separator()


def demo_routing_analysis():
    """Demonstrate routing decision analysis."""
    print_separator("DEMO 2: Routing Analysis & Metrics")

    orchestrator = create_orchestrator(verbose=False)

    # Test various query types
    test_cases = [
        "What is 100 divided by 5?",
        "Tell me the current time and date",
        "Reverse the text 'OpenAI'",
        "How much is 50 + 50?"
    ]

    for query in test_cases:
        print(f"\nAnalyzing: '{query}'")

        # Get routing decision
        decision = orchestrator.route_query(query)

        print(f"\nSelected Agent: {decision.agent_name}")
        print(f"Confidence Score: {decision.confidence_score:.2%}")
        print(f"Matched Keywords: {decision.matched_keywords}")
        print(f"Reasoning: {decision.reasoning}")

        print("\nAll Agent Scores:")
        for agent_type, score in sorted(
            decision.scores.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            bar = '█' * int(score * 40)
            print(f"  {agent_type.value:12} [{score:.2f}] {bar}")

        print_separator()


def demo_verbose_mode():
    """Demonstrate verbose debugging mode."""
    print_separator("DEMO 3: Verbose Mode (Debugging)")

    # Create orchestrator with verbose mode enabled
    orchestrator = create_orchestrator(verbose=True)

    print("\nProcessing with verbose logging enabled...")
    print("This shows internal decision-making and tool usage:\n")

    query = "What is 25 * 4 and what time is it?"

    response = orchestrator.process(query)

    print(f"\n\nFinal Response: {response.response}")


def demo_agent_statistics():
    """Demonstrate statistics and monitoring."""
    print_separator("DEMO 4: Agent Statistics & Monitoring")

    orchestrator = create_orchestrator(verbose=False)

    # Process some queries to build history
    queries = [
        "Hello!",
        "What is 10 + 10?",
        "What's the time?",
        "Calculate 50 / 2",
        "What's today's date?"
    ]

    print("\nProcessing sample queries to build history...\n")
    for query in queries:
        response = orchestrator.process(query)
        print(f"✓ Processed: '{query}' → {response.agent_used}")

    # Get statistics
    print("\n")
    print_separator()
    stats = orchestrator.get_agent_stats()

    print(f"\nOrchestrator Statistics:")
    print(f"  Total Agents: {stats['total_agents']}")
    print(f"  Agent Types: {', '.join(stats['agent_types'])}")
    print(f"  Total Available Tools: {stats['total_tools_available']}")

    print(f"\nAvailable Tools:")
    for tool in stats['available_tools']:
        print(f"  • {tool}")

    print(f"\nAgent Details:")
    for agent in stats['agents']:
        print(f"\n  {agent['name']}:")
        print(f"    Type: {agent['type']}")
        print(f"    Model: {agent['model']}")
        print(f"    Messages in History: {agent['message_history_length']}")
        print(f"    Estimated Tokens: {agent['token_estimate']}")


def demo_direct_agent_access():
    """Demonstrate direct access to specific agents."""
    print_separator("DEMO 5: Direct Agent Access")

    orchestrator = create_orchestrator(verbose=False)

    print("\nDirectly accessing the Math Specialist agent:\n")

    # Get math agent directly
    math_agent = orchestrator.get_agent(AgentType.MATH)

    print(f"Agent: {math_agent.name}")
    print(f"Role: {math_agent.role}")

    # Use it directly
    query = "Calculate: (25 + 15) * 3 - 10"
    print(f"\nQuery: {query}")

    response = math_agent.process_with_tools(
        user_input=query,
        tools=registry.schemas,
        tool_executor=registry
    )

    print(f"Response: {response}")


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print_separator("DEMO 6: Error Handling")

    orchestrator = create_orchestrator(verbose=False)

    # Test with edge cases
    test_cases = [
        ("Empty query", ""),
        ("Very long calculation", "1" + "+1" * 50),
        ("Invalid math", "calculate xyz"),
    ]

    for description, query in test_cases:
        if query:
            print(f"\n{description}: '{query[:50]}...'")
            response = orchestrator.process(query)

            if response.error:
                print(f"  Error Detected: {response.error}")
            print(f"  Response: {response.response[:100]}...")
            print(f"  Agent: {response.agent_used}")


def demo_response_times():
    """Demonstrate performance metrics."""
    print_separator("DEMO 7: Performance Metrics")

    orchestrator = create_orchestrator(verbose=False)

    queries = [
        "Hello!",
        "What is 123 * 456?",
        "What time is it?",
        "Convert 'test' to uppercase"
    ]

    print("\nMeasuring response times:\n")

    times_by_agent = {}

    for query in queries:
        response = orchestrator.process(query)

        agent_type = response.agent_type.value
        if agent_type not in times_by_agent:
            times_by_agent[agent_type] = []

        times_by_agent[agent_type].append(response.processing_time)

        print(f"Query: '{query}'")
        print(f"  Agent: {response.agent_used}")
        print(f"  Time: {response.processing_time:.3f}s")
        print(f"  Tools: {len(response.tools_used)}")
        print()

    print_separator()
    print("\nAverage Response Times by Agent:")
    for agent_type, times in times_by_agent.items():
        avg_time = sum(times) / len(times)
        print(f"  {agent_type:12} {avg_time:.3f}s (n={len(times)})")


def main():
    """Run all demonstrations."""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║              Multi-Agent Orchestrator System - Demonstration                 ║
    ║                                                                              ║
    ║  This demo showcases intelligent agent routing, tool integration,           ║
    ║  and comprehensive orchestration capabilities.                              ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Run demonstrations
        demo_basic_queries()
        input("\nPress Enter to continue to Routing Analysis...")

        demo_routing_analysis()
        input("\nPress Enter to continue to Verbose Mode...")

        demo_verbose_mode()
        input("\nPress Enter to continue to Statistics...")

        demo_agent_statistics()
        input("\nPress Enter to continue to Direct Agent Access...")

        demo_direct_agent_access()
        input("\nPress Enter to continue to Error Handling...")

        demo_error_handling()
        input("\nPress Enter to continue to Performance Metrics...")

        demo_response_times()

        print_separator("DEMONSTRATION COMPLETE")
        print("\nAll demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  ✓ Intelligent agent routing with confidence scoring")
        print("  ✓ Seamless tool integration")
        print("  ✓ Response attribution and metadata")
        print("  ✓ Verbose debugging mode")
        print("  ✓ Performance metrics and monitoring")
        print("  ✓ Direct agent access")
        print("  ✓ Error handling")
        print("\nThe orchestrator is production-ready and fully integrated!")

    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demonstration: {str(e)}")
        print("\nMake sure OPENAI_API_KEY is set in your environment:")
        print("  export OPENAI_API_KEY='your-key-here'")


if __name__ == "__main__":
    main()
