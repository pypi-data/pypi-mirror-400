"""
TodoWrite Tool - Task management and tracking.

Adapted from Agency-Code for indus-agents framework.
"""
from datetime import datetime
from typing import List, ClassVar, Literal
from pydantic import BaseModel, Field
from indusagi.tools.base import BaseTool


class TodoItem(BaseModel):
    """Individual todo item with status and priority."""

    task: str = Field(
        ...,
        min_length=1,
        description="The human-readable task description. Required parameter."
    )
    status: Literal["pending", "in_progress", "completed"] = Field(
        ...,
        description="The status of the todo item. Required parameter."
    )
    priority: Literal["high", "medium", "low"] = Field(
        "medium",
        description="The priority of the todo item. Defaults to 'medium'"
    )


class TodoWrite(BaseTool):
    """
    Create and manage a structured task list for your current coding session.

    This helps you track progress, organize complex tasks, and demonstrate
    thoroughness to the user. It also helps the user understand the progress
    of the task and overall progress of their requests.

    ## When to Use This Tool
    Use this tool proactively in these scenarios:
    1. Complex multi-step tasks - When a task requires 3 or more distinct steps or actions
    2. Non-trivial and complex tasks - Tasks that require careful planning or multiple operations
    3. User explicitly requests todo list - When the user directly asks you to use the todo list
    4. User provides multiple tasks - When users provide a list of things to be done (numbered or comma-separated)
    5. After receiving new instructions - Immediately capture user requirements as todos
    6. When you start working on a task - Mark it as in_progress BEFORE beginning work. Ideally you should only have one todo as in_progress at a time
    7. After completing a task - Mark it as completed and add any new follow-up tasks discovered during implementation

    ## When NOT to Use This Tool
    Skip using this tool when:
    1. There is only a single, straightforward task
    2. The task is trivial and tracking it provides no organizational benefit
    3. The task can be completed in less than 3 trivial steps
    4. The task is purely conversational or informational

    ## Task States and Management
    1. **Task States**: Use these states to track progress:
       - pending: Task not yet started
       - in_progress: Currently working on (limit to ONE task at a time)
       - completed: Task finished successfully

    2. **Task Management**:
       - Update task status in real-time as you work
       - Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
       - Only have ONE task in_progress at any time
       - Complete current tasks before starting new ones
       - Remove tasks that are no longer relevant from the list entirely

    3. **Task Completion Requirements**:
       - ONLY mark a task as completed when you have FULLY accomplished it
       - If you encounter errors, blockers, or cannot finish, keep the task as in_progress
       - When blocked, create a new task describing what needs to be resolved
       - Never mark a task as completed if:
         - Tests are failing
         - Implementation is partial
         - You encountered unresolved errors
         - You couldn't find necessary files or dependencies

    4. **Task Breakdown**:
       - Create specific, actionable items
       - Break complex tasks into smaller, manageable steps
       - Use clear, descriptive task names

    When in doubt, use this tool. Being proactive with task management demonstrates
    attentiveness and ensures you complete all requirements successfully.
    """

    name: ClassVar[str] = "todo_write"
    description: ClassVar[str] = """Manage task list for tracking progress.

Use this tool to create and update todos for complex multi-step tasks.
IMPORTANT: Use this BEFORE starting any non-trivial task (3+ steps).
Mark tasks as in_progress when starting, completed when done."""

    todos: List[TodoItem] = Field(..., description="The updated todo list")

    def execute(self) -> str:
        """Execute the todo write operation."""
        try:
            # Validate that only one task is in_progress
            in_progress_tasks = [
                todo for todo in self.todos if todo.status == "in_progress"
            ]
            if len(in_progress_tasks) > 1:
                return f"Error: Only one task can be 'in_progress' at a time. Found {len(in_progress_tasks)} tasks in progress."

            # Add timestamp
            current_time = datetime.now().isoformat()

            # Convert todos to dict format for storage
            todos_payload = [todo.model_dump() for todo in self.todos]

            # Store in tool context
            self.context.set("todos", todos_payload)
            self.context.set("todos_updated", current_time)

            # Format the response
            total_tasks = len(self.todos)
            completed_tasks = len([t for t in self.todos if t.status == "completed"])
            in_progress_tasks_count = len(
                [t for t in self.todos if t.status == "in_progress"]
            )
            pending_tasks = len([t for t in self.todos if t.status == "pending"])

            result = f"Todo List Updated ({current_time[:19]})\n"
            result += f"Summary: total={total_tasks}, done={completed_tasks}, in_progress={in_progress_tasks_count}, pending={pending_tasks}\n"

            # Group tasks by status
            status_groups = {"in_progress": [], "pending": [], "completed": []}

            for todo in self.todos:
                status_groups[todo.status].append(todo)

            # Display in_progress tasks first
            if status_groups["in_progress"]:
                result += "\nIN PROGRESS:\n"
                for todo in status_groups["in_progress"]:
                    result += f"  [{todo.priority.upper()}] {todo.task}\n"

            # Display pending tasks
            if status_groups["pending"]:
                result += "\nPENDING:\n"
                for todo in status_groups["pending"]:
                    result += f"  [{todo.priority.upper()}] {todo.task}\n"

            # Display completed tasks (limit to last 5 to avoid clutter)
            if status_groups["completed"]:
                completed_to_show = status_groups["completed"][
                    -5:
                ]  # Show last 5 completed
                result += f"\nCOMPLETED (showing last {len(completed_to_show)}):\n"
                for todo in completed_to_show:
                    result += f"  [{todo.priority.upper()}] {todo.task}\n"

                if len(status_groups["completed"]) > 5:
                    result += f"  ... and {len(status_groups['completed']) - 5} more completed tasks\n"

            # Add usage tips
            result += "\nTips:\n"
            result += "  - Keep only ONE task 'in_progress' at a time\n"
            result += "  - Mark tasks 'completed' immediately after finishing\n"
            result += "  - Break complex tasks into smaller, actionable steps\n"

            return result.strip()

        except Exception as e:
            return f"Error managing todo list: {str(e)}"
