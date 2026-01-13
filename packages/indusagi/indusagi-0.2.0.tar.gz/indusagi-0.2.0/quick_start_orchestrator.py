"""
Quick Start Example for Multi-Agent Orchestrator

This script demonstrates the simplest way to get started with the orchestrator.
Run this file to see the system in action with minimal setup.

Usage:
    python quick_start_orchestrator.py
"""

from orchestrator import create_orchestrator


def main():
    """Quick demonstration of orchestrator capabilities."""

    print("=" * 70)
    print("Multi-Agent Orchestrator - Quick Start")
    print("=" * 70)

    # Step 1: Create orchestrator (one line!)
    print("\n[1] Creating orchestrator...")
    orchestrator = create_orchestrator(verbose=False)
    print(f"    Created: {orchestrator}")

    # Step 2: Process different types of queries
    print("\n[2] Processing queries...")

    queries = [
        # General queries → General Agent
        ("Hello! How are you?", "General conversation"),

        # Math queries → Math Agent
        ("What is 25 * 4?", "Math calculation"),
        ("Calculate 100 / 5", "Math operation"),

        # Time/Date queries → Time/Date Agent
        ("What time is it?", "Time query"),
        ("What's today's date?", "Date query"),

        # Text manipulation → General Agent (with tools)
        ("Convert 'python' to uppercase", "Text manipulation"),
    ]

    print()
    for query, description in queries:
        print(f"    {description}:")
        print(f"      Query: \"{query}\"")

        # Process the query
        response = orchestrator.process(query)

        # Display results
        print(f"      Agent: {response.agent_used}")
        print(f"      Response: {response.response}")
        print(f"      Confidence: {response.routing_decision.confidence_score:.0%}")

        if response.tools_used:
            print(f"      Tools: {', '.join(response.tools_used)}")

        print()

    # Step 3: View statistics
    print("\n[3] Orchestrator Statistics:")
    stats = orchestrator.get_agent_stats()

    print(f"    Total Agents: {stats['total_agents']}")
    print(f"    Available Tools: {stats['total_tools_available']}")

    print("\n    Agents:")
    for agent in stats['agents']:
        print(f"      - {agent['name']} ({agent['type']})")
        print(f"        Model: {agent['model']}")
        print(f"        Messages: {agent['message_history_length']}")

    # Step 4: Advanced usage example
    print("\n[4] Advanced Usage - Routing Analysis:")

    test_query = "Calculate 50 + 50"
    decision = orchestrator.route_query(test_query)

    print(f"    Query: \"{test_query}\"")
    print(f"    Selected Agent: {decision.agent_name}")
    print(f"    Confidence: {decision.confidence_score:.2%}")
    print(f"    Matched Keywords: {decision.matched_keywords}")
    print(f"    Reasoning: {decision.reasoning}")

    print("\n    Score Breakdown:")
    for agent_type, score in sorted(
        decision.scores.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        bar = '█' * int(score * 30)
        print(f"      {agent_type.value:12} [{score:.2f}] {bar}")

    print("\n" + "=" * 70)
    print("Quick Start Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  • create_orchestrator() - One line to set up everything")
    print("  • orchestrator.process(query) - Process any query")
    print("  • Automatic routing to specialized agents")
    print("  • Seamless tool integration")
    print("  • Rich metadata and metrics")
    print("\nNext Steps:")
    print("  • Run 'python demo_orchestrator.py' for full demo")
    print("  • Read ORCHESTRATOR_GUIDE.md for complete documentation")
    print("  • Enable verbose mode: create_orchestrator(verbose=True)")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nMake sure OPENAI_API_KEY is set:")
        print("  export OPENAI_API_KEY='your-key-here'")
