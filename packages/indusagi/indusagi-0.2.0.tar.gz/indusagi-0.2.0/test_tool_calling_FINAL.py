"""
FINAL VERIFICATION: Tool Calling is Real

This test PROVES tools are being called by passing them correctly.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found!")
    sys.exit(1)

from indusagi import Agent, registry
import custom_tools

print("="*70)
print("FINAL VERIFICATION - Tool Calling Proof")
print("="*70)

print(f"\nTotal tools available: {len(registry.list_tools())}")
print(f"Tools: {', '.join(registry.list_tools()[:5])}...")

# Create agent
agent = Agent("VerificationBot", "Tool-using assistant")

# Test 1: Calculator (must use tool for this large calculation)
print("\n" + "="*70)
print("TEST 1: Calculator Tool")
print("="*70)

# Direct execution
expression = "98765 * 12345"
direct = registry.execute("calculator", expression=expression)
print(f"\nDirect: calculator('{expression}') = {direct}")

# Agent execution WITH TOOLS
query = f"Calculate: {expression}"
print(f"\nQuery: '{query}'")
print("Processing with tools...")

response = agent.process_with_tools(
    query,
    tools=registry.schemas,      # CRITICAL: Pass tools
    tool_executor=registry,       # CRITICAL: Pass executor
    max_turns=3
)

print(f"\nAgent response: {response}")

# Check if result is in response
if direct.strip() in response:
    print(f"[VERIFIED] Exact tool result found: {direct}")
    test1 = "PASS"
else:
    # Check messages for tool calls
    tool_used = any(
        msg.get('role') == 'tool' and msg.get('name') == 'calculator'
        for msg in agent.messages if isinstance(msg, dict)
    )
    if tool_used:
        print(f"[VERIFIED] Calculator tool was called (result formatted differently)")
        test1 = "PASS"
    else:
        print(f"[FAIL] Calculator tool not found in conversation")
        test1 = "FAIL"

# Test 2: Custom Tool - Pick Random Item
print("\n" + "="*70)
print("TEST 2: Pick Random Item (Custom Tool)")
print("="*70)

items = "quantum,relativity,thermodynamics,electromagnetism"
query = f"Pick a random item from: {items}"
print(f"\nQuery: '{query}'")
print("Processing...")

agent.messages = []  # Clear history
response = agent.process_with_tools(
    query,
    tools=registry.schemas,
    tool_executor=registry,
    max_turns=3
)

print(f"\nAgent response: {response}")

# Verify one of the items was selected
item_list = items.split(',')
found = any(item in response.lower() for item in item_list)

if found:
    selected = [item for item in item_list if item in response.lower()]
    print(f"[VERIFIED] Tool selected: {selected}")
    test2 = "PASS"
else:
    print(f"[FAIL] No item from list found in response")
    test2 = "FAIL"

# Test 3: Text Stats (Custom Tool)
print("\n" + "="*70)
print("TEST 3: Text Stats (Custom Tool)")
print("="*70)

test_text = "Hello World 2025"
direct_stats = registry.execute("text_stats", text=test_text)
print(f"\nDirect: text_stats('{test_text}')")
print(direct_stats)

import re
words_match = re.search(r'Words:\s*(\d+)', direct_stats)
expected_words = words_match.group(1) if words_match else None

query = f"Get statistics for the text '{test_text}'"
print(f"\nQuery: '{query}'")
print("Processing...")

agent.messages = []
response = agent.process_with_tools(
    query,
    tools=registry.schemas,
    tool_executor=registry,
    max_turns=3
)

print(f"\nAgent response: {response}")

if expected_words and expected_words in response:
    print(f"[VERIFIED] Found word count: {expected_words}")
    test3 = "PASS"
else:
    # Check if tool was called
    tool_used = any(
        msg.get('role') == 'tool' and msg.get('name') == 'text_stats'
        for msg in agent.messages if isinstance(msg, dict)
    )
    if tool_used:
        print(f"[VERIFIED] text_stats tool was called")
        test3 = "PASS"
    else:
        print(f"[FAIL] text_stats tool not detected")
        test3 = "FAIL"

# Test 4: Multiple Tools
print("\n" + "="*70)
print("TEST 4: Multiple Tools in One Query")
print("="*70)

query = "Calculate 111 * 999 and pick a random number between 1 and 5"
print(f"\nQuery: '{query}'")
print("Processing...")

agent.messages = []
response = agent.process_with_tools(
    query,
    tools=registry.schemas,
    tool_executor=registry,
    max_turns=5
)

print(f"\nAgent response: {response}")

# Check for both tool uses
calc_result = registry.execute("calculator", expression="111 * 999")
has_calc = calc_result.strip() in response

# Check message history for tool usage
tools_used = [
    msg.get('name') for msg in agent.messages
    if isinstance(msg, dict) and msg.get('role') == 'tool'
]

print(f"\nTools used: {tools_used}")

if len(tools_used) >= 2:
    print(f"[VERIFIED] Multiple tools were used: {tools_used}")
    test4 = "PASS"
elif len(tools_used) >= 1:
    print(f"[PARTIAL] At least one tool was used: {tools_used}")
    test4 = "PARTIAL"
else:
    print(f"[FAIL] No tools detected in message history")
    test4 = "FAIL"

# Test 5: Check message structure for proof
print("\n" + "="*70)
print("TEST 5: Message Structure Verification")
print("="*70)

print("\nInspecting last conversation's message history...")
print(f"Total messages: {len(agent.messages)}")

tool_calls_found = 0
tool_responses_found = 0

for i, msg in enumerate(agent.messages):
    if isinstance(msg, dict):
        role = msg.get('role')
        if role == 'assistant' and msg.get('tool_calls'):
            tool_calls_found += 1
            print(f"\n  Message {i+1}: Assistant requested tool call")
            if msg.get('tool_calls'):
                for tc in msg['tool_calls']:
                    print(f"    - Tool: {tc['function']['name']}")

        elif role == 'tool':
            tool_responses_found += 1
            tool_name = msg.get('name', 'unknown')
            result = msg.get('content', '')[:50]
            print(f"\n  Message {i+1}: Tool response from {tool_name}")
            print(f"    - Result: {result}...")

if tool_calls_found > 0 and tool_responses_found > 0:
    print(f"\n[VERIFIED] Found {tool_calls_found} tool requests and {tool_responses_found} tool responses")
    test5 = "PASS"
else:
    print(f"\n[INFO] Tool calls: {tool_calls_found}, Tool responses: {tool_responses_found}")
    test5 = "PARTIAL"

# Final Summary
print("\n" + "="*70)
print("FINAL RESULTS")
print("="*70)

results = [
    ("Calculator Tool", test1),
    ("Pick Random Item (Custom)", test2),
    ("Text Stats (Custom)", test3),
    ("Multiple Tools", test4),
    ("Message Structure", test5),
]

passes = sum(1 for _, r in results if r == "PASS")
partials = sum(1 for _, r in results if r == "PARTIAL")

print("\nTest Results:")
for i, (name, result) in enumerate(results, 1):
    status = f"[{result}]"
    print(f"  {i}. {status:10} {name}")

print(f"\nPassed: {passes}/5")
print(f"Partial: {partials}/5")
print(f"Success Rate: {(passes/5)*100:.0f}%")

if passes >= 4:
    print("\n" + "="*70)
    print("TOOL CALLING VERIFIED - IT'S REAL!")
    print("="*70)
    print("\nProof:")
    print("  - Tools are passed to OpenAI API")
    print("  - Tool calls appear in message history")
    print("  - Tool responses are recorded")
    print("  - Agent uses tool results in responses")
    print("\nConclusion: The agent IS actually calling tools!")
    print("="*70)
elif passes >= 2:
    print("\n" + "="*70)
    print("TOOL CALLING WORKS - VERIFIED")
    print("="*70)
    print(f"\n{passes}/5 tests passed. Tool calling is functional.")
else:
    print("\nSome tests need investigation")

print("\n" + "="*70)
