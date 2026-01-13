"""
Agency - Multi-Agent Orchestration System

Provides Agency Swarm-like orchestration for indus-agents.
"""
import os
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from indusagi.agent import Agent
from indusagi.tool_usage_logger import tool_logger


class HandoffType(Enum):
    """Types of agent handoff mechanisms."""
    MESSAGE = "message"
    FULL_CONTEXT = "full_context"


@dataclass
class HandoffResult:
    """Result of an agent handoff."""
    success: bool
    response: str
    from_agent: str
    to_agent: str
    processing_time: float
    error: Optional[str] = None


@dataclass
class AgencyResponse:
    """Response from agency processing."""
    response: str
    agents_used: List[str]
    handoffs: List[HandoffResult]
    total_time: float
    final_agent: str


class Agency:
    """
    Multi-agent orchestration system with defined communication flows.

    Similar to Agency Swarm's Agency class, this manages multiple agents
    and their inter-communication patterns.

    Example:
        >>> planner = create_planner_agent()
        >>> coder = create_coder_agent()
        >>> agency = Agency(
        ...     entry_agent=coder,
        ...     agents=[coder, planner],
        ...     communication_flows=[
        ...         (coder, planner),  # coder can hand off to planner
        ...         (planner, coder),  # planner can hand off to coder
        ...     ],
        ...     name="DevAgency",
        ...     shared_instructions="./project-overview.md"
        ... )
        >>> response = agency.process("Build a REST API")
    """

    def __init__(
        self,
        entry_agent: Agent,
        agents: Optional[List[Agent]] = None,
        communication_flows: Optional[List[Tuple[Agent, Agent]]] = None,
        shared_instructions: Optional[str] = None,
        name: str = "Agency",
        max_handoffs: int = 10,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Any] = None,
    ):
        """
        Initialize an Agency.

        Args:
            entry_agent: The agent that receives initial user input
            agents: List of all agents in the agency
            communication_flows: List of (source, target) tuples defining allowed handoffs
            shared_instructions: Path to shared instructions file
            name: Name of this agency
            max_handoffs: Maximum number of handoffs allowed per request
            tools: List of tool schemas for function calling
            tool_executor: Tool executor instance
        """
        self.entry_agent = entry_agent
        self.name = name
        self.max_handoffs = max_handoffs
        self.tools = tools or []
        self.tool_executor = tool_executor

        # Build agent registry
        self.agents = agents or [entry_agent]
        self._agent_map: Dict[str, Agent] = {a.name: a for a in self.agents}

        # Build communication graph
        self._flows: Dict[str, List[str]] = {}
        if communication_flows:
            for source, target in communication_flows:
                if source.name not in self._flows:
                    self._flows[source.name] = []
                self._flows[source.name].append(target.name)

        # Load shared instructions
        self._shared_context = ""
        if shared_instructions and os.path.exists(shared_instructions):
            with open(shared_instructions, "r") as f:
                self._shared_context = f.read()

        # Shared state across all agents
        self._shared_state: Dict[str, Any] = {}

        # Handoff history for current request
        self._handoff_history: List[HandoffResult] = []

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        return self._agent_map.get(name)

    def list_agents(self) -> List[str]:
        """List all agent names in the agency."""
        return list(self._agent_map.keys())

    def can_handoff(self, from_agent: str, to_agent: str) -> bool:
        """Check if handoff is allowed between agents."""
        return to_agent in self._flows.get(from_agent, [])

    def get_allowed_handoffs(self, agent_name: str) -> List[str]:
        """Get list of agents this agent can hand off to."""
        return self._flows.get(agent_name, [])

    def handoff(
        self,
        from_agent: Agent,
        to_agent_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> HandoffResult:
        """
        Execute a handoff from one agent to another.

        Args:
            from_agent: The agent initiating the handoff
            to_agent_name: Name of the target agent
            message: Message to pass to target agent
            context: Optional additional context

        Returns:
            HandoffResult with response and metadata
        """
        start_time = time.time()

        if not self.can_handoff(from_agent.name, to_agent_name):
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=0,
                error=f"Handoff from {from_agent.name} to {to_agent_name} not allowed"
            )

        target = self._agent_map.get(to_agent_name)
        if not target:
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=0,
                error=f"Agent {to_agent_name} not found"
            )

        # Build handoff message with context
        full_message = f"[Handoff from {from_agent.name}]\n\n{message}"

        if self._shared_context:
            full_message = f"[Shared Project Context]\n{self._shared_context}\n\n{full_message}"

        if context:
            context_str = "\n".join(f"- {k}: {v}" for k, v in context.items())
            full_message += f"\n\n[Additional Context]\n{context_str}"

        try:
            response = target.process(full_message)
            processing_time = time.time() - start_time

            result = HandoffResult(
                success=True,
                response=response,
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=processing_time
            )
            self._handoff_history.append(result)
            return result

        except Exception as e:
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def process(self, user_input: str, use_tools: bool = True, tools: Optional[List[Dict[str, Any]]] = None, tool_executor: Optional[Any] = None) -> AgencyResponse:
        """
        Process user input through the agency.

        Starts with entry_agent and handles any handoffs.

        Args:
            user_input: The user's request
            use_tools: Whether to enable tool usage
            tools: List of tool schemas (optional)
            tool_executor: Tool executor instance (optional)

        Returns:
            AgencyResponse with full processing details
        """
        start_time = time.time()
        self._handoff_history = []
        agents_used = [self.entry_agent.name]

        # Add shared context to initial message
        full_input = user_input
        if self._shared_context:
            full_input = f"[Project Context]\n{self._shared_context}\n\n[User Request]\n{user_input}"

        # Process with entry agent - use tools if enabled
        current_agent = self.entry_agent
        current_message = full_input
        response = ""
        handoff_count = 0

        # Loop until no more handoffs or max reached
        continue_processing = True

        while continue_processing and handoff_count < self.max_handoffs:
            # Process with current agent
            if use_tools and tools is not None:
                response = current_agent.process_with_tools(
                    current_message,
                    tools=tools,
                    tool_executor=tool_executor
                )
            else:
                response = current_agent.process(current_message)

            # Check if a handoff was requested via tool execution
            handoff_target = None
            handoff_message = None

            if tool_executor and hasattr(tool_executor, '_pending_handoff'):
                handoff_data = tool_executor._pending_handoff
                print(f"\nDEBUG: handoff_data = {handoff_data}")  # DEBUG
                # Check if handoff_data is not None before calling .get()
                if handoff_data is not None:
                    handoff_target = handoff_data.get('agent_name')
                    handoff_message = handoff_data.get('message', '')
                    print(f"DEBUG: handoff_target = {handoff_target}")  # DEBUG
                # Clear the pending handoff
                tool_executor._pending_handoff = None

            # If no handoff requested, we're done processing
            if not handoff_target:
                print(f"\nDEBUG: No handoff - processing complete")  # DEBUG
                continue_processing = False
                break

            print(f"\nDEBUG: Handoff detected to {handoff_target}")  # DEBUG

            # Validate handoff is allowed
            if not self.can_handoff(current_agent.name, handoff_target):
                print(f"\nWARNING: Handoff from {current_agent.name} to {handoff_target} not allowed")
                continue_processing = False
                break

            # Get target agent
            target_agent = self._agent_map.get(handoff_target)
            if not target_agent:
                print(f"\nWARNING: Target agent {handoff_target} not found")
                continue_processing = False
                break

            # Execute handoff
            print(f"\nHANDOFF: [{current_agent.name}] -> Handing off to [{handoff_target}]...")

            # Prepare message for target agent
            current_message = f"[Handoff from {current_agent.name}]\n\n{handoff_message}"
            if self._shared_context:
                current_message = f"[Shared Context]\n{self._shared_context}\n\n{current_message}"

            # Update current agent and continue loop to process with new agent
            current_agent = target_agent
            agents_used.append(current_agent.name)
            handoff_count += 1
            # continue_processing stays True - loop will continue with new agent

        return AgencyResponse(
            response=response,
            agents_used=agents_used,
            handoffs=self._handoff_history,
            total_time=time.time() - start_time,
            final_agent=agents_used[-1]
        )

    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """Get a value from shared state."""
        return self._shared_state.get(key, default)

    def set_shared_state(self, key: str, value: Any) -> None:
        """Set a value in shared state."""
        self._shared_state[key] = value

    def clear_shared_state(self) -> None:
        """Clear all shared state."""
        self._shared_state = {}

    def terminal_demo(self, show_reasoning: bool = False):
        """
        Run interactive terminal demo.

        Args:
            show_reasoning: Whether to show agent reasoning
        """
        print(f"\n{'='*60}")
        print(f"  {self.name} - Interactive Demo")
        print(f"  Agents: {', '.join(self.list_agents())}")
        print(f"  Entry: {self.entry_agent.name}")
        print(f"{'='*60}\n")

        print("Commands:")
        print("  /quit, /exit  - Exit the demo")
        print("  /agents       - List all agents")
        print("  /handoffs     - Show allowed handoffs")
        print("  /clear        - Clear conversation history")
        print("  /logs         - Show recent tool usage")
        print("  /stats        - Show tool usage statistics")
        print("  /export       - Export logs to JSON file")
        print()

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["/quit", "/exit"]:
                    print("Goodbye!")
                    break

                if user_input.lower() == "/agents":
                    print(f"Agents: {', '.join(self.list_agents())}")
                    continue

                if user_input.lower() == "/handoffs":
                    for agent in self.agents:
                        targets = self.get_allowed_handoffs(agent.name)
                        print(f"  {agent.name} → {targets if targets else '(none)'}")
                    continue

                if user_input.lower() == "/clear":
                    for agent in self.agents:
                        agent.clear_history()
                    print("Conversation history cleared.")
                    continue

                if user_input.lower() == "/logs":
                    tool_logger.print_recent_calls(limit=10)
                    continue

                if user_input.lower() == "/stats":
                    tool_logger.print_statistics()
                    continue

                if user_input.lower() == "/export":
                    filename = f"tool_logs_{int(time.time())}.json"
                    tool_logger.export_to_json(filename)
                    continue

                # Process the request
                result = self.process(
                    user_input,
                    use_tools=True,
                    tools=self.tools if self.tools else None,
                    tool_executor=self.tool_executor
                )

                print(f"\n[{result.final_agent}]: {result.response}")

                if result.handoffs:
                    print(f"\n  (Handoffs: {len(result.handoffs)}, Time: {result.total_time:.2f}s)")

                print()

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\n[Error]: {e}\n")

    def visualize(self) -> str:
        """
        Generate ASCII visualization of the agency structure.

        Returns:
            ASCII art representation of agents and flows
        """
        lines = [
            f"Agency: {self.name}",
            "=" * 40,
            "",
            "Agents:",
        ]

        for agent in self.agents:
            marker = ">" if agent == self.entry_agent else " "
            lines.append(f"  {marker} {agent.name}")

        lines.append("")
        lines.append("Communication Flows:")

        for source, targets in self._flows.items():
            for target in targets:
                lines.append(f"  {source} -> {target}")

        if not self._flows:
            lines.append("  (none defined)")

        return "\n".join(lines)
