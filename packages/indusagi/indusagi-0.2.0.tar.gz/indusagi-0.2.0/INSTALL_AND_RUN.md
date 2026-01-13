# 🚀 Installation & Quick Run Guide

## Step-by-Step Installation

### 1. Navigate to Project

```bash
cd "C:\Users\Varun israni\agent-framework-build-plan"
```

### 2. Install UV Package Manager (if not installed)

```bash
pip install uv
```

### 3. Create Virtual Environment

```bash
uv venv
```

### 4. Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 5. Install the Framework

```bash
uv pip install -e ".[dev]"
```

This installs:
- All core dependencies (openai, typer, rich, pydantic)
- All dev dependencies (pytest, black, ruff)
- The package in editable mode (changes reflect immediately)

### 6. Configure API Key

```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your OpenAI API key
# Replace YOUR_API_KEY_HERE with: sk-proj-YOUR_ACTUAL_KEY_HERE
```

**Your .env file should look like:**
```env
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
```

### 7. Verify Installation

```bash
# Check CLI is installed
indusagi --help

# Test API connection
indusagi test-connection

# List available tools
indusagi list-tools

# Show version
indusagi version
```

---

## 🎯 Quick Run Examples

### Single Query Mode

```bash
# Math calculation
indusagi run "What is 144 divided by 12?"

# Time query
indusagi run "What time is it?"

# General query
indusagi run "Tell me a fun fact about AI"
```

### Interactive Chat Mode

```bash
# Start interactive mode
indusagi interactive
```

In interactive mode, try:
```
You: What is 25 * 48?
Agent: 25 * 48 equals 1,200

You: What time is it?
Agent: The current time is 2:34:56 PM

You: /help
[Shows available commands]

You: /quit
[Exits interactive mode]
```

### Verbose Mode (See What's Happening)

```bash
indusagi run "Calculate 100 / 4" --verbose
```

This shows:
- Which agent is selected
- Routing decision
- Tools being called
- Response generation

---

## 🧪 Run Tests

```bash
# Run all tests
pytest tests/ -v

# Expected output:
# ============================= test session starts =============================
# collected 255 items
#
# tests\test_agent.py ...............................                      [ 12%]
# tests\test_cli.py ..............................................         [ 30%]
# tests\test_config.py ......................................              [ 45%]
# tests\test_integration.py .........................                      [ 54%]
# tests\test_memory.py .....................................               [ 69%]
# tests\test_orchestrator.py .................................             [ 82%]
# tests\test_tools.py .............................................        [100%]
#
# ======================= 255 passed in 0.67s ===============================
```

---

## 📝 Run Examples

```bash
# Basic agent usage
python examples/basic_usage.py

# Memory system demo
python examples/memory_example.py

# Orchestrator demo
python examples/orchestrator_demo.py
```

---

## 🐍 Use in Python Code

Create a file `test_my_agent.py`:

```python
from indusagi import Agent, create_orchestrator

# Option 1: Single agent
print("=== Single Agent ===")
agent = Agent("MyBot", "Helpful assistant")
response = agent.process("What is 25 * 4?")
print(f"Response: {response}\n")

# Option 2: Multi-agent orchestrator (recommended)
print("=== Multi-Agent Orchestrator ===")
orchestrator = create_orchestrator()

# Math query (routes to Math Agent)
response = orchestrator.process("What is 144 / 12?")
print(f"Response: {response.response}")
print(f"Agent: {response.agent_used}")
print(f"Confidence: {response.confidence_score}\n")

# Time query (routes to Time Agent)
response = orchestrator.process("What time is it?")
print(f"Response: {response.response}")
print(f"Agent: {response.agent_used}\n")

# General query (routes to General Agent)
response = orchestrator.process("Tell me a joke")
print(f"Response: {response.response}")
print(f"Agent: {response.agent_used}")
```

Run it:
```bash
python test_my_agent.py
```

---

## 🔧 Troubleshooting

### Issue: "my-agent: command not found"

**Solution:**
```bash
# Make sure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Reinstall in editable mode
uv pip install -e .
```

### Issue: "OPENAI_API_KEY not set"

**Solution:**
```bash
# Check .env file exists
dir .env  # Windows
ls .env   # Mac/Linux

# Make sure it contains your API key
type .env  # Windows
cat .env   # Mac/Linux

# Should show: OPENAI_API_KEY=sk-proj-...
```

### Issue: "Module not found: indusagi"

**Solution:**
```bash
# Verify installation
pip list | findstr indusagi  # Windows
pip list | grep indusagi     # Mac/Linux

# Reinstall
uv pip install -e . --force-reinstall
```

### Issue: Tests failing

**Solution:**
```bash
# Make sure API key is set
indusagi test-connection

# Run tests with verbose output
pytest tests/ -v -s
```

---

## ✅ Verification Checklist

Run these commands to verify everything works:

```bash
# 1. Check virtual environment is activated
echo $VIRTUAL_ENV  # Should show path to .venv

# 2. Check CLI is installed
indusagi --help  # Should show help message

# 3. Check API key is configured
indusagi test-connection  # Should show "✓ API connection successful"

# 4. List tools
indusagi list-tools  # Should show 9 tools

# 5. List agents
indusagi list-agents  # Should show 3 agents

# 6. Run a test query
indusagi run "What is 2+2?"  # Should respond with "4"

# 7. Run tests
pytest tests/ -v  # Should show 255 passed

# 8. Check package is installed
pip show indusagi  # Should show package info
```

---

## 🎉 You're Ready!

If all verification steps pass, you're ready to use the framework!

Try:
```bash
# Start interactive mode and chat with the AI
indusagi interactive
```

For more information:
- **Full documentation**: See `README.md`
- **Quick reference**: See `QUICK_START.md`
- **Examples**: See `examples/` directory
- **API reference**: See component-specific guides in `docs/`

---

**Need Help?**

Check these files:
- `FINAL_PROJECT_SUMMARY.md` - Complete project overview
- `README.md` - Comprehensive documentation
- `QUICK_START.md` - Fast reference guide
- Component guides in root directory (AGENT_README.md, etc.)
