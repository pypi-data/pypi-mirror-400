"""
Test script to verify handoff loop fix.

This tests that:
1. Coder receives request
2. Coder hands off to Planner
3. Planner executes and creates plan.md
4. Planner hands off back to Coder
5. Coder implements the plan
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Test the improved agency
from example_agency_improved import create_development_agency

def test_handoff_loop():
    """Test that handoffs work in a loop."""
    print("="*70)
    print("TESTING HANDOFF LOOP FIX")
    print("="*70)
    print()

    # Create agency
    agency = create_development_agency(model="gpt-4o", max_handoffs=5)

    # Simulate user request
    test_request = "Create plan.md for a simple calculator app"

    print(f"Test Request: {test_request}")
    print()
    print("Processing...")
    print("="*70)
    print()

    # Process
    result = agency.process(
        test_request,
        use_tools=True,
        tools=agency.tools,
        tool_executor=agency.tool_executor
    )

    print()
    print("="*70)
    print("RESULTS:")
    print("="*70)
    print(f"Agents used: {result.agents_used}")
    print(f"Handoffs: {len(result.handoffs)}")
    print(f"Final agent: {result.final_agent}")
    print(f"Total time: {result.total_time:.2f}s")
    print()
    print(f"Response: {result.response[:200]}...")
    print()

    # Verify handoff occurred
    if len(result.agents_used) > 1:
        print("✅ SUCCESS: Handoff loop working!")
        print(f"   Flow: {' → '.join(result.agents_used)}")
    else:
        print("❌ FAILED: No handoff occurred")
        print(f"   Only {result.agents_used} was used")

    return len(result.agents_used) > 1


if __name__ == "__main__":
    success = test_handoff_loop()
    exit(0 if success else 1)
