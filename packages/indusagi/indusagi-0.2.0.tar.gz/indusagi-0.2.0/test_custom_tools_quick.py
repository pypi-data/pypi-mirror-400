"""
Quick Test: Verify Custom Tools Work

This script tests that custom tools can be:
1. Registered
2. Discovered
3. Executed directly
4. Used by the agent

No OpenAI API calls required for basic tests!
"""

print("="*70)
print("QUICK TEST - Custom Tools Functionality")
print("="*70)

# Test 1: Import and registration
print("\n[Test 1/5] Importing custom tools...")
from indusagi import registry

before_count = len(registry.list_tools())
print(f"  Tools before import: {before_count}")

import custom_tools

after_count = len(registry.list_tools())
print(f"  Tools after import: {after_count}")
print(f"  New tools added: {after_count - before_count}")

if after_count > before_count:
    print("  [PASS] Custom tools imported successfully")
else:
    print("  [FAIL] No custom tools were added")
    exit(1)

# Test 2: Verify specific custom tools
print("\n[Test 2/5] Verifying custom tools exist...")
expected_custom_tools = [
    "get_weather", "create_file", "read_file", "random_number",
    "generate_password", "text_stats", "date_calculator",
    "pick_random_item", "build_search_url"
]

all_tools = registry.list_tools()
found_count = 0

for tool_name in expected_custom_tools:
    if tool_name in all_tools:
        found_count += 1

print(f"  Found {found_count}/{len(expected_custom_tools)} custom tools")

if found_count == len(expected_custom_tools):
    print("  [PASS] All custom tools registered")
else:
    missing = [t for t in expected_custom_tools if t not in all_tools]
    print(f"  [FAIL] Missing tools: {missing}")
    exit(1)

# Test 3: Execute custom tools directly
print("\n[Test 3/5] Testing custom tool execution...")
tests = [
    ("get_weather", {"city": "Tokyo", "unit": "celsius"}, "Weather in Tokyo"),
    ("random_number", {"min_value": 1, "max_value": 10}, "Random number between 1 and 10"),
    ("date_calculator", {"days_from_now": 7}, "7 days from now"),
    ("text_stats", {"text": "Hello World"}, "Text Statistics"),
    ("pick_random_item", {"items": "red,blue,green", "separator": ","}, "Randomly selected"),
    ("build_search_url", {"query": "AI", "search_engine": "google"}, "https://www.google.com"),
]

passed = 0
for tool_name, kwargs, expected_in_result in tests:
    try:
        result = registry.execute(tool_name, **kwargs)
        if expected_in_result in result:
            print(f"  [OK] {tool_name}: {result[:60]}...")
            passed += 1
        else:
            print(f"  [FAIL] {tool_name}: Unexpected result")
    except Exception as e:
        print(f"  [ERROR] {tool_name}: {str(e)}")

if passed == len(tests):
    print(f"  [PASS] All {len(tests)} custom tool tests passed")
else:
    print(f"  [FAIL] Only {passed}/{len(tests)} tests passed")
    exit(1)

# Test 4: Verify schemas are generated
print("\n[Test 4/5] Checking OpenAI schemas...")
schemas = registry.schemas

custom_tool_schemas = [s for s in schemas if s['function']['name'] in expected_custom_tools]
print(f"  Custom tool schemas: {len(custom_tool_schemas)}")

if len(custom_tool_schemas) == len(expected_custom_tools):
    print("  [PASS] All custom tools have schemas")
else:
    print(f"  [FAIL] Expected {len(expected_custom_tools)} schemas, got {len(custom_tool_schemas)}")
    exit(1)

# Test 5: Verify schema format
print("\n[Test 5/5] Verifying schema structure...")
sample_schema = custom_tool_schemas[0]

required_keys = ["type", "function"]
function_keys = ["name", "description", "parameters"]

schema_valid = True

if not all(key in sample_schema for key in required_keys):
    print(f"  [FAIL] Missing required keys in schema")
    schema_valid = False

if not all(key in sample_schema["function"] for key in function_keys):
    print(f"  [FAIL] Missing required keys in function schema")
    schema_valid = False

if schema_valid:
    print("  [PASS] Schema structure is valid")
    print(f"  Sample schema: {sample_schema['function']['name']}")
else:
    exit(1)

# Success summary
print("\n" + "="*70)
print("ALL TESTS PASSED - Custom Tools Working!")
print("="*70)

print("\nSummary:")
print(f"  Total tools in registry: {len(all_tools)}")
print(f"  Built-in tools: {before_count}")
print(f"  Custom tools: {after_count - before_count}")
print(f"  All schemas generated: {len(schemas)}")

print("\nCustom tools ready to use!")
print("Run 'python demo_custom_tools.py' for full agent demo")

print("\n" + "="*70)
