# 🤖 How to Run the Planning Agent Demo

This guide shows you how to run the autonomous agent that creates plans and executes tools step-by-step.

---

## 🚀 Quick Start (3 Steps)

### 1. Set Your API Key

```bash
# Option A: Create .env file (recommended)
cp .env.example .env
# Then edit .env and add:
# OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE

# Option B: Set temporarily in terminal
# Windows PowerShell:
$env:OPENAI_API_KEY="sk-proj-YOUR_ACTUAL_KEY_HERE"

# Linux/Mac:
export OPENAI_API_KEY="sk-proj-YOUR_ACTUAL_KEY_HERE"
```

### 2. Navigate to Project

```bash
cd "C:\Users\Varun israni\agent-framework-build-plan"
```

### 3. Run the Demo

```bash
python demo_agent_with_planning.py
```

---

## 📋 What You'll See

The agent will show you:

```
======================================================================
              🚀 AUTONOMOUS AGENT WITH PLANNING DEMO
======================================================================

[Step 1/4] RECEIVING USER QUERY
----------------------------------------------------------------------
User Query: "What is 144 divided by 12, and what time is it right now?"

[Step 2/4] AGENT ANALYZING QUERY & CREATING PLAN
----------------------------------------------------------------------
Agent is thinking about which tools to use...

[Step 3/4] EXECUTING PLAN (Turn 1)
----------------------------------------------------------------------

📋 Agent's Plan: Use 2 tool(s)
  1. calculator({"expression": "144 / 12"})
  2. get_time({})

⚙️  Executing Tools:

  Tool 1/2:
  🔧 Tool: calculator
  📝 Arguments: {'expression': '144 / 12'}
  ✅ Result: 12.0

  Tool 2/2:
  🔧 Tool: get_time
  📝 Arguments: {}
  ✅ Result: 03:45:23 AM

✓ All tools executed successfully!

[Step 4/4] FINAL RESPONSE
----------------------------------------------------------------------

Agent: 144 divided by 12 equals 12. The current time is 03:45:23 AM.

----------------------------------------------------------------------
                        📊 EXECUTION SUMMARY
----------------------------------------------------------------------
Total Turns: 1
Tools Used: 2

1. Turn 1: calculator
   Args: {'expression': '144 / 12'}
   Result: 12.0

2. Turn 1: get_time
   Args: {}
   Result: 03:45:23 AM

======================================================================
                        ✅ TASK COMPLETE
======================================================================
```

---

## 🎯 Example Queries to Try

The demo includes 4 built-in examples:

1. **"What is 144 divided by 12, and what time is it right now?"**
   - Uses: calculator + get_time

2. **"Calculate 25 * 48 and then tell me the result in uppercase"**
   - Uses: calculator + text_uppercase

3. **"What's the current date and time?"**
   - Uses: get_date + get_time

4. **"Reverse the text 'HELLO WORLD' and count how many words it has"**
   - Uses: text_reverse + text_count_words

---

## 💡 Try Your Own Queries

When you run the demo, you can:

- **Press Enter** - Use example 1
- **Type 1-4** - Use one of the example queries
- **Type anything else** - Use your custom query

Example custom queries:
```
"Calculate 100 * 5 and convert it to uppercase"
"What time is it and reverse the word AGENT"
"Get the date and calculate 50 + 50"
"Convert HELLO to lowercase and count the words"
```

---

## 🔍 What the Agent Does Automatically

1. **Receives Query** - Gets your question
2. **Analyzes** - Thinks about what tools are needed
3. **Creates Plan** - Decides which tools to use and in what order
4. **Shows Plan** - Displays the plan before execution
5. **Executes Tools** - Runs each tool with the right arguments
6. **Shows Results** - Displays result of each tool
7. **Synthesizes** - Combines results into final answer
8. **Summary** - Shows what it did

**All of this happens autonomously!** The agent uses OpenAI's function calling to decide which tools to use.

---

## 🛠️ Available Tools

The agent can use any of these 9 tools:

1. **calculator** - Math calculations
2. **get_time** - Current time
3. **get_date** - Current date
4. **get_datetime** - Date and time
5. **text_uppercase** - Convert to UPPER
6. **text_lowercase** - Convert to lower
7. **text_reverse** - Reverse text
8. **text_count_words** - Count words
9. **text_title_case** - Title Case

---

## 📊 Understanding the Output

### Step 1: Receiving User Query
Shows what you asked

### Step 2: Agent Analyzing
Agent thinks about which tools to use

### Step 3: Executing Plan
- **📋 Agent's Plan** - Shows which tools will be used
- **⚙️ Executing Tools** - Runs each tool
- **🔧 Tool** - Tool name
- **📝 Arguments** - What was passed to the tool
- **✅ Result** - What the tool returned

### Step 4: Final Response
Agent's complete answer combining all tool results

### Execution Summary
- How many turns it took
- All tools used
- All arguments and results

---

## 🎓 Learning Points

This demo shows:

✅ **Autonomous Planning** - Agent decides which tools to use
✅ **Multi-Tool Usage** - Can use multiple tools in one query
✅ **Sequential Execution** - Tools run in logical order
✅ **Transparent Process** - You see every step
✅ **Real Function Calling** - Uses OpenAI's actual tool calling API

---

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"
Set your API key (see step 1 above)

### "Module not found"
Make sure you're in the project directory:
```bash
cd "C:\Users\Varun israni\agent-framework-build-plan"
```

### "Package not installed"
Install the package:
```bash
python -m pip install -e .
```

---

## 🎉 That's It!

Run the demo and watch your agent plan and execute tasks autonomously!

```bash
python demo_agent_with_planning.py
```

The agent will show you its complete thought process from planning to execution! 🚀
