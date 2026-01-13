# How to Test Custom Tools - Complete Guide

## Quick Commands

All commands assume you're in the project directory:
```bash
cd "C:\Users\Varun israni\agent-framework-build-plan"
```

---

## Test 1: Quick Verification (No API Key Needed)

This test verifies custom tools work without making any API calls.

```bash
python test_custom_tools_quick.py
```

**Expected Output:**
```
======================================================================
QUICK TEST - Custom Tools Functionality
======================================================================

[Test 1/5] Importing custom tools... [PASS]
  Tools before import: 9
  Tools after import: 18
  New tools added: 9

[Test 2/5] Verifying custom tools exist... [PASS]
  Found 9/9 custom tools

[Test 3/5] Testing custom tool execution... [PASS]
  All 6 custom tool tests passed

[Test 4/5] Checking OpenAI schemas... [PASS]
  Custom tool schemas: 9

[Test 5/5] Verifying schema structure... [PASS]
  Schema structure is valid

======================================================================
ALL TESTS PASSED - Custom Tools Working!
======================================================================
```

**Time:** ~2 seconds

---

## Test 2: Full Demo with Agent (Requires API Key)

This runs the complete demo showing agent using custom tools.

```bash
python demo_custom_tools.py
```

**What You'll See:**
1. Custom tools loading (9 tools imported)
2. Tool verification (all 18 tools listed)
3. Direct tool execution (4 examples)
4. Agent using custom tools (5 test queries)
5. Interactive mode option (press Enter to skip)

**Time:** ~30-60 seconds (depends on API calls)

**Example Output:**
```
======================================================================
STEP 1: LOADING CUSTOM TOOLS
======================================================================

Before importing custom_tools.py:
  Total tools in registry: 9

After importing custom_tools.py:
  Total tools in registry: 18

[... continues with tests ...]

DEMO COMPLETE - CUSTOM TOOLS WORKING!
```

---

## Test 3: Planning Agent with Custom Tools

Test the planning agent that shows its tool usage.

```bash
python demo_agent_with_planning.py
```

Then enter a query that uses custom tools:
```
What's the weather in London and pick a random number between 1 and 100?
```

**Expected:** Agent will show its plan and execute both custom tools.

---

## Test 4: Direct Tool Execution

Test individual tools directly without the agent.

```bash
python -c "from indusagi import registry; import custom_tools; print(registry.execute('get_weather', city='Paris', unit='celsius'))"
```

**Output:** `Weather in Paris: [condition], [temp] degrees C`

**Try Different Tools:**

```bash
# Random number
python -c "from indusagi import registry; import custom_tools; print(registry.execute('random_number', min_value=1, max_value=10))"

# Date calculator
python -c "from indusagi import registry; import custom_tools; print(registry.execute('date_calculator', days_from_now=30))"

# Text statistics
python -c "from indusagi import registry; import custom_tools; print(registry.execute('text_stats', text='Hello World'))"

# Password generator
python -c "from indusagi import registry; import custom_tools; print(registry.execute('generate_password', length=16, include_symbols=True))"

# Pick random item
python -c "from indusagi import registry; import custom_tools; print(registry.execute('pick_random_item', items='apple,banana,orange', separator=','))"
```

---

## Test 5: List All Tools

See all registered tools (built-in + custom).

```bash
python -c "from indusagi import registry; import custom_tools; print('\n'.join(registry.list_tools()))"
```

**Expected Output:**
```
calculator
get_time
get_date
get_datetime
text_uppercase
text_lowercase
text_reverse
text_count_words
text_title_case
get_weather
create_file
read_file
random_number
generate_password
text_stats
date_calculator
pick_random_item
build_search_url
```

---

## Test 6: Create and Test Your Own Tool

### Step 1: Open custom_tools.py

```bash
notepad custom_tools.py
```

### Step 2: Add Your Tool (at the end of the file)

```python
@registry.register
def my_custom_tool(text: str) -> str:
    """
    Example custom tool - converts text to alternating case.

    Args:
        text: Text to convert

    Returns:
        Text in aLtErNaTiNg CaSe
    """
    result = ''.join(
        c.upper() if i % 2 == 0 else c.lower()
        for i, c in enumerate(text)
    )
    return f"Alternating case: {result}"
```

### Step 3: Test Your Tool

```bash
python -c "from indusagi import registry; import custom_tools; print(registry.execute('my_custom_tool', text='Hello World'))"
```

**Expected:** `Alternating case: HeLlO WoRlD`

### Step 4: Use with Agent

```bash
python
```

Then in Python:
```python
from indusagi import Agent
import custom_tools

agent = Agent("TestBot", "Test assistant")
response = agent.process_with_tools("Convert 'Hello World' to alternating case")
print(response)
```

---

## Test 7: Integration Test

Run the main integration test to verify framework + custom tools.

```bash
python test_integration_quick.py
```

**Expected:** All 7 tests pass

---

## Example Agent Queries with Custom Tools

Try these queries with the agent to see custom tools in action:

### Weather Tool
```
"What's the weather in Tokyo?"
"Get weather for London in fahrenheit"
```

### Random Number Tool
```
"Generate a random number between 1 and 100"
"Pick a random number from 50 to 75"
```

### Date Calculator Tool
```
"What will the date be 30 days from now?"
"What was the date 15 days ago?"
```

### Text Stats Tool
```
"Get statistics for the text 'Custom tools are awesome!'"
"Analyze this text: Hello World"
```

### Password Generator Tool
```
"Generate a secure password of length 16"
"Create a password with 20 characters and symbols"
```

### Pick Random Item Tool
```
"Pick a random item from: apple,banana,orange,grape"
"Choose randomly from: red,blue,green,yellow,purple"
```

### Search URL Builder Tool
```
"Build a Google search URL for 'artificial intelligence'"
"Create a Bing search URL for 'Python programming'"
```

### Multiple Tools in One Query
```
"What's the weather in Paris and pick a random number between 1 and 50?"
"Get the date 10 days from now and generate a password"
"Pick a random item from red,blue,green and calculate 25 * 4"
```

---

## Interactive Testing

### Method 1: Demo Script

```bash
python demo_custom_tools.py
```

When prompted, enter your own queries.

### Method 2: Python REPL

```bash
python
```

Then:
```python
from indusagi import Agent
import custom_tools

agent = Agent("CustomToolBot", "Assistant with custom tools")

# Test queries
queries = [
    "What's the weather in Tokyo?",
    "Generate a random number between 1 and 100",
    "What will the date be 7 days from now?",
    "Get statistics for 'Hello World'"
]

for query in queries:
    print(f"\nQuery: {query}")
    response = agent.process_with_tools(query)
    print(f"Response: {response}\n")
```

### Method 3: Planning Agent

```bash
python demo_agent_with_planning.py
```

When prompted, type your custom query using custom tools.

---

## Verification Checklist

Use this checklist to verify everything works:

- [ ] **Test 1:** Quick test passes (all 5 tests)
- [ ] **Test 2:** Demo runs successfully
- [ ] **Test 3:** Can execute tools directly
- [ ] **Test 4:** Can list all 18 tools
- [ ] **Test 5:** Agent uses custom tools in queries
- [ ] **Test 6:** Can create and test own tool
- [ ] **Test 7:** Integration test passes

**If all checked:** Custom tools feature is fully working! ✅

---

## Troubleshooting

### API Key Issues

If you get "OPENAI_API_KEY not found":

```bash
# Check if .env exists
dir .env

# If not, create it
copy .env.example .env

# Edit and add your key
notepad .env
```

### Import Errors

If you get "Module not found":

```bash
# Make sure you're in the right directory
cd "C:\Users\Varun israni\agent-framework-build-plan"

# Verify package is installed
python -c "import indusagi; print('OK')"

# If not, install it
python -m pip install -e .
```

### Tool Not Found

If agent can't find your tool:

```bash
# Verify tool is registered
python -c "from indusagi import registry; import custom_tools; print('my_tool_name' in registry.list_tools())"

# If False, check:
# 1. Did you add @registry.register decorator?
# 2. Did you import custom_tools?
# 3. Is the tool in custom_tools.py?
```

---

## Performance Benchmarks

Expected execution times on a typical system:

| Test | Time | API Calls |
|------|------|-----------|
| Quick test | ~2 sec | 0 |
| Direct tool execution | < 1 sec | 0 |
| List tools | < 1 sec | 0 |
| Agent with 1 tool | ~2-5 sec | 1-2 |
| Agent with multiple tools | ~5-10 sec | 2-3 |
| Full demo | ~30-60 sec | 5 |

---

## Summary

**Fastest way to verify everything works:**

```bash
# 1. Quick test (2 seconds)
python test_custom_tools_quick.py

# 2. Direct execution test (1 second)
python -c "from indusagi import registry; import custom_tools; print(registry.execute('get_weather', city='Tokyo', unit='celsius'))"

# 3. Full demo (30-60 seconds, requires API key)
python demo_custom_tools.py
```

**All tests passing?** You're ready to build custom tools! 🚀

---

## Next Steps

1. ✅ Run quick test
2. ✅ Run full demo
3. ✅ Read HOW_TO_CREATE_CUSTOM_TOOLS.md
4. ✅ Create your first custom tool
5. ✅ Test it with the agent
6. ✅ Build more tools!

**Happy coding!** 🛠️
