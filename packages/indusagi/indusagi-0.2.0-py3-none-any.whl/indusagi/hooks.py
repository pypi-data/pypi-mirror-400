"""
Hooks System - Lifecycle management for agents.

Provides hooks for intercepting agent execution at various points.
"""
from abc import ABC
from typing import Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class RunContext:
    """Context passed to hooks during agent execution."""
    agent_name: str
    shared_state: dict = field(default_factory=dict)
    messages: List[dict] = field(default_factory=list)
    tool_calls: int = 0
    pending_reminder: Optional[str] = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.shared_state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.shared_state[key] = value


class AgentHooks(ABC):
    """
    Base class for agent hooks.

    Hooks allow injecting custom behavior at various points:
    - on_start: When agent begins processing
    - on_end: When agent finishes processing
    - on_tool_start: Before each tool execution
    - on_tool_end: After each tool execution
    - on_handoff: When agent receives a handoff
    """

    async def on_start(self, context: RunContext, agent: Any) -> None:
        """Called when agent starts processing."""
        pass

    async def on_end(self, context: RunContext, agent: Any, output: str) -> None:
        """Called when agent finishes processing."""
        pass

    async def on_tool_start(self, context: RunContext, agent: Any, tool: Any) -> None:
        """Called before each tool execution."""
        pass

    async def on_tool_end(
        self, context: RunContext, agent: Any, tool: Any, result: str
    ) -> None:
        """Called after each tool execution."""
        pass

    async def on_handoff(
        self, context: RunContext, agent: Any, source: Any
    ) -> None:
        """Called when agent receives a handoff from another agent."""
        pass


class SystemReminderHook(AgentHooks):
    """
    Injects periodic system reminders.

    Triggers:
    - Every N tool calls (default: 15)
    - After each user message
    """

    def __init__(self, tool_call_interval: int = 15):
        self.tool_call_count = 0
        self.tool_call_interval = tool_call_interval

    async def on_start(self, context: RunContext, agent: Any) -> None:
        """Inject reminder at start."""
        self._inject_reminder(context, "start")

    async def on_tool_end(
        self, context: RunContext, agent: Any, tool: Any, result: str
    ) -> None:
        """Track tool calls and inject reminder periodically."""
        self.tool_call_count += 1
        context.tool_calls = self.tool_call_count

        if self.tool_call_count >= self.tool_call_interval:
            self._inject_reminder(context, "tool_limit")
            self.tool_call_count = 0

    def _inject_reminder(self, context: RunContext, trigger: str) -> None:
        """Build and inject a system reminder."""
        todos = context.get("todos", [])

        reminder = """<system-reminder>
# Important Reminders
- Complete the requested task fully
- Use tools appropriately (Read before Edit)
- Do not create unnecessary files
- Track progress with TodoWrite
"""

        if todos:
            pending = sum(1 for t in todos if t.get("status") == "pending")
            in_progress = sum(1 for t in todos if t.get("status") == "in_progress")
            completed = sum(1 for t in todos if t.get("status") == "completed")
            reminder += f"""
# TODO Status
- Pending: {pending}
- In Progress: {in_progress}
- Completed: {completed}
"""

        reminder += "</system-reminder>"
        context.pending_reminder = reminder


class CompositeHook(AgentHooks):
    """Combines multiple hooks into one."""

    def __init__(self, hooks: List[AgentHooks]):
        self.hooks = hooks

    async def on_start(self, context: RunContext, agent: Any) -> None:
        for hook in self.hooks:
            await hook.on_start(context, agent)

    async def on_end(self, context: RunContext, agent: Any, output: str) -> None:
        for hook in self.hooks:
            await hook.on_end(context, agent, output)

    async def on_tool_start(self, context: RunContext, agent: Any, tool: Any) -> None:
        for hook in self.hooks:
            await hook.on_tool_start(context, agent, tool)

    async def on_tool_end(
        self, context: RunContext, agent: Any, tool: Any, result: str
    ) -> None:
        for hook in self.hooks:
            await hook.on_tool_end(context, agent, tool, result)

    async def on_handoff(
        self, context: RunContext, agent: Any, source: Any
    ) -> None:
        for hook in self.hooks:
            await hook.on_handoff(context, agent, source)
