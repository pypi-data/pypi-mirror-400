# 🔴 Real-Time Tool Usage Logging

## Overview

Tool usage is now displayed **in real-time** as the agent works! See every tool call, execution time, and running statistics **instantly**.

---

## What You'll See

### Before (Silent Logging):
```
[Coder] Running bash: 'mkdir calculator_app'
[Coder] ✅ Command completed successfully

[Coder] Creating file: calculator_app/index.html
[Coder] ✅ File created successfully
```

### After (Real-Time Logging):
```
[Coder] Running bash: 'mkdir calculator_app'
[Coder] ✅ Command completed successfully

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ bash
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.045s
🤖 Agent: Coder
📈 Session Stats: 5 calls | 100.0% success | 0.67s total
──────────────────────────────────────────────────────────────────────

[Coder] Creating file: calculator_app/index.html
[Coder] ✅ File created successfully

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ write
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.120s
🤖 Agent: Coder
📈 Session Stats: 6 calls | 100.0% success | 0.79s total
──────────────────────────────────────────────────────────────────────
```

---

## Complete Example Session

```
You: create a calculator app

======================================================================
[Coder] Creating todo list with 5 tasks:
======================================================================
  1. [!] ⏳ Create folder calculator_app
  2. [!] ⏳ Create calculator_app/index.html
  3. [~] ⏳ Create calculator_app/styles.css
  4. [~] ⏳ Create calculator_app/app.js
  5. [-] ⏳ Test the calculator app
======================================================================

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ todo_write
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.012s
🤖 Agent: Coder
📈 Session Stats: 1 calls | 100.0% success | 0.01s total
──────────────────────────────────────────────────────────────────────

======================================================================
[Coder] TODO LIST UPDATE:
======================================================================
  1. [!] 🔄 Create folder calculator_app
  2. [!] ⏳ Create calculator_app/index.html
  3. [~] ⏳ Create calculator_app/styles.css
  4. [~] ⏳ Create calculator_app/app.js
  5. [-] ⏳ Test the calculator app

Progress: 0 done, 1 in progress, 4 pending
======================================================================

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ todo_write
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.015s
🤖 Agent: Coder
📈 Session Stats: 2 calls | 100.0% success | 0.03s total
──────────────────────────────────────────────────────────────────────

[Coder] Running bash: 'mkdir calculator_app'
[Coder] Description: Create project folder
[Coder] ✅ Command completed successfully

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ bash
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.045s
🤖 Agent: Coder
📈 Session Stats: 3 calls | 100.0% success | 0.07s total
──────────────────────────────────────────────────────────────────────

======================================================================
[Coder] TODO LIST UPDATE:
======================================================================
  1. [!] ✅ Create folder calculator_app
  2. [!] 🔄 Create calculator_app/index.html
  3. [~] ⏳ Create calculator_app/styles.css
  4. [~] ⏳ Create calculator_app/app.js
  5. [-] ⏳ Test the calculator app

Progress: 1 done, 1 in progress, 3 pending
======================================================================

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ todo_write
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.013s
🤖 Agent: Coder
📈 Session Stats: 4 calls | 100.0% success | 0.09s total
──────────────────────────────────────────────────────────────────────

[Coder] Creating file: calculator_app/index.html
[Coder] ✅ File created successfully

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ write
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.120s
🤖 Agent: Coder
📈 Session Stats: 5 calls | 100.0% success | 0.21s total
──────────────────────────────────────────────────────────────────────

... continues for each tool call ...
```

---

## Information Displayed Per Tool Call

For **every tool call**, you instantly see:

1. **Status Icon** - ✅ success or ❌ failure
2. **Tool Name** - Which tool was used
3. **Execution Time** - How long it took (in seconds)
4. **Agent Name** - Which agent made the call
5. **Error Message** - If failed, why it failed
6. **Running Statistics**:
   - Total calls so far
   - Success rate percentage
   - Total execution time

---

## Example: Failed Tool Call

```
[Coder] Running bash: 'invalid-command'

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ❌ bash
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.050s
🤖 Agent: Coder
❌ Error: Command not found
📈 Session Stats: 10 calls | 90.0% success | 1.23s total
──────────────────────────────────────────────────────────────────────
```

---

## Benefits

### ✅ Real-Time Visibility
- See exactly what's happening as it happens
- No need to wait and check logs afterwards
- Instant feedback on tool execution

### ✅ Performance Monitoring
- See execution time for each call
- Identify slow operations immediately
- Track cumulative performance

### ✅ Easy Debugging
- Spot failures instantly
- See error messages right away
- Understand tool usage patterns

### ✅ Progress Tracking
- Running statistics show overall progress
- See success rate in real-time
- Monitor total execution time

---

## What Gets Logged

### Real-Time Display (Shown Immediately):
- ✅ Tool name and status
- ✅ Execution time
- ✅ Agent name
- ✅ Error messages (if any)
- ✅ Running statistics (calls, success rate, total time)

### Background Logging (For Later Analysis):
- ✅ Complete arguments
- ✅ Complete results
- ✅ Detailed statistics
- ✅ Export to JSON

---

## Commands Still Available

All the original commands still work:

```
You: /logs     ← View detailed recent calls
You: /stats    ← View comprehensive statistics
You: /export   ← Export to JSON file
```

**Now you get:**
- **Real-time** brief stats during execution
- **Detailed** full stats with `/logs` and `/stats`
- **Exportable** data with `/export`

---

## Complete Workflow

### 1. Run the Agency
```powershell
python example_agency.py
```

### 2. Give Instructions
```
You: create a todo app
```

### 3. Watch Real-Time Logging
```
[Agent works...]

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ bash
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.045s
🤖 Agent: Coder
📈 Session Stats: 3 calls | 100.0% success | 0.07s total
──────────────────────────────────────────────────────────────────────

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ write
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.120s
🤖 Agent: Coder
📈 Session Stats: 4 calls | 100.0% success | 0.19s total
──────────────────────────────────────────────────────────────────────

... and so on ...
```

### 4. View Detailed Stats (Optional)
```
You: /stats

======================================================================
📊 TOOL USAGE STATISTICS
======================================================================

📈 Overall:
  Total Calls:     12
  Successful:      12 (100.0%)
  Failed:          0
  Session Time:    45.2s
  Total Exec Time: 1.45s
  Avg Exec Time:   0.121s

🔧 Tools Used:
  todo_write            5 calls  (100% success, 0.014s avg)
  write                 3 calls  (100% success, 0.125s avg)
  bash                  3 calls  (100% success, 0.048s avg)
  read                  1 calls  (100% success, 0.085s avg)

🤖 Agents Active:
  Coder                12 calls
======================================================================
```

---

## Comparison

### Before (No Real-Time Logging):
- ❌ Silent tool execution
- ❌ No performance visibility
- ❌ Must use `/logs` to see anything
- ❌ Can't see issues until after

### After (Real-Time Logging):
- ✅ Instant feedback on every tool call
- ✅ Real-time performance metrics
- ✅ See issues immediately as they happen
- ✅ Running statistics always visible
- ✅ Plus all the old commands still work

---

## Example: Multi-Agent Handoff

```
You: create a complex app

[Coder working...]

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ bash
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.050s
🤖 Agent: Coder
📈 Session Stats: 5 calls | 100.0% success | 0.45s total
──────────────────────────────────────────────────────────────────────

[Coder] Handing off to Planner: Need help planning architecture...

[Planner working...]

──────────────────────────────────────────────────────────────────────
📊 TOOL USAGE: ✅ read
──────────────────────────────────────────────────────────────────────
⏱️  Execution Time: 0.080s
🤖 Agent: Planner
📈 Session Stats: 6 calls | 100.0% success | 0.53s total
──────────────────────────────────────────────────────────────────────
```

See which agent is using which tool in real-time!

---

## Files Modified

### Modified:
- ✅ `src/indusagi/agent.py` - Added real-time logging display

### Created:
- ✅ `REAL_TIME_TOOL_LOGGING.md` - This documentation

---

## Test It Now!

```powershell
python example_agency.py
```

```
You: create a calculator app
```

Watch the real-time tool usage appear after every tool call! 🎉

---

## Result

**Real-time tool usage logging is now LIVE!** 🚀

- ✅ Instant feedback on every tool call
- ✅ Execution time shown immediately
- ✅ Running statistics always visible
- ✅ Errors displayed right away
- ✅ Performance monitoring in real-time
- ✅ Complete visibility into agent actions

**No more waiting to see what happened - watch it live!** 📊
