"""
Anthropic Claude provider implementation.

Handles API calls to Anthropic's Messages API with Claude models.
"""

from typing import List, Dict, Any, Optional, Iterator
import json
from .base import BaseProvider, ProviderResponse, ToolCall, ProviderStreamEvent
from ..utils.tool_converter import convert_openai_tools_to_anthropic


class AnthropicProvider(BaseProvider):
    """
    Anthropic Claude API provider implementation.

    Handles communication with Anthropic's API using the official Python SDK.
    Converts between OpenAI and Anthropic message formats to maintain compatibility.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            base_url: Optional custom API endpoint

        Raises:
            ValueError: If api_key is not provided
            ImportError: If anthropic package is not installed
        """
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required. "
                "Please set it with: export ANTHROPIC_API_KEY='your-key-here'"
            )

        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "The 'anthropic' package is required to use Anthropic models. "
                "Install it with: pip install anthropic"
            )

        if base_url:
            self.client = Anthropic(api_key=api_key, base_url=base_url)
        else:
            self.client = Anthropic(api_key=api_key)

    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> ProviderResponse:
        """
        Create a completion using Anthropic's API.

        Args:
            messages: Conversation messages in OpenAI format
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas in OpenAI format

        Returns:
            Normalized ProviderResponse

        Raises:
            Exception: If API call fails
        """
        # Convert messages from OpenAI format to Anthropic format
        anthropic_messages = self._convert_messages_to_anthropic(messages)

        # Convert tools if provided
        anthropic_tools = None
        if tools:
            anthropic_tools = convert_openai_tools_to_anthropic(tools)

        # Build API parameters
        api_params = {
            "model": config.model,
            "system": system_prompt,
            "messages": anthropic_messages,
            "max_tokens": config.max_tokens,  # Required for Anthropic
        }

        # Handle temperature/top_p (Claude 4.5 only supports one, not both)
        if config.temperature != 0.7:  # Non-default temperature
            api_params["temperature"] = config.temperature
        elif config.top_p != 1.0:  # Non-default top_p
            api_params["top_p"] = config.top_p
        else:
            # Both are default - use temperature
            api_params["temperature"] = config.temperature

        # Add tools if provided
        if anthropic_tools:
            api_params["tools"] = anthropic_tools

        # Call Anthropic API
        response = self.client.messages.create(**api_params)

        # Normalize response
        return self._normalize_response(response)

    def create_streaming_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Iterator[ProviderStreamEvent]:
        """
        Create a streaming completion using Anthropic's API.

        Args:
            messages: Conversation messages in OpenAI format
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas

        Yields:
            ProviderStreamEvent objects

        Raises:
            Exception: If API call fails
        """
        # Convert messages and tools
        anthropic_messages = self._convert_messages_to_anthropic(messages)
        anthropic_tools = None
        if tools:
            anthropic_tools = convert_openai_tools_to_anthropic(tools)

        # Build API parameters
        api_params = {
            "model": config.model,
            "system": system_prompt,
            "messages": anthropic_messages,
            "max_tokens": config.max_tokens,
            "stream": True
        }

        # Handle temperature/top_p
        if config.temperature != 0.7:
            api_params["temperature"] = config.temperature
        elif config.top_p != 1.0:
            api_params["top_p"] = config.top_p
        else:
            api_params["temperature"] = config.temperature

        if anthropic_tools:
            api_params["tools"] = anthropic_tools

        # Stream response
        with self.client.messages.stream(**api_params) as stream:
            for event in stream:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield ProviderStreamEvent(
                            type="content",
                            content=event.delta.text
                        )
                elif event.type == "message_stop":
                    yield ProviderStreamEvent(
                        type="done",
                        finish_reason=stream.current_message.stop_reason
                    )

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "anthropic"

    def _convert_messages_to_anthropic(
        self,
        openai_messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert OpenAI message format to Anthropic message format.

        Key differences:
        - System messages are handled separately (not in messages array)
        - Tool results are user messages with tool_result content blocks
        - Assistant tool calls are content blocks with type: tool_use

        Args:
            openai_messages: Messages in OpenAI format

        Returns:
            Messages in Anthropic format
        """
        anthropic_messages = []

        for msg in openai_messages:
            role = msg["role"]

            # Skip system messages (handled separately in Anthropic)
            if role == "system":
                continue

            # Handle tool messages -> convert to user messages with tool_result
            if role == "tool":
                anthropic_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.get("tool_call_id", ""),
                        "content": msg.get("content", "")
                    }]
                })

            # Handle assistant messages with tool calls
            elif role == "assistant" and msg.get("tool_calls"):
                content_blocks = []

                # Add text content if present
                if msg.get("content"):
                    content_blocks.append({
                        "type": "text",
                        "text": msg["content"]
                    })

                # Add tool use blocks
                for tc in msg["tool_calls"]:
                    # Parse arguments if they're a JSON string
                    args = tc.get("function", {}).get("arguments", "{}")
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}

                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc.get("id", ""),
                        "name": tc.get("function", {}).get("name", ""),
                        "input": args
                    })

                anthropic_messages.append({
                    "role": "assistant",
                    "content": content_blocks
                })

            # Handle regular messages
            else:
                anthropic_messages.append({
                    "role": "user" if role == "user" else "assistant",
                    "content": msg.get("content") or ""
                })

        return anthropic_messages

    def _normalize_response(self, response) -> ProviderResponse:
        """
        Normalize Anthropic response to ProviderResponse format.

        Args:
            response: Raw Anthropic API response

        Returns:
            Normalized ProviderResponse
        """
        # Extract text content
        text_content = None
        text_blocks = [
            block for block in response.content
            if hasattr(block, "text")
        ]
        if text_blocks:
            text_content = " ".join(block.text for block in text_blocks)

        # Extract tool calls
        tool_calls = []
        for block in response.content:
            if block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input
                ))

        # Normalize finish reason
        finish_reason_map = {
            "end_turn": "stop",
            "tool_use": "tool_calls",
            "max_tokens": "length",
            "stop_sequence": "stop"
        }
        finish_reason = finish_reason_map.get(
            response.stop_reason,
            "stop"
        )

        return ProviderResponse(
            content=text_content,
            tool_calls=tool_calls if tool_calls else None,
            finish_reason=finish_reason,
            raw_response=response
        )
