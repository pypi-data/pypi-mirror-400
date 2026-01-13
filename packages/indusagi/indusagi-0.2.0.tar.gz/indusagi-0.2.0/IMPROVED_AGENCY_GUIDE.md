# Improved Multi-Agent System - User Guide

## How It Works (Based on Agency-Code Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  CODER AGENT  │ ◄─── Entry Point
                    │   (Smart AI)  │
                    └───────┬───────┘
                            │
                ┌───────────┴───────────┐
                │   AI Decision Engine   │
                └───────────┬───────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
    SIMPLE TASK       COMPLEX TASK      PLANNING REQUEST
    Handle directly   → Handoff to      → Handoff to
                        Planner           Planner
          │                 │                 │
          │                 ▼                 ▼
          │         ┌───────────────┐ ┌───────────────┐
          │         │ PLANNER AGENT │ │ PLANNER AGENT │
          │         │ Analyze task  │ │ Create plan.md│
          │         └───────┬───────┘ └───────┬───────┘
          │                 │                 │
          │                 ▼                 ▼
          │         Handoff back      Handoff back
          │         to CODER          to CODER
          │                 │                 │
          │                 ▼                 ▼
          │         Read plan.md      Read plan.md
          │         Implement         Implement
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    RESULT     │
                    └───────────────┘
```

## Key Features

### 1. **Dynamic AI-Controlled Routing**
- No manual agent selection needed
- Coder agent intelligently decides when to use Planner
- Based on task complexity analysis

### 2. **Smart Handoff Criteria (Built into Coder)**

**Coder → Planner handoff happens when:**
- Task requires 5+ steps with dependencies
- Multi-component architecture needed
- User explicitly requests planning ("create plan.md")
- Large-scale refactoring
- Strategic decision-making required

**Coder handles directly when:**
- Simple file creation
- Basic CRUD operations
- Single file modifications
- Straightforward implementations

### 3. **Bidirectional Communication**
```
Coder ←→ Planner
```
- Both agents can handoff to each other
- Seamless collaboration

## Usage

### Running the Improved Agency

```bash
python example_agency_improved.py
```

### Example Prompts

#### 1. Simple Task (Coder handles)

**Input:**
```
Create a simple HTML page with a button
```

**Flow:**
```
User → Coder → Creates file directly → Done
```

---

#### 2. Planning Request (Coder → Planner → Coder)

**Input:**
```
Create plan.md for a todo list web application, then implement it
```

**Flow:**
```
User → Coder (receives request)
     → Coder (detects "plan.md" keyword)
     → Handoff to Planner
     → Planner (creates detailed plan.md)
     → Handoff back to Coder
     → Coder (reads plan.md)
     → Coder (implements according to plan)
     → Done
```

**What Planner creates in plan.md:**
```markdown
# Todo List Application - Implementation Plan

## Project Overview
Simple todo list web app with add, delete, mark complete functionality

## Folder Structure
```
todo_app/
├── index.html
├── styles.css
└── app.js
```

## Files to Create

### 1. index.html
- Basic HTML5 structure
- Input field for new todos
- Todo list container
- Buttons for add/delete

### 2. styles.css
- Modern, clean design
- Responsive layout
- Button hover effects

### 3. app.js
- addTodo() function
- deleteTodo() function
- toggleComplete() function
- localStorage persistence

## Implementation Steps
1. Create todo_app folder
2. Create index.html with structure
3. Create styles.css with styling
4. Create app.js with logic
5. Test functionality
```

---

#### 3. Complex Task (Coder → Planner → Coder)

**Input:**
```
Build a weather dashboard with API integration. Include current weather,
5-day forecast, and location search.
```

**Flow:**
```
User → Coder (receives complex request)
     → Coder (analyzes: multi-component, API integration, complex)
     → Handoff to Planner
     → Planner (creates strategic plan)
     → Handoff back to Coder
     → Coder (implements step by step)
     → Done
```

---

#### 4. Explicit Planner Request

**Input:**
```
Use planner subagent to create plan.md for an e-commerce site
```

**Flow:**
```
User → Coder (detects explicit planner request)
     → Immediate handoff to Planner
     → Planner (creates comprehensive plan.md)
     → Handoff back to Coder
     → Coder asks: "Should I implement this plan?"
```

## Comparison: Old vs Improved

### ❌ Old Approach (Manual Routing)
```python
# User had to manually specify which agent
"Planner: create a plan"
"Coder: implement the code"
```
- Manual agent selection
- User needs to understand agent roles
- Prone to mistakes

### ✅ Improved Approach (AI-Controlled)
```python
# User just describes the task
"Create a todo app with plan.md first"
```
- AI decides routing automatically
- User focuses on task, not architecture
- Follows Agency-Code best practices

## Testing the System

### Test 1: Simple Task
```
You: Create a hello world HTML file

Expected: Coder handles directly (no handoff)
```

### Test 2: Plan Request
```
You: Create plan.md for a calculator app, then build it

Expected:
1. Coder → Planner handoff
2. Planner creates plan.md
3. Planner → Coder handoff
4. Coder reads plan.md
5. Coder implements
```

### Test 3: Complex Task
```
You: Build a real-time chat application with user authentication,
     message persistence, and typing indicators

Expected:
1. Coder detects complexity
2. Coder → Planner handoff
3. Planner breaks down into phases
4. Planner → Coder handoff with plan
5. Coder implements systematically
```

## Key Improvements Based on Agency-Code

### 1. Instructions-Based Intelligence
- Coder's system prompt has clear handoff criteria (lines 86-104 in Agency-Code)
- No separate router agent needed
- Intelligence is in the instructions

### 2. Entry Point Strategy
```python
Agency(
    entry_agent=coder,  # ✅ All requests go to Coder first
    # ...
)
```

### 3. Bidirectional Flows
```python
communication_flows=[
    (coder, planner),   # Coder can ask Planner for help
    (planner, coder),   # Planner hands back to Coder
]
```

### 4. Clear Role Separation

**Planner:**
- Strategic planning
- Task breakdown
- Create plan.md files
- No implementation

**Coder:**
- Receives all user requests
- Smart routing decisions
- Implementation
- File operations
- Testing

## Advanced Usage

### Forcing Planner Mode
```
You: I need strategic planning for [task]. Use Planner to create plan.md
```

### Checking Agent Activity
```
You: /agents     # List all agents
You: /handoffs   # Show communication flows
You: /logs       # Show recent tool usage
You: /stats      # Show statistics
```

### Debugging Handoffs
Watch the output to see:
```
[Coder] Handing off to Planner: Create plan for...
[Planner] Creating plan.md...
[Planner] Handing off to Coder: Plan complete, please implement
[Coder] Reading plan.md...
[Coder] Creating folder...
```

## Troubleshooting

### Issue: Coder doesn't handoff to Planner
**Solution:** Use explicit keywords:
- "create plan.md"
- "use planner"
- "strategic planning needed"

### Issue: Too many handoffs
**Solution:** Be more specific in initial request
```
❌ "Build something cool"
✅ "Create a calculator app with plan.md first"
```

### Issue: Plan.md not created
**Solution:** Check if Planner has Write tool access

## Best Practices

1. **For simple tasks:** Just describe what you want
2. **For complex tasks:** Mention "plan.md" or "planning"
3. **Trust the AI:** Let Coder decide routing
4. **Be specific:** Clear requirements = better plans
5. **Iterate:** Ask questions, refine plans

## Summary

This improved system follows Agency-Code's proven architecture:
- ✅ Single entry point (Coder)
- ✅ AI-controlled routing
- ✅ Dynamic handoffs based on complexity
- ✅ Clear role separation
- ✅ Bidirectional communication
- ✅ No manual agent selection needed

Just describe your task, and let the AI handle the rest!
