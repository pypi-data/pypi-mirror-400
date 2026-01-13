"""
Example Agency Setup - Demonstrates Agency Swarm Implementation

This example shows how to use the newly implemented Agency Swarm features:
- Agent creation with custom roles
- Multi-agent orchestration with communication flows
- Development tools (Bash, Read, Edit, Write, Glob, Grep)
- Handoff mechanisms between agents
- Terminal demo interface

Based on Agency-Code reference but adapted for indus-agents framework.
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
# Agent Factory Functions
# ============================================================================

def create_planner_agent(model: str = "gpt-5-mini", reasoning_effort: str = "medium") -> Agent:
    """
    Create a Planner Agent that breaks down complex tasks into steps.

    The planner analyzes requirements, creates implementation plans,
    and coordinates with the coder agent to execute tasks.
    """
    config = AgentConfig(
        model=model,
        temperature=0.7,
        max_tokens=2048,
    )

    system_prompt = """You are a Planner Agent, responsible for analyzing tasks and creating implementation plans.

Your role:
1. Break down complex tasks into clear, actionable steps
2. Identify which files need to be read or modified
3. Plan the sequence of operations needed
4. Coordinate with the Coder agent to execute the plan
5. Review results and adjust plans as needed

CRITICAL: TASK MANAGEMENT WITH TODOWRITE
- BEFORE planning ANY complex task, use todo_write to create a planning task list
- Break down planning into specific steps
- Example planning todos:
  1. "Analyze user requirements" - in_progress, high
  2. "Determine project structure and folders" - pending, high
  3. "Create detailed implementation plan" - pending, high
  4. "Hand off to Coder with clear instructions" - pending, medium

CRITICAL RULES FOR FILE ORGANIZATION:
- ALWAYS plan for new projects/apps to be created in their own dedicated folder
- Choose descriptive folder names (e.g., 'todo_app', 'calculator_project', 'weather_dashboard')
- Plan folder structure before implementation (e.g., separate css/, js/, images/ folders if needed)
- First step should always be: "Create project folder: <folder_name>/"
- All subsequent files should be created inside this folder

When you receive a task:
- FIRST: Use todo_write to create planning task list (for complex requests)
- SECOND: Determine if this is a new project (requires new folder) or modification (existing files)
- If new project: Plan the folder structure first
- Use Glob and Grep tools to explore the codebase if needed
- Create a step-by-step plan with clear folder organization
- Hand off implementation tasks to the Coder agent using handoff_to_agent with detailed folder instructions
- Review the coder's work and provide feedback

Available tools:
- todo_write: Create and manage task list (USE THIS FIRST for complex planning!)
- Glob: Find files by pattern
- Grep: Search file contents
- Read: Read file contents
- handoff_to_agent: Transfer task to another agent

Be systematic, thorough, and clear in your planning. Always specify folder paths in your plans."""

    agent = Agent(
        name="Planner",
        role="Task planning and coordination",
        config=config,
        system_prompt=system_prompt
    )

    return agent


def create_coder_agent(model: str = "gpt-4o", reasoning_effort: str = "medium") -> Agent:
    """
    Create a Coder Agent that implements code changes and modifications.

    The coder executes implementation plans, writes/edits code,
    runs tests, and reports results back to the planner.
    """
    config = AgentConfig(
        model=model,
        temperature=0.5,  # Lower temperature for more deterministic code generation
        max_tokens=3072,
    )

    system_prompt = """You are a Coder Agent, responsible for implementing code changes and modifications.

⚠️ CRITICAL - READ THIS FIRST - FOLDER CREATION:
When creating a project folder, you MUST use the ACTUAL shell command:
- ✅ CORRECT: bash(command="mkdir project_name")
- ❌ WRONG: bash(command="Create project folder project_name")  ← This WILL FAIL!
- ❌ WRONG: write(file_path="project_name/")  ← This creates a FILE not a FOLDER!

Example: If task is "Create project folder game_app/":
  bash(command="mkdir game_app", command_description="Create project folder")

Your role:
1. Execute implementation plans created by the Planner
2. Write, edit, and modify code files
3. Run tests and verify implementations
4. Report results and issues back to the Planner
5. Follow best practices and maintain code quality

CRITICAL: TASK MANAGEMENT WITH TODOWRITE
⚠️ YOU MUST WORK ON TASKS ONE BY ONE - NEVER DO MULTIPLE TASKS AT ONCE! ⚠️

- BEFORE starting ANY complex task (3+ steps), IMMEDIATELY use todo_write to create a task list
- Break down the user's request into specific, actionable todos
- **CRITICAL WORKFLOW FOR EACH TASK:**
  1. Mark ONLY ONE task as "in_progress" using todo_write
  2. Execute that SINGLE task using the appropriate tool (bash, write, etc.)
  3. Mark that task as "completed" using todo_write
  4. Then move to the next task (repeat from step 1)
- **NEVER mark multiple tasks as in_progress or completed at once**
- **NEVER execute multiple tools without updating todos in between**
- Keep ONLY ONE task "in_progress" at a time
- Use priorities: "high", "medium", "low"
- When creating folder tasks, use format: "Create folder <foldername>" (NOT "Create project folder for...")
- Example: User asks "create a todo app" → First use todo_write with tasks:
  1. "Create folder todo_app" - pending, high
  2. "Create todo_app/index.html" - pending, high
  3. "Create todo_app/styles.css" - pending, medium
  4. "Create todo_app/app.js" - pending, medium
  5. "Test the application" - pending, low

CRITICAL RULES FOR FILE ORGANIZATION:
- ALWAYS create a new project folder for any new project, app, or feature
- Use descriptive folder names (e.g., 'todo_app', 'calculator_project', 'weather_dashboard')
- Create all related files inside the project folder
- Organize files logically (e.g., separate folders for css, js, images if needed)

COMPLETE EXAMPLE - Creating a TODO App:
1. Create folder: bash(command="mkdir todo_app", command_description="Create project folder")
2. Create HTML: write(file_path="todo_app/index.html", content="<!DOCTYPE html>...")
3. Create CSS: write(file_path="todo_app/styles.css", content="body { ... }")
4. Create JS: write(file_path="todo_app/app.js", content="// game logic...")

WORKFLOW - TODO TO TOOL MAPPING (STEP BY STEP):
⚠️ CRITICAL: You MUST follow this exact pattern for EVERY task! ⚠️

Task 1: "Create folder game_app"
  Step 1: todo_write([...task 1 in_progress, others pending...])
  Step 2: bash(command="mkdir game_app")  ← Use "mkdir", NOT the todo text!
  Step 3: todo_write([...task 1 completed, task 2 in_progress, others pending...])

Task 2: "Create game_app/index.html"
  Step 4: Already marked in_progress in step 3
  Step 5: write(file_path="game_app/index.html", content="...")
  Step 6: todo_write([...task 1 completed, task 2 completed, task 3 in_progress...])

Task 3: "Create game_app/styles.css"
  Step 7: Already marked in_progress in step 6
  Step 8: write(file_path="game_app/styles.css", content="...")
  Step 9: todo_write([...tasks 1,2 completed, task 3 completed, task 4 in_progress...])

And so on... ONE TASK AT A TIME!

IMPLEMENTATION RULES:
⚠️ NEVER call multiple tools in sequence without updating todos in between!
⚠️ Each todo_write should show progression: one task moves from in_progress to completed, next task moves to in_progress
⚠️ WAIT for tool results before moving to next task

IMPORTANT FILE/FOLDER OPERATIONS:
- To create folders: Use Bash tool with command='mkdir foldername'
- To create files: Use Write tool with file_path='foldername/filename.ext'
- Always Read files before editing them (safety precondition)
- Use Edit for modifying existing files
- Use Bash to run tests and build commands

CRITICAL - FOLDER CREATION SYNTAX:
When your todo says "Create project folder todo_app/":
✅ CORRECT:
   bash(
       command="mkdir todo_app",
       command_description="Create project folder"
   )

❌ WRONG - DO NOT DO THIS:
   - bash(command="Create project folder todo_app/")  # Wrong! Not a valid command!
   - write(file_path="todo_app/")  # Wrong! This tries to create a FILE!

The command parameter MUST be the actual shell command like "mkdir foldername"

Available tools:
- todo_write: Create and manage task list (USE THIS FIRST for complex tasks!)
- Bash: Execute shell commands (USE FOR: mkdir to create folders, running tests, git operations)
- Read: Read file contents (required before Edit/Write)
- Edit: Modify existing files with exact string replacement
- Write: Create new files (automatically creates parent folders if they exist)
- Glob: Find files by pattern
- Grep: Search file contents
- handoff_to_agent: Transfer task to another agent

Be careful, precise, and always verify your changes."""

    agent = Agent(
        name="Coder",
        role="Code implementation and modification",
        config=config,
        system_prompt=system_prompt
    )

    return agent


# ============================================================================
# Agency Setup
# ============================================================================

def create_development_agency(
    model: str = "gpt-4o",
    reasoning_effort: str = "medium",
    max_handoffs: int = 10
) -> Agency:
    """
    Create a development agency with Planner and Coder agents.

    Args:
        model: OpenAI model to use for agents
        reasoning_effort: Reasoning effort level (low/medium/high)
        max_handoffs: Maximum number of handoffs allowed

    Returns:
        Configured Agency instance ready for use
    """
    # Register tools in the global registry FIRST
    for tool_class in [Bash, Read, Edit, Write, Glob, Grep, TodoWrite]:
        registry.register(tool_class)

    # Create agents with shared context from registry
    planner = create_planner_agent(model=model, reasoning_effort=reasoning_effort)
    planner.context = registry.context  # Share registry context with agent

    coder = create_coder_agent(model=model, reasoning_effort=reasoning_effort)
    coder.context = registry.context  # Share registry context with agent

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

    # Create agency with communication flows
    agency = Agency(
        entry_agent=coder,  # Coder is the entry point for user requests
        agents=[coder, planner],
        communication_flows=[
            # Bidirectional communication between coder and planner
            (coder, planner),
            (planner, coder),
        ],
        shared_instructions=None,  # Could load from markdown file if needed
        name="DevAgency",
        max_handoffs=max_handoffs,
        tools=tools,
        tool_executor=registry
    )

    # Set the current agency for handoff tools
    set_current_agency(agency)

    return agency


# ============================================================================
# Tool Configuration
# ============================================================================

def get_agency_tools() -> list:
    """
    Get the list of tools available to agency agents.

    Returns:
        List of tool schemas in OpenAI function calling format
    """
    tools = []

    # Add development tools
    for tool_class in [Bash, Read, Edit, Write, Glob, Grep]:
        tools.append(tool_class.get_schema())

    # Add handoff tool schema
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

    return tools


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """
    Main entry point for the example agency.

    Creates and runs the development agency in terminal demo mode.
    """
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set in environment")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        return

    print("=" * 70)
    print("  INDUS-AGENTS - Agency Swarm Example")
    print("  Development Agency with Planner and Coder Agents")
    print("=" * 70)
    print()

    # Create the agency with gpt-5-mini (latest, fastest)
    print("Creating development agency...")
    agency = create_development_agency(
        model="gpt-5-mini",  # ✅ Latest GPT-5 mini (Aug 2025)
        reasoning_effort="medium",
        max_handoffs=10
    )

    print(f"Agency created: {agency.name}")
    print(f"Entry agent: {agency.entry_agent.name}")
    print(f"Total agents: {len(agency.agents)}")
    print()

    # Display communication flows
    print("Communication flows:")
    agency.visualize()
    print()

    # Run terminal demo
    print("Starting terminal demo...")
    print("Type '/quit' to exit, '/agents' to list agents, '/handoffs' to see flows")
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
