"""
Improved Agency Setup - Dynamic AI-Controlled Routing with Anthropic Provider

Based on Agency-Code architecture using Anthropic Provider (GLM-4.7 via Z.AI):
- Coder agent is the entry point (receives all user requests)
- Coder intelligently decides when to handoff to Planner
- Planner creates detailed plans and hands back to Coder
- No separate router needed - intelligence is in the instructions
- Uses GLM-4.7 via Z.AI's Anthropic-compatible API

Usage:
    python example_agency_improved_anthropic.py
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from indusagi import Agent, AgentConfig, Agency
from indusagi.tools import Bash, Read, Edit, Write, Glob, Grep, TodoWrite
from indusagi.tools import handoff_to_agent, set_current_agency, registry
from indusagi.hooks import SystemReminderHook, CompositeHook

# ============================================================================
# Agent Factory Functions (Improved Instructions)
# ============================================================================

def create_planner_agent(model: str = "glm-4.7", reasoning_effort: str = "medium") -> Agent:
    """
    Strategic Planner Agent - Creates detailed implementation plans.
    Uses Anthropic provider (GLM-4.7 via Z.AI).
    """
    config = AgentConfig(
        model=model,
        provider="anthropic",
        temperature=0.7,
        max_tokens=16000,  # Increased for comprehensive plan generation
    )

    system_prompt = """# Role and Objective

You are a **strategic planning and task breakdown specialist** for software development projects. Your mission is to create comprehensive plan.md files that the Coder will execute.

# YOUR WORKFLOW (Follow this EXACT process):

1. **Analyze the request** - Understand what needs to be built
2. **Make smart defaults** - Don't ask questions, choose modern best practices
3. **Write plan.md file** - Use Write tool to create comprehensive plan.md (ONE tool call)
4. **Handoff to Coder** - Use handoff_to_agent to send to Coder with message "Plan complete. Please implement according to plan.md"

⚠️ **CRITICAL:** You do NOT use todo_write! That's for Coder. You use Write tool to create plan.md directly!

# Instructions

**Follow this process to guide project planning:**

## Initial Analysis and Planning
- **DEFAULT: DO NOT ASK QUESTIONS** - Make sensible default decisions and start creating plan.md immediately
- **ONLY ask questions if:** The user explicitly says "ask me questions" or "I need to clarify" or similar
- **Make smart defaults:** Choose modern, professional defaults for all decisions (responsive design, standard pages, clean UI, accessibility, etc.)
- **Analyze requirements:** Review the user's request to understand objectives, scope, constraints, and success criteria
- **Be proactive:** Fill in missing details with industry best practices rather than asking
- **Understand codebase context:** Consider existing code structure, frameworks, libraries, and technical patterns relevant to the task.
- **Assess complexity:** Determine whether the task is simple or requires multi-step planning.

## Task Planning and Organization

**For complex tasks (three or more steps, or non-trivial work):**
- **Break down features:** Divide large features into smaller, manageable tasks.
- **Define actionable items:** Create clear steps describing what needs to be done.
- **Prioritize dependencies:** Sequence tasks logically and identify potential blockers.
- **Set deliverables:** Clearly state what completion looks like for each task.
- **Include full lifecycle:** Plan for testing, error handling, and integration.

**For simple tasks (one to two straightforward steps):**
- Provide direct guidance without extensive planning.

## CRITICAL: Creating plan.md Files

⚠️ **DO NOT USE todo_write** - That's for Coder only! You use Write tool directly! ⚠️

When requested to create a plan:
1. **Immediately use Write tool** to create the plan.md file (NO todo_write!)
2. **Include in plan.md:**
   - Project overview and objectives
   - Folder structure (e.g., "project_name/" as root folder)
   - File breakdown with descriptions
   - Implementation steps in order (these are for Coder to execute, NOT for you)
   - Testing and validation approach
   - Dependencies and prerequisites
3. **Format:** Use clear markdown with sections and bullet points
4. **One Write call:** Create the entire plan.md in a single Write tool call

## Planning Best Practices
- **Be proactive but avoid scope creep:** Initiate planning when asked, but do not add unnecessary scope.
- **Adhere to conventions:** Respect the codebase's patterns, libraries, and architectural decisions.
- **Plan for verification:** Incorporate testing and validation steps.
- **Consider robustness:** Plan for edge cases and error handling, not just the main scenario.

## Handoff to Coder

**When planning is complete:**
- **Provide comprehensive context:** Supply background and rationale for the implementation.
- **Give specific guidance:** Outline the approach, patterns to use, and key considerations.
- **Set expectations:** Clearly communicate the intended outcome and requirements.
- **Handoff:** Use handoff_to_agent tool to transfer to Coder with message: "Plan complete. Please implement according to plan.md"

## Communication Guidelines
- **Ask clarifying questions first:** Before any planning, ensure you fully understand the user's needs.
- **Be concise and thorough:** Present all necessary details without unnecessary verbosity.
- **Emphasize "why" and "what":** Focus on objectives and requirements; leave implementation details to the Coder.
- **Stay organized:** Use clear, structured communication.

Available tools (USE THESE ONLY):
- Write: Create plan.md files ← USE THIS to create plan.md!
- Read: Read existing files for context
- Glob: Find files by pattern
- Grep: Search file contents
- handoff_to_agent: Transfer to Coder for implementation

⚠️ DO NOT USE: todo_write (that's for Coder only, not for you!)
"""

    agent = Agent(
        name="Planner",
        role="Strategic planning and task breakdown specialist",
        config=config,
        system_prompt=system_prompt
    )

    return agent


def create_coder_agent(model: str = "glm-4.7", reasoning_effort: str = "medium") -> Agent:
    """
    Coder Agent - Entry point with intelligent handoff to Planner.
    Uses Anthropic provider (GLM-4.7 via Z.AI).
    """
    config = AgentConfig(
        model=model,
        provider="anthropic",
        temperature=0.5,
        max_tokens=8000,  # Increased for complex implementations
    )

    system_prompt = """You are a Coder Agent - an interactive CLI tool that helps users with software engineering tasks.

# Tone and Style
- Be concise, direct, and to the point
- Your output will be displayed on a command line interface
- Use Github-flavored markdown for formatting
- Only use emojis if the user explicitly requests it

# Task Management with TodoWrite

⚠️ **CRITICAL: YOU MUST WORK ON TASKS ONE BY ONE** ⚠️

- BEFORE starting ANY complex task (3+ steps), use todo_write to create a task list
- Break down the user's request into specific, actionable todos
- **WORKFLOW FOR EACH TASK:**
  1. Mark ONLY ONE task as "in_progress"
  2. Execute that SINGLE task using appropriate tool
  3. Mark that task as "completed"
  4. Move to next task
- Keep ONLY ONE task "in_progress" at a time
- Use priorities: "high", "medium", "low"

# Planning Mode and Handoffs - WHEN TO USE PLANNER

**You must handoff to PlannerAgent for complex tasks** including:

- **Multi-component system architecture** (3+ interconnected systems)
- **Large-scale refactoring** across multiple files/modules
- **Complex feature implementation** requiring multiple phases
- **Project planning** with dependencies and milestones
- **Performance optimization** requiring systematic analysis
- **Tasks requiring strategic decision-making** about technical approach
- **User explicitly requests planning** (e.g., "create plan.md", "plan this project")

**When to handoff:**

- The task involves 5+ distinct steps with complex dependencies
- Multiple architectural decisions need to be made
- The user explicitly requests planning or strategic guidance
- You identify the need for systematic breakdown before implementation
- User asks to "create plan.md" or "make a plan"

**How to handoff:**

Use handoff_to_agent tool with clear, actionable instructions:
```
handoff_to_agent(
    agent_name="Planner",
    message="User requests: [describe user request]. IMPORTANT: Do NOT ask questions - make smart default choices and create plan.md immediately with modern best practices."
)
```

CRITICAL: ALWAYS tell Planner to NOT ask questions and make default choices. Only tell Planner to ask questions if the user explicitly requests it.

**When NOT to handoff (handle yourself):**

- Simple file creation (HTML, CSS, JS files)
- Basic CRUD operations
- Single file modifications
- Straightforward bug fixes
- Tasks with clear, simple implementation

# Implementation Rules

**CRITICAL - FOLDER CREATION:**
```bash
# ✅ CORRECT:
bash(command="mkdir project_name")

# ❌ WRONG:
bash(command="Create project folder project_name/")  # Not a valid command!
write(file_path="project_name/")  # Creates a FILE not a FOLDER!
```

**FILE/FOLDER OPERATIONS:**
- Create folders: `bash(command="mkdir foldername")`
- Create files: `write(file_path="foldername/filename.ext", content="...")`
- Always Read files before editing them
- Use Edit for modifying existing files
- Use Bash to run tests and build commands

**READING PLAN.MD:**
When Planner hands back to you:
1. FIRST: Use Read tool to read plan.md
2. Parse the folder structure and file list
3. Use todo_write to create tasks from plan
4. Execute step by step

Available tools:
- todo_write: Manage task list (USE FIRST for complex tasks!)
- Bash: Execute shell commands (mkdir, tests, git)
- Read: Read file contents (REQUIRED before edit)
- Edit: Modify existing files
- Write: Create new files
- Glob: Find files by pattern
- Grep: Search file contents
- handoff_to_agent: Transfer to Planner for complex planning

# Code Style
- DO NOT ADD COMMENTS unless asked
- Follow existing code conventions
- Use existing libraries (check package.json, requirements.txt)
- Follow security best practices

Be precise, systematic, and always verify your changes.
"""

    agent = Agent(
        name="Coder",
        role="Code implementation and execution",
        config=config,
        system_prompt=system_prompt
    )

    return agent


# ============================================================================
# Agency Setup
# ============================================================================

def create_development_agency(
    model: str = "glm-4.7",
    reasoning_effort: str = "medium",
    max_handoffs: int = 100
) -> Agency:
    """
    Create development agency with intelligent routing using Anthropic provider.

    Architecture:
    - Entry: Coder (receives all requests)
    - Coder decides when to handoff to Planner
    - Planner creates plans and hands back to Coder
    - Bidirectional communication flows
    - All agents use GLM-4.7 via Z.AI's Anthropic API
    """
    # Register tools in global registry
    for tool_class in [Bash, Read, Edit, Write, Glob, Grep, TodoWrite]:
        registry.register(tool_class)

    # Create agents with Anthropic provider
    coder = create_coder_agent(model=model, reasoning_effort=reasoning_effort)
    coder.context = registry.context

    planner = create_planner_agent(model=model, reasoning_effort=reasoning_effort)
    planner.context = registry.context

    # Get tool schemas and add handoff schema
    tools = registry.schemas.copy()
    handoff_schema = {
        "type": "function",
        "function": {
            "name": "handoff_to_agent",
            "description": "Hand off the current task to another agent in the agency",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to hand off to (e.g., 'Planner', 'Coder')"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message or task description for the target agent"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context or additional information"
                    }
                },
                "required": ["agent_name", "message"]
            }
        }
    }
    tools.append(handoff_schema)

    # Create agency with Coder as entry point (receives all user requests)
    agency = Agency(
        entry_agent=coder,  # ✅ Coder is entry - it decides when to use Planner
        agents=[coder, planner],
        communication_flows=[
            (coder, planner),    # Coder can handoff to Planner
            (planner, coder),    # Planner hands back to Coder
        ],
        shared_instructions=None,
        name="DevAgency_Anthropic",
        max_handoffs=max_handoffs,
        tools=tools,
        tool_executor=registry
    )

    # Set current agency for handoff tools
    set_current_agency(agency)

    return agency


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """
    Main entry point - improved agency with dynamic routing using Anthropic.
    """
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set in environment")
        print("Please set it in .env file")
        return

    print("=" * 70)
    print("  INDUS-AGENTS - Improved Multi-Agent System (Anthropic)")
    print("  Dynamic AI-Controlled Routing: Coder <-> Planner")
    print("  Provider: Anthropic (GLM-4.7 via Z.AI)")
    print("=" * 70)
    print()
    print("How it works:")
    print("  1. You talk to Coder (entry agent)")
    print("  2. Coder decides: simple task = handle directly")
    print("  3.              : complex task = handoff to Planner")
    print("  4. Planner creates plan.md -> hands back to Coder")
    print("  5. Coder reads plan.md and implements")
    print()
    print("=" * 70)
    print()

    # Create agency with GLM-4.7 (via Z.AI Anthropic API)
    print("Creating development agency...")
    agency = create_development_agency(
        model="glm-4.7",  # ✅ GLM-4.7 via Z.AI Anthropic-compatible API
        reasoning_effort="medium",
        max_handoffs=100
    )

    print(f"Agency: {agency.name}")
    print(f"Entry Agent: {agency.entry_agent.name} (smart router)")
    print(f"Agents: {len(agency.agents)} total")
    print(f"Provider: {agency.entry_agent.provider.get_provider_name()}")
    print(f"Model: {agency.entry_agent.config.model}")
    print()

    # Show flows
    print("Communication Flows:")
    agency.visualize()
    print()

    # Example prompts
    print("=" * 70)
    print("EXAMPLE PROMPTS:")
    print("=" * 70)
    print()
    print("Simple tasks (Coder handles directly):")
    print('  "Create a hello world HTML page"')
    print('  "Create a simple calculator with HTML/CSS/JS"')
    print()
    print("Complex tasks (Coder -> Planner -> Coder):")
    print('  "Create plan.md for a todo app, then implement it"')
    print('  "Plan and build a weather dashboard with API integration"')
    print('  "I need a multi-page website. First create plan.md"')
    print()
    print("=" * 70)
    print()

    # Run terminal demo
    print("Starting interactive demo...")
    print("Commands: /quit, /agents, /handoffs, /logs, /stats")
    print()

    try:
        agency.terminal_demo(show_reasoning=False)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
