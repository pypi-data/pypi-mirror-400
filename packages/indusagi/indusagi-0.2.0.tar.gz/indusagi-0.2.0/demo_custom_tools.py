"""
Demo: Using Custom Tools with Agent

This script demonstrates how to:
1. Import custom tools (which auto-registers them)
2. Verify custom tools are in the registry
3. Use custom tools with the autonomous agent
4. Test multiple custom tool queries

The agent will autonomously decide which custom tools to use!
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("\n" + "="*70)
    print("ERROR: OPENAI_API_KEY not found!")
    print("="*70)
    print("\nPlease set your API key in .env file")
    print("="*70)
    sys.exit(1)

from indusagi import Agent, registry

# ============================================================================
# STEP 1: Import custom tools (this auto-registers them!)
# ============================================================================

print("\n" + "="*70)
print("STEP 1: LOADING CUSTOM TOOLS")
print("="*70)

print("\nBefore importing custom_tools.py:")
print(f"  Total tools in registry: {len(registry.list_tools())}")

# Import custom tools - this automatically registers them!
import custom_tools

print("\nAfter importing custom_tools.py:")
all_tools = registry.list_tools()
print(f"  Total tools in registry: {len(all_tools)}")

# ============================================================================
# STEP 2: Verify custom tools are registered
# ============================================================================

print("\n" + "="*70)
print("STEP 2: VERIFYING CUSTOM TOOLS")
print("="*70)

# Built-in tools (original 9)
builtin_tools = [
    "calculator", "get_time", "get_date", "get_datetime",
    "text_uppercase", "text_lowercase", "text_reverse",
    "text_count_words", "text_title_case"
]

# Custom tools (the 8 we just added)
custom_tool_names = [
    "get_weather", "create_file", "read_file", "random_number",
    "generate_password", "text_stats", "date_calculator",
    "pick_random_item", "build_search_url"
]

print("\nBuilt-in tools (9 original):")
for tool in builtin_tools:
    status = "OK" if tool in all_tools else "MISSING"
    print(f"  [{status}] {tool}")

print("\nCustom tools (8 new):")
for tool in custom_tool_names:
    status = "OK" if tool in all_tools else "MISSING"
    print(f"  [{status}] {tool}")

# ============================================================================
# STEP 3: Test custom tools directly
# ============================================================================

print("\n" + "="*70)
print("STEP 3: TESTING CUSTOM TOOLS DIRECTLY")
print("="*70)

print("\nTest 1: get_weather")
result = registry.execute("get_weather", city="London", unit="celsius")
print(f"  Result: {result}")

print("\nTest 2: random_number")
result = registry.execute("random_number", min_value=1, max_value=10)
print(f"  Result: {result}")

print("\nTest 3: date_calculator")
result = registry.execute("date_calculator", days_from_now=7)
print(f"  Result: {result}")

print("\nTest 4: text_stats")
result = registry.execute("text_stats", text="Hello World! This is a test.")
print(f"  Result: {result}")

# ============================================================================
# STEP 4: Create agent and test with custom tool queries
# ============================================================================

print("\n" + "="*70)
print("STEP 4: TESTING CUSTOM TOOLS WITH AGENT")
print("="*70)

# Create agent
agent = Agent(
    name="CustomToolAgent",
    role="Assistant that uses both built-in and custom tools"
)

# Test queries that will use custom tools
test_queries = [
    {
        "query": "What's the weather in Paris and what time is it now?",
        "expected_tools": ["get_weather", "get_time"]
    },
    {
        "query": "Generate a random number between 1 and 100 and also calculate 50 * 2",
        "expected_tools": ["random_number", "calculator"]
    },
    {
        "query": "What will the date be 30 days from now?",
        "expected_tools": ["date_calculator"]
    },
    {
        "query": "Get statistics for the text 'Custom tools are awesome!'",
        "expected_tools": ["text_stats"]
    },
    {
        "query": "Pick a random item from this list: apple,banana,orange,grape",
        "expected_tools": ["pick_random_item"]
    }
]

print("\nRunning 5 test queries with custom tools...")
print("(Agent will autonomously decide which tools to use)\n")

for i, test in enumerate(test_queries, 1):
    print("\n" + "-"*70)
    print(f"TEST QUERY {i}/{len(test_queries)}")
    print("-"*70)
    print(f"Query: {test['query']}")
    print(f"Expected tools: {', '.join(test['expected_tools'])}")
    print("\nAgent processing...\n")

    try:
        # Let agent process the query
        response = agent.process_with_tools(test['query'], max_turns=3)
        print(f"Agent Response:\n{response}")
        print("\n[OK] Query processed successfully!")

    except Exception as e:
        print(f"\n[ERROR] Query failed: {str(e)}")

# ============================================================================
# STEP 5: Interactive mode with custom tools
# ============================================================================

print("\n" + "="*70)
print("STEP 5: INTERACTIVE MODE (OPTIONAL)")
print("="*70)

print("\nYou can now test custom tools interactively!")
print("\nExample queries you can try:")
print("  - 'What's the weather in Tokyo?'")
print("  - 'Generate a random number between 1 and 50'")
print("  - 'What will the date be 15 days from now?'")
print("  - 'Generate a password of length 16'")
print("  - 'Pick a random item from: red,blue,green,yellow'")
print("  - 'Build a Google search URL for artificial intelligence'")
print("  - 'Get statistics for the word Hello'")
print("\nType 'skip' to skip interactive mode")
print("Type 'quit' to exit interactive mode")

# Try interactive mode, skip if not available
try:
    user_input = input("\nEnter your query (or 'skip'): ").strip()

    if user_input.lower() != 'skip':
        while user_input.lower() != 'quit':
            if user_input:
                print("\nAgent processing...\n")
                try:
                    response = agent.process_with_tools(user_input, max_turns=3)
                    print(f"\nAgent: {response}\n")
                except Exception as e:
                    print(f"\nError: {str(e)}\n")

            user_input = input("Enter your query (or 'quit'): ").strip()
except (EOFError, KeyboardInterrupt):
    print("\nSkipping interactive mode")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*70)
print("DEMO COMPLETE - CUSTOM TOOLS WORKING!")
print("="*70)

print("\nSummary:")
print(f"  Built-in tools: {len(builtin_tools)}")
print(f"  Custom tools: {len(custom_tool_names)}")
print(f"  Total tools available: {len(all_tools)}")

print("\nKey Takeaways:")
print("  1. Custom tools are registered simply by importing them")
print("  2. Agent automatically discovers and uses custom tools")
print("  3. Custom tools work exactly like built-in tools")
print("  4. No code changes needed to agent.py!")

print("\n" + "="*70)
print("You can now create your own custom tools!")
print("See: HOW_TO_CREATE_CUSTOM_TOOLS.md for detailed guide")
print("="*70)
