# 📊 Tool Usage Logging - Complete Guide

## Overview

The **Tool Usage Logger** automatically tracks every tool call made by your agents, providing detailed analytics, debugging insights, and performance metrics.

---

## Features

### ✅ What Gets Logged

For every tool call, the logger records:

- **Tool Name** - Which tool was used (bash, write, read, etc.)
- **Agent Name** - Which agent made the call
- **Timestamp** - When the call was made
- **Arguments** - What parameters were passed
- **Result** - What the tool returned
- **Success Status** - Whether it succeeded or failed
- **Execution Time** - How long it took (in seconds)
- **Error Message** - If it failed, why

### 📈 Analytics Provided

- **Total Calls** - How many times tools were used
- **Success Rate** - Percentage of successful calls
- **Execution Times** - Average and total execution time
- **Tool Distribution** - Which tools are used most
- **Agent Activity** - Which agents are most active
- **Failed Calls** - All errors and failures

---

## Usage

### Automatic Logging

Logging happens **automatically**! No setup needed. Every tool call is logged.

```python
from indusagi import tool_logger

# Tools are logged automatically as agents use them
# Nothing to configure!
```

### View Recent Tool Calls

```python
# In terminal demo
/logs

# Or programmatically
tool_logger.print_recent_calls(limit=10)
```

**Example Output:**
```
======================================================================
📝 RECENT TOOL CALLS (Last 10)
======================================================================

1. ✅ [Coder] todo_write
   Time: 2025-01-02T15:30:45
   Args: todos=[...]
   Result: Todo list updated. Summary: total=5, done=0, in_progress=1...

2. ✅ [Coder] bash
   Time: 2025-01-02T15:30:46
   Args: command=mkdir game_website, command_description=Create project folder
   Result: Exit code: 0
(No output)

3. ✅ [Coder] write
   Time: 2025-01-02T15:30:47
   Args: file_path=game_website/index.html, content=<!DOCTYPE html>...
   Result: Successfully created file 'game_website/index.html'

... (7 more)
======================================================================
```

### View Statistics

```python
# In terminal demo
/stats

# Or programmatically
tool_logger.print_statistics()
```

**Example Output:**
```
======================================================================
📊 TOOL USAGE STATISTICS
======================================================================

📈 Overall:
  Total Calls:     15
  Successful:      14 (93.3%)
  Failed:          1
  Session Time:    45.2s
  Total Exec Time: 3.45s
  Avg Exec Time:   0.230s

🔧 Tools Used:
  todo_write            5 calls  (100% success, 0.015s avg)
  write                 4 calls  (100% success, 0.120s avg)
  bash                  4 calls  (75% success, 0.450s avg)
  read                  2 calls  (100% success, 0.080s avg)

🤖 Agents Active:
  Coder                12 calls
  Planner               3 calls
======================================================================
```

### Export to JSON

```python
# In terminal demo
/export

# Or programmatically
tool_logger.export_to_json("my_logs.json")
```

**Example JSON:**
```json
{
  "session_start": "2025-01-02T15:30:00",
  "statistics": {
    "total_calls": 15,
    "successful_calls": 14,
    "success_rate": 93.3,
    "tools_used": {
      "todo_write": 5,
      "write": 4,
      "bash": 4
    }
  },
  "calls": [
    {
      "tool_name": "bash",
      "timestamp": 1735832446.123,
      "datetime": "2025-01-02T15:30:46",
      "agent_name": "Coder",
      "arguments": {
        "command": "mkdir game_website",
        "command_description": "Create project folder"
      },
      "result": "Exit code: 0\n(No output)",
      "success": true,
      "execution_time": 0.045
    }
  ]
}
```

---

## Terminal Commands

When running the agency in terminal demo mode:

```
You: create a website game

... agent works ...

You: /logs      ← Show recent tool calls
You: /stats     ← Show statistics
You: /export    ← Export to JSON file
```

**All Available Commands:**
- `/quit` or `/exit` - Exit the demo
- `/agents` - List all agents
- `/handoffs` - Show communication flows
- `/clear` - Clear conversation history
- `/logs` - Show recent tool usage (NEW!)
- `/stats` - Show tool statistics (NEW!)
- `/export` - Export logs to JSON (NEW!)

---

## Programmatic Access

### Get Statistics

```python
from indusagi import tool_logger

stats = tool_logger.get_statistics()

print(f"Total calls: {stats['total_calls']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Most used tool: {max(stats['tools_used'].items(), key=lambda x: x[1])}")
```

### Get Recent Calls

```python
recent = tool_logger.get_recent_calls(limit=5)

for call in recent:
    print(f"{call['tool_name']} by {call['agent_name']}: {call['success']}")
```

### Get Calls by Tool

```python
# Get all bash calls
bash_calls = tool_logger.get_calls_by_tool("bash")

print(f"Bash was used {len(bash_calls)} times")
for call in bash_calls:
    print(f"  Command: {call['arguments']['command']}")
```

### Get Calls by Agent

```python
# Get all calls made by Coder
coder_calls = tool_logger.get_calls_by_agent("Coder")

print(f"Coder made {len(coder_calls)} tool calls")
```

### Get Failed Calls

```python
# Get all failed calls
failed = tool_logger.get_failed_calls()

print(f"Found {len(failed)} failed calls:")
for call in failed:
    print(f"  {call['tool_name']}: {call['error']}")
```

---

## Use Cases

### 1. Debugging

**Problem:** Agent behavior is unexpected

**Solution:**
```python
# Check what tools were actually called
tool_logger.print_recent_calls(limit=20)

# Check for failures
failed = tool_logger.get_failed_calls()
for call in failed:
    print(f"Failed: {call['tool_name']} - {call['error']}")
```

### 2. Performance Analysis

**Problem:** Agent is slow

**Solution:**
```python
stats = tool_logger.get_statistics()

# Find slow tools
for tool, data in stats['tool_statistics'].items():
    if data['avg_execution_time'] > 1.0:  # > 1 second
        print(f"Slow tool: {tool} ({data['avg_execution_time']:.2f}s avg)")
```

### 3. Usage Analytics

**Problem:** Want to understand agent behavior patterns

**Solution:**
```python
stats = tool_logger.get_statistics()

print("Tool Usage Distribution:")
for tool, count in sorted(stats['tools_used'].items(), key=lambda x: x[1], reverse=True):
    percentage = (count / stats['total_calls']) * 100
    print(f"  {tool}: {count} calls ({percentage:.1f}%)")
```

### 4. Audit Trail

**Problem:** Need to track all actions for compliance

**Solution:**
```python
# Export complete audit log
tool_logger.export_to_json("audit_log_2025_01_02.json")

# Or get specific agent's actions
coder_actions = tool_logger.get_calls_by_agent("Coder")
# Save to database, send to logging service, etc.
```

---

## Example Session

```python
# Start agency
python example_agency.py
```

```
You: create a calculator app

======================================================================
[Coder] Creating todo list with 4 tasks:
======================================================================
  1. [!] ⏳ Create folder calculator_app
  2. [!] ⏳ Create calculator_app/index.html
  3. [~] ⏳ Create calculator_app/styles.css
  4. [~] ⏳ Create calculator_app/app.js
======================================================================

... (agent works) ...

[Coder]: Calculator app created successfully!

You: /stats

======================================================================
📊 TOOL USAGE STATISTICS
======================================================================

📈 Overall:
  Total Calls:     8
  Successful:      8 (100.0%)
  Failed:          0
  Session Time:    12.5s
  Total Exec Time: 1.23s
  Avg Exec Time:   0.154s

🔧 Tools Used:
  todo_write            3 calls  (100% success, 0.012s avg)
  bash                  1 calls  (100% success, 0.045s avg)
  write                 3 calls  (100% success, 0.250s avg)
  read                  1 calls  (100% success, 0.080s avg)

🤖 Agents Active:
  Coder                 8 calls
======================================================================

You: /export

✅ Logs exported to tool_logs_1735832500.json

You: /quit

Goodbye!
```

---

## Advanced Features

### Custom Logging

```python
from indusagi import tool_logger

# Manually log a custom event
tool_logger.log_call(
    tool_name="custom_tool",
    agent_name="MyAgent",
    arguments={"param": "value"},
    result="Success",
    success=True,
    execution_time=0.5
)
```

### Clear Logs

```python
# Clear all logs
tool_logger.clear()

# Useful for starting fresh or periodic cleanup
```

### Multiple Sessions

```python
# Export before clearing
tool_logger.export_to_json("session1.json")
tool_logger.clear()

# New session starts fresh
# ... use agency ...

tool_logger.export_to_json("session2.json")
```

---

## Integration with CI/CD

### Test Automation

```python
# test_agent.py
from indusagi import tool_logger, create_development_agency

def test_agent_tool_usage():
    tool_logger.clear()

    agency = create_development_agency()
    result = agency.process("create a simple app")

    stats = tool_logger.get_statistics()

    # Assert expected behavior
    assert stats['total_calls'] > 0, "Agent should use tools"
    assert stats['success_rate'] > 95, "Success rate should be high"
    assert 'bash' in stats['tools_used'], "Should use bash for folders"
    assert 'write' in stats['tools_used'], "Should use write for files"

    # Export for analysis
    tool_logger.export_to_json("test_results.json")
```

### Performance Monitoring

```python
# monitor.py
from indusagi import tool_logger

stats = tool_logger.get_statistics()

# Alert if performance degrades
if stats['avg_execution_time'] > 2.0:
    send_alert(f"Agent performance degraded: {stats['avg_execution_time']:.2f}s avg")

# Alert if success rate drops
if stats['success_rate'] < 90:
    send_alert(f"Agent success rate low: {stats['success_rate']:.1f}%")
```

---

## Benefits

### For Development:
- ✅ Debug agent behavior easily
- ✅ Understand tool usage patterns
- ✅ Identify performance bottlenecks
- ✅ Track down errors quickly

### For Production:
- ✅ Monitor agent performance
- ✅ Audit all actions
- ✅ Analyze usage trends
- ✅ Compliance and logging

### For Optimization:
- ✅ Find slow operations
- ✅ Identify unused tools
- ✅ Optimize workflows
- ✅ Improve efficiency

---

## Files Added

1. **`src/indusagi/tool_usage_logger.py`** - Core logging implementation
2. **`TOOL_USAGE_LOGGING.md`** - This documentation

## Files Modified

1. **`src/indusagi/agent.py`** - Integrated logging into tool execution
2. **`src/indusagi/agency.py`** - Added terminal commands (/logs, /stats, /export)
3. **`src/indusagi/__init__.py`** - Exported tool_logger

---

## Summary

**Tool Usage Logging is now FULLY INTEGRATED!** 🎉

- ✅ Automatic logging of all tool calls
- ✅ Detailed statistics and analytics
- ✅ Easy debugging with /logs command
- ✅ Performance monitoring with /stats command
- ✅ Export to JSON with /export command
- ✅ Programmatic access to all data
- ✅ Production-ready logging system

**No setup required - just use your agency and logging happens automatically!** 🚀
