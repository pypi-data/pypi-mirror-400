"""
Core Agent class for LLM interaction using OpenAI API.

This module provides the Agent class which handles communication with OpenAI's API,
manages conversation history, and supports tool calling capabilities.
"""
from typing import Optional, List, Dict, Any
from openai import OpenAI
from pydantic import BaseModel, Field
import os
import time
import json


class AgentConfig(BaseModel):
    """
    Configuration for an Agent instance.

    Attributes:
        model: OpenAI model to use (e.g., 'gpt-4o', 'gpt-4-turbo')
        max_tokens: Maximum tokens in response (100-4096)
        temperature: Sampling temperature for randomness (0.0-2.0)
        top_p: Nucleus sampling parameter (0.0-1.0)
        frequency_penalty: Penalty for token frequency (-2.0 to 2.0)
        presence_penalty: Penalty for token presence (-2.0 to 2.0)
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Delay in seconds between retries
    """

    model: str = Field(
        default="gpt-4o",
        description="OpenAI model identifier"
    )
    max_tokens: int = Field(
        default=1024,
        ge=100,
        le=4096,
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
            OPENAI_MODEL: Model to use (default: gpt-4o)
            OPENAI_MAX_TOKENS: Maximum tokens (default: 1024)
            OPENAI_TEMPERATURE: Temperature (default: 0.7)

        Returns:
            AgentConfig instance with values from environment
        """
        return cls(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1024")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )


class Agent:
    """
    AI Agent that interacts with OpenAI's API.

    The Agent class manages conversation with LLM, maintains message history,
    and supports tool calling for extended capabilities. It handles retries,
    error recovery, and provides both basic and tool-enhanced processing.

    Attributes:
        name: Unique identifier for the agent
        role: Agent's specialized role or purpose
        config: Configuration settings
        client: OpenAI API client
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
    ) -> None:
        """
        Initialize an Agent instance.

        Args:
            name: Agent's identifier
            role: Agent's specialized role/purpose
            config: Configuration settings (uses defaults if None)
            system_prompt: Custom system prompt (auto-generated if None)

        Raises:
            ValueError: If OPENAI_API_KEY not set in environment
        """
        self.name = name
        self.role = role
        self.config = config or AgentConfig.from_env()

        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it with: export OPENAI_API_KEY='your-key-here'"
            )

        self.client = OpenAI(api_key=api_key)
        self.messages: List[Dict[str, Any]] = []
        self.system_prompt = system_prompt or (
            f"You are {name}, a helpful AI assistant. Your role is: {role}. "
            "Provide clear, accurate, and helpful responses."
        )

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
                # Call OpenAI API
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        *self.messages
                    ],
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    frequency_penalty=self.config.frequency_penalty,
                    presence_penalty=self.config.presence_penalty,
                )

                # Extract response text
                assistant_message = response.choices[0].message.content

                # Add to history
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
        max_turns: int = 10
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
                # Prepare API call parameters
                api_params = {
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        *self.messages
                    ],
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "frequency_penalty": self.config.frequency_penalty,
                    "presence_penalty": self.config.presence_penalty,
                }

                # Add tools if provided
                if tools:
                    api_params["tools"] = tools
                    api_params["tool_choice"] = "auto"

                # Call OpenAI API
                response = self.client.chat.completions.create(**api_params)

                # Get the message from response
                response_message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason

                # Add assistant message to history
                self.messages.append({
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": response_message.tool_calls
                })

                # Check if we're done
                if finish_reason == "stop":
                    # No tool calls, return final answer
                    return response_message.content or "I've completed the task."

                # Check if tools were called
                if finish_reason == "tool_calls" and response_message.tool_calls:
                    # Execute each tool call
                    tool_messages = []

                    for tool_call in response_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        print(f"[{self.name}] Using tool: {tool_name} with args: {tool_args}")

                        # Execute tool
                        if tool_executor:
                            try:
                                result = tool_executor.execute(tool_name, **tool_args)
                            except Exception as e:
                                result = f"Error executing tool: {str(e)}"
                        else:
                            result = f"Tool executor not provided for {tool_name}"

                        # Add tool result to messages
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": str(result)
                        })

                    # Add all tool results to history
                    self.messages.extend(tool_messages)

                    # Continue loop to get next response
                    continue

                # If we get here, something unexpected happened
                if response_message.content:
                    return response_message.content
                else:
                    return "I encountered an unexpected situation while processing your request."

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
