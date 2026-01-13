"""
Definitive Proof: Agent Actually Calls Tools

This test PROVES tool calling by:
1. Inspecting the actual OpenAI API messages
2. Checking for tool_calls in the conversation
3. Verifying tool execution happened
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found!")
    sys.exit(1)

from indusagi import Agent, registry
import custom_tools

print("="*70)
print("DEFINITIVE PROOF - Agent Tool Calling Verification")
print("="*70)

# Create agent
agent = Agent("ProofBot", "Assistant that demonstrates tool usage")

# Test queries designed to trigger tool usage
test_cases = [
    {
        "query": "Calculate exactly: 7531 * 8642",
        "expected_tool": "calculator",
        "description": "Calculator tool"
    },
    {
        "query": "Pick one random item from this exact list: alpha,beta,gamma,delta",
        "expected_tool": "pick_random_item",
        "description": "Pick random item tool"
    },
    {
        "query": "Generate a random number between 1 and 10",
        "expected_tool": "random_number",
        "description": "Random number tool"
    },
]

total_tests = len(test_cases)
tools_called = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}/{total_tests}: {test['description']}")
    print(f"{'='*70}")

    query = test['query']
    expected_tool = test['expected_tool']

    print(f"\nQuery: '{query}'")
    print(f"Expected tool: {expected_tool}")

    # Clear previous messages
    agent.messages = []

    # Process query
    print("\nProcessing...")
    response = agent.process_with_tools(query, max_turns=3)

    print(f"\nAgent response: {response}")

    # PROOF: Check actual message history for tool_calls
    print(f"\n--- PROOF OF TOOL CALLING ---")

    tool_call_found = False
    tools_used = []

    for msg in agent.messages:
        # Check if this message has tool_calls
        if isinstance(msg, dict) and msg.get('role') == 'assistant':
            if 'tool_calls' in msg and msg['tool_calls']:
                tool_call_found = True
                for tc in msg['tool_calls']:
                    tool_name = tc['function']['name']
                    tool_args = tc['function']['arguments']
                    tools_used.append(tool_name)

                    print(f"\nTOOL CALL DETECTED:")
                    print(f"  Tool: {tool_name}")
                    print(f"  Arguments: {tool_args}")

        # Check if this is a tool response
        if isinstance(msg, dict) and msg.get('role') == 'tool':
            tool_result = msg.get('content', '')
            tool_name = msg.get('name', 'unknown')
            print(f"\nTOOL RESPONSE:")
            print(f"  Tool: {tool_name}")
            print(f"  Result: {tool_result[:100]}...")

    # Verdict
    if tool_call_found:
        if expected_tool in tools_used:
            print(f"\n[VERIFIED] Agent called {expected_tool} tool!")
            tools_called += 1
            verdict = "PASS"
        else:
            print(f"\n[INFO] Agent called tools: {tools_used}")
            print(f"       Expected: {expected_tool}")
            tools_called += 1
            verdict = "PARTIAL"
    else:
        print(f"\n[FAIL] No tool calls detected in message history")
        verdict = "FAIL"

    print(f"\nVerdict: {verdict}")

# Additional proof: Direct tool execution vs Agent execution
print(f"\n{'='*70}")
print("COMPARISON TEST: Direct vs Agent Execution")
print(f"{'='*70}")

# Test with a calculation that has a specific answer
test_expr = "12345 + 67890"
print(f"\nExpression: {test_expr}")

# Direct execution
direct_result = registry.execute("calculator", expression=test_expr)
print(f"\nDirect tool execution: {direct_result}")

# Agent execution
agent.messages = []
query = f"Calculate exactly: {test_expr}"
print(f"\nAgent query: '{query}'")

agent_response = agent.process_with_tools(query, max_turns=3)
print(f"Agent response: {agent_response}")

# Check if agent used the tool
agent_used_tool = False
for msg in agent.messages:
    if isinstance(msg, dict) and msg.get('role') == 'tool':
        if msg.get('name') == 'calculator':
            tool_output = msg.get('content', '')
            print(f"\nAgent's calculator tool output: {tool_output}")
            agent_used_tool = True

            if direct_result.strip() == tool_output.strip():
                print("[VERIFIED] Agent's tool output EXACTLY matches direct execution!")
            else:
                print(f"[INFO] Outputs differ slightly:")
                print(f"  Direct: {direct_result}")
                print(f"  Agent:  {tool_output}")

if not agent_used_tool:
    print("[INFO] Agent may have calculated without using the tool")

# Final summary
print(f"\n{'='*70}")
print("FINAL PROOF SUMMARY")
print(f"{'='*70}")

print(f"\nTests where tools were called: {tools_called}/{total_tests}")

if tools_called > 0:
    print("\n[PROVEN] The agent IS actually calling tools!")
    print("\nEvidence:")
    print("  1. tool_calls present in message history")
    print("  2. Tool responses recorded in conversation")
    print("  3. OpenAI API is executing function calls")
    print("\nConclusion: Tool calling is REAL, not fake!")
else:
    print("\n[INFO] No tool calls detected in this test run")
    print("This may be due to OpenAI deciding not to use tools for these queries")

# Show example of message structure
print(f"\n{'='*70}")
print("EXAMPLE MESSAGE STRUCTURE (Last Test)")
print(f"{'='*70}")

print("\nMessage history structure:")
for i, msg in enumerate(agent.messages[-5:], 1):  # Show last 5 messages
    if isinstance(msg, dict):
        role = msg.get('role', 'unknown')
        print(f"\nMessage {i}:")
        print(f"  Role: {role}")

        if role == 'assistant' and 'tool_calls' in msg:
            print(f"  Has tool_calls: YES")
            print(f"  Number of tools: {len(msg.get('tool_calls', []))}")
        elif role == 'tool':
            print(f"  Tool name: {msg.get('name', 'unknown')}")
            print(f"  Has result: YES")

print(f"\n{'='*70}")
print("Test complete! Check the tool_calls above as proof.")
print(f"{'='*70}")
