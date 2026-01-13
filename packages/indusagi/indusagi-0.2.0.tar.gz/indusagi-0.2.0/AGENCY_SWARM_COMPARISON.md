# Agency-Code vs indus-agents: Comprehensive Comparison

## Executive Summary

This document provides a detailed comparison between **Agency-Code** (built on Agency Swarm framework) and **indus-agents** to identify gaps and opportunities for enhancement.

---

## 1. Architecture Comparison

### Agency-Code Architecture

```
┌─────────────────────────────────────────┐
│          Agency (Orchestrator)          │
│  - Manages communication flows          │
│  - Routes messages between agents       │
│  - Maintains shared context             │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴──────┬────────────────────────┐
    │             │                        │
    v             v                        v
┌─────────┐ ┌──────────────┐         ┌────────────┐
│ Planner │ │ Agency Code  │         │ Subagents  │
│ Agent   │ │ Agent        │         │ (optional) │
└─────────┘ └──────────────┘         └────────────┘
```

**Key Components:**
- **Agency Class**: Central orchestrator managing multiple agents
- **Communication Flows**: Bidirectional handoff mechanisms
- **SendMessageHandoff**: Tool for agent-to-agent transfer
- **Shared Instructions**: Project-wide context for all agents
- **Factory Pattern**: `create_*_agent()` functions for fresh instances

### indus-agents Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Multi-Agent Orchestrator (35 KB, 1085 lines)        │
│  • Intelligent Routing Engine (keyword + weighted scoring)      │
│  • Agent Type Enum (General, Math, Time/Date)                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────┐   ┌────────┐    ┌────────┐
    │ Agent  │   │ Agent  │    │ Agent  │
    │General │   │ Math   │    │ Time   │
    └────────┘   └────────┘    └────────┘
```

**Key Components:**
- **MultiAgentOrchestrator**: Keyword-based routing to specialized agents
- **Agent Class**: Single agent with tool calling capability
- **ToolRegistry**: Decorator-based tool registration
- **ConversationMemory**: Thread-safe message storage

---

## 2. Feature Comparison Matrix

| Feature | Agency-Code | indus-agents | Gap Level |
|---------|-------------|--------------|-----------|
| **Multi-Agent Support** | ✅ True multi-agent with handoffs | ⚠️ Keyword routing only | CRITICAL |
| **Agent Handoffs** | ✅ SendMessageHandoff tool | ❌ Not available | CRITICAL |
| **Communication Flows** | ✅ Bidirectional defined flows | ❌ No inter-agent communication | CRITICAL |
| **Agent Generation** | ✅ Factory pattern with templates | ❌ Manual creation | HIGH |
| **Instruction Templates** | ✅ Markdown with placeholders | ❌ Hardcoded prompts | HIGH |
| **Hook System** | ✅ Lifecycle hooks | ❌ Not available | MEDIUM |
| **Shared Context** | ✅ Agency-wide state | ❌ Per-agent only | MEDIUM |
| **Dev Tools (Bash/Git)** | ✅ 14+ production tools | ⚠️ 9 basic tools | HIGH |
| **File Operations** | ✅ Read/Write/Edit/MultiEdit | ⚠️ Basic only | HIGH |
| **Code Search** | ✅ Glob/Grep | ❌ Not available | HIGH |
| **Git Integration** | ✅ Full git operations | ❌ Not available | HIGH |
| **Jupyter Support** | ✅ NotebookRead/Edit | ❌ Not available | MEDIUM |
| **CLI** | ⚠️ Terminal demo only | ✅ Full CLI with Typer | indus-agents better |
| **Memory System** | ⚠️ Basic | ✅ Full with persistence | indus-agents better |
| **Type Safety** | ✅ Pydantic throughout | ✅ Pydantic throughout | Equal |

---

## 3. Tool System Comparison

### Agency-Code Tools (14 tools)

| Category | Tools |
|----------|-------|
| **File I/O** | Read, Write, Edit, MultiEdit, NotebookRead, NotebookEdit |
| **Search** | Glob, Grep |
| **Execution** | Bash, Git, LS |
| **Navigation** | ExitPlanMode |
| **Web** | ClaudeWebSearch, WebSearchTool |
| **Project Mgmt** | TodoWrite |

### indus-agents Tools (9+ tools)

| Category | Tools |
|----------|-------|
| **Math** | calculator |
| **Time** | get_time, get_date, get_datetime |
| **Text** | text_uppercase, text_lowercase, text_reverse, text_title_case, text_count_words |
| **Custom** | get_weather, create_file, read_file, random_number, generate_password |

### Missing Critical Tools in indus-agents

1. **Bash** - Execute shell commands with timeout
2. **Git** - Version control operations
3. **Glob** - File pattern matching with .gitignore support
4. **Grep** - Regex-based content search
5. **Edit/MultiEdit** - Safe string replacement in files
6. **TodoWrite** - Task management with status tracking
7. **LS** - Directory listing with metadata

---

## 4. Agent Communication Patterns

### Agency-Code: True Multi-Agent Handoffs

```python
# Communication flows define who can talk to whom
agency = Agency(
    coder, planner,
    communication_flows=[
        (coder, planner, SendMessageHandoff),  # Coder → Planner
        (planner, coder, SendMessageHandoff),  # Planner → Coder
    ],
)

# Agent can handoff during execution
# PlannerAgent: "Planning complete, handing off to coder..."
# -> AgencyCodeAgent receives context and continues
```

### indus-agents: Keyword-Based Routing (No Handoffs)

```python
# Routing based on keyword matching
class MultiAgentOrchestrator:
    def route_query(self, query) -> RoutingDecision:
        scores = self._analyze_query(query)  # Keyword matching
        return max(scores, key=scores.get)   # Single agent selected

# Once routed, no inter-agent communication possible
```

---

## 5. Instruction System Comparison

### Agency-Code: Template-Based Instructions

```markdown
# instructions.md with placeholders

You are {class_name} - a specialized agent.

# Environment
<env>
Working directory: {cwd}
Is directory a git repo: {is_git_repo}
Platform: {platform}
Today's date: {today}
Model Name: {model}
</env>
```

**Features:**
- Model-specific variants (`instructions-gpt-5.md`)
- Runtime placeholder replacement
- Shared project-overview.md across all agents

### indus-agents: Hardcoded System Prompts

```python
# In agent.py or orchestrator.py
system_prompt = "You are a helpful assistant..."
```

**Limitations:**
- No template system
- No model-specific variants
- No runtime context injection

---

## 6. Key Architectural Differences

| Aspect | Agency-Code | indus-agents |
|--------|-------------|--------------|
| **Agent Creation** | Factory functions (`create_*_agent()`) | Direct instantiation |
| **Agent Directory** | Each agent in own directory with instructions | Single agent class |
| **Tool Organization** | tools/ folder with individual files | Single tools.py file |
| **Model Support** | Multi-model via LiteLLM (GPT, Claude, Grok) | OpenAI-focused |
| **Hooks** | Full lifecycle hooks (on_start, on_end, on_tool_*) | None |
| **State Sharing** | Agency-wide shared state | Per-agent only |

---

## 7. Strengths of Each Framework

### Agency-Code Strengths
1. **True multi-agent collaboration** with handoffs
2. **Comprehensive dev tools** for software engineering
3. **Agency Swarm framework** provides solid foundation
4. **Model-agnostic** via LiteLLM integration
5. **Production-grade tools** with safety features

### indus-agents Strengths
1. **Professional CLI** with Rich formatting
2. **Comprehensive memory system** with persistence
3. **Clean, understandable codebase** (~5000 lines)
4. **Excellent type safety** with Pydantic
5. **Thread-safe operations** with proper locking
6. **Token counting and cost estimation**
7. **No external framework dependency** - fully standalone

---

## 8. Recommendations for indus-agents

### Priority 1: Critical Gaps to Address

1. **Add Agency Class** for multi-agent orchestration
2. **Implement SendMessageHandoff** for agent-to-agent communication
3. **Add communication_flows** pattern
4. **Create agent factory pattern** with templates

### Priority 2: Tool System Enhancements

1. **Add Bash tool** with timeout and security
2. **Add Git tool** for version control
3. **Add Glob/Grep** for code search
4. **Add Edit/Write** with safety checks
5. **Add TodoWrite** for task tracking

### Priority 3: Infrastructure Improvements

1. **Implement hook system** for lifecycle management
2. **Add instruction template system** with placeholders
3. **Support model-specific instructions**
4. **Add shared context/state** across agents

---

## 9. Migration Path

To transform indus-agents into an Agency Swarm-like framework:

```
Phase 1: Foundation (Week 1)
├── Add BaseTool class (Pydantic-based)
├── Create core dev tools (Bash, Read, Edit, Write)
├── Implement template rendering
└── Add create-agent CLI command

Phase 2: Multi-Agent (Week 2)
├── Implement Agency class
├── Add handoff mechanism
├── Create communication flow system
└── Build shared state management

Phase 3: Enhancements (Week 3)
├── Add remaining tools (Git, Glob, Grep)
├── Implement hooks system
├── Add TodoWrite for task management
└── Create project scaffolding

Phase 4: Polish (Week 4)
├── Add YAML configuration
├── Create comprehensive documentation
├── Add tests
└── Create example agencies
```

---

## 10. Conclusion

**Agency-Code** provides a mature multi-agent framework with sophisticated agent collaboration, comprehensive development tools, and production-ready features. It excels at complex software engineering tasks requiring multiple specialized agents.

**indus-agents** offers a clean, standalone implementation with excellent CLI, memory management, and type safety. It's simpler to understand and extend but lacks true multi-agent capabilities.

**Recommendation:** Enhance indus-agents with Agency Swarm patterns to combine the best of both worlds - the clean architecture and professional CLI of indus-agents with the multi-agent collaboration capabilities of Agency-Code.
