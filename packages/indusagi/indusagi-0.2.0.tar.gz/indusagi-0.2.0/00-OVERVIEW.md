# Building Your Own indus-agents: 2-3 Hour Live Coding Plan

## 🎯 Project Goal

Build a **production-ready, minimal indus-agents** from scratch in 2-3 hours that:
- Supports multiple AI agents with specialized roles
- Implements tool/function calling
- Handles conversation memory
- Can be packaged and distributed
- Works locally and can be deployed

## 📁 Documentation Structure

This folder contains everything you need for a successful live coding session:

1. **00-OVERVIEW.md** (This file) - Project overview and quick navigation
2. **01-SESSION-PLAN.md** - Detailed 2-3 hour timeline with milestones
3. **02-ARCHITECTURE.md** - Framework architecture and design decisions
4. **03-IMPLEMENTATION-GUIDE.md** - Step-by-step coding instructions
5. **04-TOOL-SYSTEM.md** - Tool integration patterns and examples
6. **05-PACKAGING-DEPLOYMENT.md** - Package, test locally, and deploy
7. **06-QUICK-REFERENCE.md** - Code snippets and troubleshooting

## ⚡ Quick Start (3 Commands)

```bash
# 1. Setup project (30 seconds)
uv init --package indusagi && cd indusagi

# 2. Add dependencies (30 seconds)
uv add typer anthropic rich pydantic && uv add --dev pytest pytest-asyncio

# 3. Install editable + start coding (30 seconds)
uv pip install -e .
```

## 🎬 Session Timeline Overview

### **2-Hour Session**
- **00:00-00:10** Setup & Environment
- **00:10-01:00** Core Agent Foundation
- **01:00-01:10** Break & Checkpoint
- **01:10-02:00** Tools & Multi-Agent
- **02:00-02:10** Testing & Package

### **3-Hour Session**
- **00:00-00:15** Setup & Environment
- **00:15-01:15** Foundation (Agent + Config)
- **01:15-01:25** Break
- **01:25-02:25** Core Features (Tools + Memory)
- **02:25-02:35** Break
- **02:35-03:15** Advanced (Multi-Agent + Orchestration)
- **03:15-03:30** Package & Deploy

## 🏗️ What You'll Build

### Minimal Viable Framework Components:

```
indusagi/
├── src/indusagi/
│   ├── __init__.py
│   ├── agent.py          # Core Agent class
│   ├── tools.py          # Tool registry & decorators
│   ├── memory.py         # Conversation memory
│   ├── orchestrator.py   # Multi-agent coordination
│   └── cli.py            # CLI interface (Typer)
├── tests/
│   ├── test_agent.py
│   └── test_tools.py
├── pyproject.toml        # Modern Python packaging
└── README.md
```

### Core Features:
- ✅ **Agent Class** with LLM integration (Claude/OpenAI)
- ✅ **Tool System** with auto-schema generation
- ✅ **Memory Management** (conversation history)
- ✅ **Multi-Agent Orchestration** (2-3 specialized agents)
- ✅ **CLI Interface** (professional command-line tool)
- ✅ **Local Testing** (editable install, instant feedback)
- ✅ **Packaging** (pyproject.toml, ready for PyPI)

## 🛠️ Tech Stack (Optimized for Speed)

### Core Libraries:
- **anthropic** or **openai** - LLM API integration
- **pydantic** - Data validation & schema generation
- **typer** - Modern CLI creation
- **rich** - Beautiful terminal output

### Development Tools:
- **uv** - 10-100x faster than pip/poetry (2025 standard)
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support

### Why This Stack?
- **Minimal dependencies** - Only 4 core libraries
- **Fast iteration** - UV + editable install = instant feedback
- **Type-safe** - Pydantic catches errors at runtime
- **Professional UX** - Typer + Rich = beautiful CLI

## 🎓 Prerequisites

### Required Knowledge:
- Python 3.9+ basics
- Basic understanding of LLMs and APIs
- Command line familiarity

### Required Setup (Before Session):
- Python 3.9+ installed
- API key for Anthropic or OpenAI
- Code editor (VS Code, PyCharm, etc.)
- Terminal access

### Recommended (Optional):
- Git for version control
- Virtual environment experience
- Basic async/await understanding

## 📋 Pre-Session Checklist

### Environment Setup (15 minutes before):
- [ ] Install UV: `pip install uv`
- [ ] Get API key: https://console.anthropic.com/
- [ ] Test API: `export ANTHROPIC_API_KEY="your-key"`
- [ ] Create project folder
- [ ] Open documentation in browser
- [ ] Set readable font size in editor (14-18pt)
- [ ] Close unnecessary applications

### Documentation Ready:
- [ ] Anthropic API docs: https://docs.anthropic.com/
- [ ] Typer docs: https://typer.tiangolo.com/
- [ ] Pydantic docs: https://docs.pydantic.dev/

## 🚀 Success Criteria

By the end of the session, you'll have:

1. **Working indus-agents** that:
   - Connects to Claude/GPT API
   - Uses 2-3 tools (calculator, web search, etc.)
   - Maintains conversation memory
   - Routes between specialized agents

2. **Professional Package** that:
   - Installs via `pip install indusagi`
   - Provides CLI: `indusagi run "query"`
   - Has tests: `pytest` passes
   - Works in editable mode for development

3. **Knowledge & Skills**:
   - Understanding of agent architecture
   - Tool calling patterns
   - Modern Python packaging
   - Rapid prototyping techniques

## 🎯 Key Principles

### YAGNI (You Aren't Gonna Need It)
- Build only what's needed NOW
- Skip: Vector databases, RAG, complex orchestration
- Focus: Working agent with tools

### Test-Driven Iteration
- Write 10-20 lines → Test immediately
- Don't batch changes
- Use print statements liberally

### Incremental Delivery
- Each 20-30 minute block delivers something working
- Always have a "demo-able" state
- Commit after each working feature

### Speed Over Perfection
- Hardcode initially, refactor later
- Mock external calls when needed
- Simple solutions first

## 📖 How to Use This Guide

### For Live Coding:
1. **Read**: 00-OVERVIEW (this file) - 5 minutes
2. **Review**: 01-SESSION-PLAN - 5 minutes
3. **Reference**: 02-ARCHITECTURE while coding
4. **Follow**: 03-IMPLEMENTATION-GUIDE step-by-step
5. **Copy-paste**: 06-QUICK-REFERENCE for code snippets

### For Self-Study:
- Read all documents in order
- Try each code example
- Modify and experiment
- Build your own variations

### For Team Sessions:
- One person reads overview
- Rotate coding every 30 minutes
- Test together after each feature
- Discuss architecture decisions

## 🆘 When Things Go Wrong

### Stuck on a Bug?
→ See **06-QUICK-REFERENCE.md** - Troubleshooting section

### Out of Time?
→ See **01-SESSION-PLAN.md** - Contingency timeline

### API Not Working?
→ Use mock responses (examples in **04-TOOL-SYSTEM.md**)

### Lost Direction?
→ Return to this overview, check current milestone

## 🌟 Next Steps After Session

### Immediate (Day 1):
- Add 2-3 more tools
- Improve error handling
- Write more tests
- Document usage

### Short-term (Week 1):
- Add async support
- Implement streaming
- Add configuration file
- Create examples

### Long-term (Month 1):
- Publish to PyPI
- Add vector memory
- Implement RAG
- Build web interface

## 📚 Additional Resources

### Official Documentation:
- **Anthropic Tool Use**: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **Python Packaging Guide**: https://packaging.python.org/

### Tutorials:
- **Build Agent in 30 min**: https://siddharthbharath.com/build-a-coding-agent-python-tutorial
- **Simon Willison's ReAct Pattern**: https://til.simonwillison.net/llms/python-react-pattern
- **UV Quick Start**: https://docs.astral.sh/uv/

### Frameworks to Study Later:
- **LangGraph** - Complex, graph-based (when you need more control)
- **CrewAI** - Production-ready (when building for production)
- **AutoGen** - Conversational (when building chat systems)

## 🎬 Let's Begin!

Ready to start? Open **01-SESSION-PLAN.md** for your detailed timeline!

---

**Last Updated**: January 2025
**Optimized For**: Python 3.9+, UV package manager, Modern tooling
**Estimated Time**: 2-3 hours
**Difficulty**: Intermediate
