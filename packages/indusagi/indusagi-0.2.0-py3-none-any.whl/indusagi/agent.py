"""
Core Agent class for LLM interaction using OpenAI and Anthropic APIs.

This module provides the Agent class which handles communication with multiple LLM
providers (OpenAI, Anthropic), manages conversation history, and supports tool calling.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import os
import time
import json
from indusagi.tool_usage_logger import tool_logger
from indusagi.providers.base import BaseProvider, ProviderResponse, ToolCall
from indusagi.providers.openai_provider import OpenAIProvider
from indusagi.providers.anthropic_provider import AnthropicProvider


class AgentConfig(BaseModel):
    """
    Configuration for an Agent instance.

    Attributes:
        model: Model to use (e.g., 'gpt-4o', 'claude-sonnet-4-5-20250929')
        provider: LLM provider ('openai' or 'anthropic'). Auto-detected if None.
        max_tokens: Maximum tokens in response (100-32000)
        temperature: Sampling temperature for randomness (0.0-2.0)
        top_p: Nucleus sampling parameter (0.0-1.0)
        frequency_penalty: Penalty for token frequency (-2.0 to 2.0)
        presence_penalty: Penalty for token presence (-2.0 to 2.0)
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Delay in seconds between retries
    """

    model: str = Field(
        default="gpt-4o",
        description="Model identifier (OpenAI: gpt-4o, gpt-5-mini | Anthropic: claude-sonnet-4-5-20250929)"
    )
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider: 'openai' or 'anthropic'. Auto-detected if None."
    )
    max_tokens: int = Field(
        default=1024,
        ge=100,
        le=32000,  # Increased to support comprehensive outputs
        description="Maximum tokens in response"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    frequency_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Frequency penalty"
    )
    presence_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Presence penalty"
    )
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts"
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Delay between retries in seconds"
    )

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        Create configuration from environment variables.

        Environment variables:
            LLM_PROVIDER: Provider to use ('openai' or 'anthropic')
            ANTHROPIC_MODEL: Anthropic model (default: claude-sonnet-4-5-20250929)
            OPENAI_MODEL: OpenAI model (default: gpt-4o)
            MAX_TOKENS: Maximum tokens (default: 1024)
            TEMPERATURE: Temperature (default: 0.7)

        Returns:
            AgentConfig instance with values from environment
        """
        # Detect provider
        provider = cls._detect_provider()

        # Get model based on provider
        if provider == "anthropic":
            default_model = "claude-sonnet-4-5-20250929"
            model_env = "ANTHROPIC_MODEL"
        else:
            default_model = "gpt-4o"
            model_env = "OPENAI_MODEL"

        return cls(
            model=os.getenv(model_env, default_model),
            provider=provider,
            max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )

    @staticmethod
    def _detect_provider() -> str:
        """
        Auto-detect provider from environment variables.

        Priority:
        1. LLM_PROVIDER environment variable
        2. ANTHROPIC_API_KEY (if set)
        3. OPENAI_API_KEY (if set)
        4. Default to 'openai'

        Returns:
            Provider name: 'openai' or 'anthropic'
        """
        # Check explicit provider setting
        explicit_provider = os.getenv("LLM_PROVIDER")
        if explicit_provider in ["openai", "anthropic"]:
            return explicit_provider

        # Auto-detect based on API keys
        has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
        has_openai = bool(os.getenv("OPENAI_API_KEY"))

        if has_anthropic and not has_openai:
            return "anthropic"
        elif has_openai:
            return "openai"

        # Default to OpenAI for backward compatibility
        return "openai"


class Agent:
    """
    AI Agent that interacts with LLM providers (OpenAI, Anthropic).

    The Agent class manages conversation with LLM, maintains message history,
    and supports tool calling for extended capabilities. It handles retries,
    error recovery, and provides both basic and tool-enhanced processing.

    Attributes:
        name: Unique identifier for the agent
        role: Agent's specialized role or purpose
        config: Configuration settings
        provider: LLM provider instance (OpenAI or Anthropic)
        messages: Conversation message history
        system_prompt: System prompt defining agent behavior

    Example:
        >>> agent = Agent("Assistant", "Helpful AI assistant")
        >>> response = agent.process("Hello!")
        >>> print(response)
        "Hello! How can I help you today?"
    """

    def __init__(
        self,
        name: str,
        role: str,
        config: Optional[AgentConfig] = None,
        system_prompt: Optional[str] = None,
        context: Optional[Any] = None,
    ) -> None:
        """
        Initialize an Agent instance.

        Args:
            name: Agent's identifier
            role: Agent's specialized role/purpose
            config: Configuration settings (uses defaults if None)
            system_prompt: Custom system prompt (auto-generated if None)
            context: Shared context object for tool state (optional)

        Raises:
            ValueError: If required API key not set in environment
        """
        self.name = name
        self.role = role
        self.config = config or AgentConfig.from_env()
        self.context = context

        # Determine provider (explicit config overrides auto-detection)
        provider_name = self.config.provider or self.config._detect_provider()

        # Initialize the appropriate provider
        self.provider = self._create_provider(provider_name)

        self.messages: List[Dict[str, Any]] = []
        self.system_prompt = system_prompt or (
            f"You are {name}, a helpful AI assistant. Your role is: {role}. "
            "Provide clear, accurate, and helpful responses."
        )

    def _create_provider(self, provider_name: str) -> BaseProvider:
        """
        Create and return the appropriate provider instance.

        Args:
            provider_name: Provider to use ('openai' or 'anthropic')

        Returns:
            Provider instance

        Raises:
            ValueError: If provider_name is invalid or API key is missing
        """
        if provider_name == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY environment variable not set. "
                    "Please set it with: export ANTHROPIC_API_KEY='your-key-here'"
                )

            base_url = os.getenv("ANTHROPIC_BASE_URL")
            return AnthropicProvider(api_key=api_key, base_url=base_url)

        elif provider_name == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable not set. "
                    "Please set it with: export OPENAI_API_KEY='your-key-here'"
                )

            base_url = os.getenv("OPENAI_BASE_URL")
            return OpenAIProvider(api_key=api_key, base_url=base_url)

        else:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                "Supported providers: 'openai', 'anthropic'"
            )

    def _tool_call_to_openai_format(self, tool_call: ToolCall) -> Dict[str, Any]:
        """
        Convert normalized ToolCall to OpenAI format for message history storage.

        Args:
            tool_call: Normalized ToolCall object from provider

        Returns:
            Tool call in OpenAI format
        """
        import json
        return {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.name,
                "arguments": json.dumps(tool_call.arguments)
            }
        }

    def process(self, user_input: str) -> str:
        """
        Process user input and return agent response.

        This is the basic processing method without tool support. It sends
        the user's message to the LLM and returns the response, with automatic
        retry logic for handling transient failures.

        Args:
            user_input: User's query or message

        Returns:
            Agent's response text

        Raises:
            Exception: If API call fails after all retry attempts

        Example:
            >>> agent = Agent("Helper", "General assistant")
            >>> response = agent.process("What is Python?")
            >>> print(response)
            "Python is a high-level programming language..."
        """
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        # Attempt API call with retries
        for attempt in range(self.config.max_retries):
            try:
                # Use provider abstraction
                response = self.provider.create_completion(
                    messages=self.messages,
                    system_prompt=self.system_prompt,
                    config=self.config,
                    tools=None
                )

                # Extract response content from normalized response
                assistant_message = response.content

                # Add to history (store in OpenAI format for consistency)
                self.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                return assistant_message

            except Exception as e:
                error_msg = f"Error processing request (attempt {attempt + 1}/{self.config.max_retries}): {str(e)}"
                print(f"[Agent {self.name}] {error_msg}")

                # If last attempt, return error
                if attempt == self.config.max_retries - 1:
                    return f"I apologize, but I encountered an error: {str(e)}"

                # Wait before retrying
                time.sleep(self.config.retry_delay)

        return "Maximum retry attempts reached. Please try again later."

    def process_with_tools(
        self,
        user_input: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Any] = None,
        max_turns: int = 30
    ) -> str:
        """
        Process user input with tool calling support.

        This method enables the agent to use tools (functions) to accomplish tasks.
        The agent can iteratively call tools, receive results, and use them to
        formulate the final response. This implements the full tool calling loop.

        Args:
            user_input: User's query or message
            tools: List of tool schemas in OpenAI format (optional)
            tool_executor: Object with execute(name, **kwargs) method (optional)
            max_turns: Maximum iterations of tool calling loop (default: 10)

        Returns:
            Final agent response after tool usage (if any)

        Raises:
            Exception: If API call fails after all retry attempts

        Example:
            >>> from tools import registry
            >>> agent = Agent("MathBot", "Mathematical assistant")
            >>> response = agent.process_with_tools(
            ...     "What is 25 * 4?",
            ...     tools=registry.schemas,
            ...     tool_executor=registry
            ... )
            >>> print(response)
            "The result of 25 * 4 is 100."

        Note:
            - The agent will automatically determine when to use tools
            - Multiple tool calls can be made in sequence
            - If max_turns is reached, returns partial result
        """
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        # Tool calling loop
        for turn in range(max_turns):
            try:
                # Use provider abstraction
                response = self.provider.create_completion(
                    messages=self.messages,
                    system_prompt=self.system_prompt,
                    config=self.config,
                    tools=tools
                )

                # Extract normalized response
                finish_reason = response.finish_reason
                content = response.content
                tool_calls = response.tool_calls

                # DEBUG: Log finish_reason
                print(f"\nDEBUG [{self.name}]: finish_reason = {finish_reason}")
                print(f"DEBUG [{self.name}]: has content = {bool(content)}")
                print(f"DEBUG [{self.name}]: has tool_calls = {bool(tool_calls)}")

                # Add assistant message to history (store in OpenAI format)
                assistant_msg = {
                    "role": "assistant",
                    "content": content,
                }

                # Convert tool_calls to OpenAI format if present
                if tool_calls:
                    assistant_msg["tool_calls"] = [
                        self._tool_call_to_openai_format(tc) for tc in tool_calls
                    ]

                self.messages.append(assistant_msg)

                # Check if we're done
                if finish_reason == "stop":
                    # No tool calls, return final answer
                    return content or "I've completed the task."

                # Check if tools were called
                if finish_reason == "tool_calls" and tool_calls:
                    # ⚠️ ENFORCE ONE-BY-ONE EXECUTION WHEN TODOS ARE ACTIVE
                    # Check if there are active todos in context
                    todos = self.context.get("todos", []) if self.context else []
                    has_active_todos = any(
                        todo.get("status") in ["pending", "in_progress"]
                        for todo in todos
                    )

                    # Count non-todo_write tool calls
                    non_todo_calls = [
                        tc for tc in tool_calls
                        if tc.name != "todo_write"
                    ]

                    # Track which tool calls to actually execute vs skip
                    tools_to_execute = []
                    tools_to_skip = []

                    # If there are active todos and multiple non-todo tools called, enforce one-by-one
                    if has_active_todos and len(non_todo_calls) > 1:
                        print(f"\n{'='*70}")
                        print(f"[{self.name}] WARNING: Attempted to execute {len(non_todo_calls)} tools at once!")
                        print(f"[{self.name}] Enforcing ONE-BY-ONE execution when todos are active")
                        print(f"[{self.name}] Only executing the first tool call")
                        print(f"{'='*70}\n")

                        # Determine which to execute vs skip
                        first_non_todo_found = False
                        for tc in tool_calls:
                            if tc.name == "todo_write":
                                tools_to_execute.append(tc)
                            elif not first_non_todo_found:
                                tools_to_execute.append(tc)
                                first_non_todo_found = True
                            else:
                                tools_to_skip.append(tc)  # Skip remaining tools
                    else:
                        # Execute all tools normally
                        tools_to_execute = tool_calls

                    # Execute each allowed tool call
                    tool_messages = []

                    for tool_call in tools_to_execute:
                        tool_name = tool_call.name
                        tool_args = tool_call.arguments  # Already a dict in normalized format

                        # Format tool usage log
                        self._log_tool_usage(tool_name, tool_args)

                        # Execute tool with timing and logging
                        start_time = time.time()
                        success = True
                        error_msg = None

                        if tool_executor:
                            try:
                                result = tool_executor.execute(tool_name, **tool_args)
                                # Log tool result for important tools
                                self._log_tool_result(tool_name, result)
                            except Exception as e:
                                result = f"Error executing tool: {str(e)}"
                                success = False
                                error_msg = str(e)
                        else:
                            result = f"Tool executor not provided for {tool_name}"
                            success = False
                            error_msg = "No tool executor"

                        execution_time = time.time() - start_time

                        # Log to tool usage logger
                        tool_logger.log_call(
                            tool_name=tool_name,
                            agent_name=self.name,
                            arguments=tool_args,
                            result=result,
                            success=success,
                            execution_time=execution_time,
                            error=error_msg
                        )

                        # Display real-time tool usage info
                        status_icon = "[OK]" if success else "[FAIL]"
                        print(f"\n{'-'*70}")
                        print(f"TOOL USAGE: {status_icon} {tool_name}")
                        print(f"{'-'*70}")
                        print(f"Execution Time: {execution_time:.3f}s")
                        print(f"Agent: {self.name}")
                        if error_msg:
                            print(f"Error: {error_msg}")

                        # Show running statistics
                        stats = tool_logger.get_statistics()
                        print(f"Session Stats: {stats['total_calls']} calls | "
                              f"{stats['success_rate']:.1f}% success | "
                              f"{stats['total_execution_time']:.2f}s total")
                        print(f"{'-'*70}\n")

                        # Check if this was a handoff - if so, stop processing
                        if tool_name == "handoff_to_agent":
                            # Add tool result
                            tool_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": str(result)
                            })
                            # Stop processing - let Agency handle the handoff
                            print(f"\nSTOP [Agent {self.name}] Handoff requested - stopping agent processing")
                            self.messages.extend(tool_messages)
                            return f"Handoff to {tool_args.get('agent_name', 'unknown')} requested."

                        # Add tool result to messages
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": str(result)
                        })

                    # Add error responses for skipped tools (to satisfy API requirement)
                    for skipped_tool in tools_to_skip:
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": skipped_tool.id,
                            "name": skipped_tool.name,
                            "content": "Tool execution skipped: ONE-BY-ONE enforcement is active. Please complete the current task before starting the next one."
                        })

                    # Add all tool results to history
                    self.messages.extend(tool_messages)

                    # Continue loop to get next response
                    continue

                # If we get here, something unexpected happened
                print(f"\nWARNING [{self.name}] UNEXPECTED: finish_reason={finish_reason}, content={bool(content)}, tool_calls={bool(tool_calls)}")
                if content:
                    return content
                else:
                    return f"I encountered an unexpected situation (finish_reason={finish_reason})."

            except Exception as e:
                error_msg = f"Error in tool calling loop (turn {turn + 1}): {str(e)}"
                print(f"[Agent {self.name}] {error_msg}")
                return f"I apologize, but I encountered an error: {str(e)}"

        # If we've exhausted max turns
        return (
            "I've reached the maximum number of processing steps. "
            "The task may be too complex or I may need different tools to complete it."
        )

    def clear_history(self) -> None:
        """
        Clear the conversation message history.

        This resets the agent's memory, starting a fresh conversation.
        The system prompt is preserved.

        Example:
            >>> agent = Agent("Helper", "Assistant")
            >>> agent.process("Hello")
            >>> print(len(agent.messages))
            2
            >>> agent.clear_history()
            >>> print(len(agent.messages))
            0
        """
        self.messages = []

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get a copy of the conversation message history.

        Returns:
            List of message dictionaries (copy, not reference)

        Example:
            >>> agent = Agent("Helper", "Assistant")
            >>> agent.process("Hello")
            >>> history = agent.get_history()
            >>> print(len(history))
            2
            >>> print(history[0]['role'])
            'user'
        """
        return self.messages.copy()

    def set_history(self, messages: List[Dict[str, Any]]) -> None:
        """
        Set the conversation message history.

        Useful for restoring a previous conversation state or
        starting with pre-populated context.

        Args:
            messages: List of message dictionaries to set as history

        Example:
            >>> agent = Agent("Helper", "Assistant")
            >>> old_messages = [
            ...     {"role": "user", "content": "Hello"},
            ...     {"role": "assistant", "content": "Hi there!"}
            ... ]
            >>> agent.set_history(old_messages)
            >>> print(len(agent.messages))
            2
        """
        self.messages = messages.copy()

    def get_token_count_estimate(self) -> int:
        """
        Get rough estimate of tokens used in conversation history.

        This is a simple estimation (4 chars ≈ 1 token). For accurate
        token counting, use tiktoken library.

        Returns:
            Estimated number of tokens in message history

        Example:
            >>> agent = Agent("Helper", "Assistant")
            >>> agent.process("Hello")
            >>> print(agent.get_token_count_estimate())
            15
        """
        total_chars = sum(
            len(msg.get("content", ""))
            for msg in self.messages
        )
        return total_chars // 4  # Rough estimate: 4 chars per token

    def _log_tool_usage(self, tool_name: str, tool_args: dict) -> None:
        """
        Log tool usage in a user-friendly format.

        Args:
            tool_name: Name of the tool being used
            tool_args: Arguments passed to the tool
        """
        # Special formatting for different tools
        if tool_name == "todo_write":
            todos = tool_args.get("todos", [])
            # Check if this is an initial todo creation or update
            statuses = [t.get("status") for t in todos]
            in_progress_count = statuses.count("in_progress")
            completed_count = statuses.count("completed")
            pending_count = statuses.count("pending")

            if completed_count == 0 and in_progress_count == 0:
                # Initial todo creation
                print(f"\n{'='*70}")
                print(f"[{self.name}] Creating todo list with {len(todos)} tasks:")
                print(f"{'='*70}")
                for i, todo in enumerate(todos, 1):
                    priority_emoji = {"high": "!", "medium": "~", "low": "-"}.get(todo.get("priority", "medium"), "~")
                    status_emoji = "⏳"
                    print(f"  {i}. [{priority_emoji}] {status_emoji} {todo.get('task')}")
                print(f"{'='*70}")
            else:
                # Todo update - ALWAYS show full list with progress
                print(f"\n{'='*70}")
                print(f"[{self.name}] TODO LIST UPDATE:")
                print(f"{'='*70}")
                for i, todo in enumerate(todos, 1):
                    priority_emoji = {"high": "!", "medium": "~", "low": "-"}.get(todo.get("priority", "medium"), "~")
                    status = todo.get("status")

                    # Status emoji
                    if status == "completed":
                        status_emoji = "✅"
                    elif status == "in_progress":
                        status_emoji = "🔄"
                    else:
                        status_emoji = "⏳"

                    print(f"  {i}. [{priority_emoji}] {status_emoji} {todo.get('task')}")

                print(f"\nProgress: {completed_count} done, {in_progress_count} in progress, {pending_count} pending")
                print(f"{'='*70}")

        elif tool_name == "write":
            file_path = tool_args.get("file_path", "")
            print(f"[{self.name}] Creating file: {file_path}")

        elif tool_name == "edit":
            file_path = tool_args.get("file_path", "")
            print(f"[{self.name}] Editing file: {file_path}")

        elif tool_name == "read":
            file_path = tool_args.get("file_path", "")
            print(f"[{self.name}] Reading file: {file_path}")

        elif tool_name == "bash":
            command = tool_args.get("command", "")
            description = tool_args.get("command_description", "")
            # Show BOTH command and description to debug what's actually being executed
            if description and description != command:
                print(f"[{self.name}] Running bash: '{command}'")
                print(f"[{self.name}] Description: {description}")
            else:
                print(f"[{self.name}] Running bash: '{command}'")

        elif tool_name == "glob":
            pattern = tool_args.get("pattern", "")
            print(f"[{self.name}] Finding files: {pattern}")

        elif tool_name == "grep":
            pattern = tool_args.get("pattern", "")
            print(f"[{self.name}] Searching for: {pattern}")

        elif tool_name == "handoff_to_agent":
            agent_name = tool_args.get("agent_name", "")
            message = tool_args.get("message", "")
            print(f"[{self.name}] Handing off to {agent_name}: {message[:60]}...")

        else:
            # Default logging for unknown tools
            print(f"[{self.name}] Using {tool_name}")

    def _log_tool_result(self, tool_name: str, result: str) -> None:
        """
        Log tool results for important operations.

        Args:
            tool_name: Name of the tool
            result: Result from the tool execution
        """
        # Log bash errors (especially validation errors)
        if tool_name == "bash":
            if "❌ ERROR" in result or "Error" in result:
                # Show the full error message
                print(f"\n{'='*70}")
                print(f"[{self.name}] BASH ERROR:")
                print(f"{'='*70}")
                print(result)
                print(f"{'='*70}\n")
            elif "Exit code: 0" in result:
                # Success - show brief confirmation
                print(f"[{self.name}] ✅ Command completed successfully")
            else:
                # Show other results
                print(f"[{self.name}] Result: {result[:200]}")

        # Only log results for specific tools (not todo_write since we show full list in _log_tool_usage)
        elif tool_name == "write" and "Successfully" in result:
            # Show success message
            if "created" in result:
                print(f"[{self.name}] ✅ File created successfully")
            elif "overwritten" in result:
                print(f"[{self.name}] ✅ File updated successfully")

    def __repr__(self) -> str:
        """String representation of Agent."""
        return (
            f"Agent(name='{self.name}', role='{self.role}', "
            f"model='{self.config.model}', messages={len(self.messages)})"
        )


# Quick test when run directly
if __name__ == "__main__":
    print("Testing Agent class with OpenAI API...\n")

    try:
        # Create agent
        agent = Agent(
            name="TestAgent",
            role="Testing assistant"
        )

        print(f"Created: {agent}")
        print(f"System prompt: {agent.system_prompt}\n")

        # Test basic processing
        print("Test 1: Basic processing")
        response = agent.process("Say 'Hello, world!' and nothing else.")
        print(f"Response: {response}\n")

        # Test history
        print("Test 2: History management")
        print(f"Messages in history: {len(agent.get_history())}")
        print(f"Token estimate: {agent.get_token_count_estimate()}\n")

        # Clear history
        agent.clear_history()
        print(f"After clearing: {len(agent.get_history())} messages\n")

        print("All tests completed successfully!")

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        print("\nMake sure OPENAI_API_KEY is set in your environment:")
        print("  export OPENAI_API_KEY='your-key-here'")
