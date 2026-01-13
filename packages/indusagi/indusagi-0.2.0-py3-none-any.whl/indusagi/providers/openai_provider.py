"""
OpenAI provider implementation.

Handles API calls to OpenAI's chat completions API.
"""

from typing import List, Dict, Any, Optional, Iterator
from openai import OpenAI
from .base import BaseProvider, ProviderResponse, ToolCall, ProviderStreamEvent


class OpenAIProvider(BaseProvider):
    """
    OpenAI API provider implementation.

    Handles communication with OpenAI's API using the official Python SDK.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            base_url: Optional custom API endpoint

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required. "
                "Please set it with: export OPENAI_API_KEY='your-key-here'"
            )

        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)

    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> ProviderResponse:
        """
        Create a completion using OpenAI's API.

        Args:
            messages: Conversation messages in OpenAI format
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas

        Returns:
            Normalized ProviderResponse

        Raises:
            Exception: If API call fails
        """
        # Build OpenAI-style messages with system prompt
        api_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        # Handle different model types
        is_gpt5_or_reasoning = (
            "gpt-5" in config.model.lower() or
            "o1" in config.model.lower() or
            "o3" in config.model.lower()
        )

        # Build API parameters
        api_params = {
            "model": config.model,
            "messages": api_messages,
        }

        # Apply model-specific parameters
        if is_gpt5_or_reasoning:
            # GPT-5/reasoning models: restricted parameters
            api_params["max_completion_tokens"] = config.max_tokens
            api_params["temperature"] = 1  # Only supported value
        else:
            # Standard OpenAI models: full parameter support
            api_params["max_tokens"] = config.max_tokens
            api_params["temperature"] = config.temperature
            api_params["top_p"] = config.top_p
            api_params["frequency_penalty"] = config.frequency_penalty
            api_params["presence_penalty"] = config.presence_penalty

        # Add tools if provided
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        # Call OpenAI API
        response = self.client.chat.completions.create(**api_params)

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
        Create a streaming completion using OpenAI's API.

        Args:
            messages: Conversation messages
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas

        Yields:
            ProviderStreamEvent objects

        Raises:
            Exception: If API call fails
        """
        # Build messages
        api_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        # Handle different model types
        is_gpt5_or_reasoning = (
            "gpt-5" in config.model.lower() or
            "o1" in config.model.lower() or
            "o3" in config.model.lower()
        )

        # Build API parameters
        api_params = {
            "model": config.model,
            "messages": api_messages,
            "stream": True
        }

        # Apply model-specific parameters
        if is_gpt5_or_reasoning:
            api_params["max_completion_tokens"] = config.max_tokens
            api_params["temperature"] = 1
        else:
            api_params["max_tokens"] = config.max_tokens
            api_params["temperature"] = config.temperature
            api_params["top_p"] = config.top_p
            api_params["frequency_penalty"] = config.frequency_penalty
            api_params["presence_penalty"] = config.presence_penalty

        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        # Stream response
        stream = self.client.chat.completions.create(**api_params)

        for chunk in stream:
            delta = chunk.choices[0].delta

            if delta.content:
                yield ProviderStreamEvent(
                    type="content",
                    content=delta.content
                )

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.function.name and tc.function.arguments:
                        yield ProviderStreamEvent(
                            type="tool_call",
                            tool_call=ToolCall(
                                id=tc.id,
                                name=tc.function.name,
                                arguments=eval(tc.function.arguments)  # Parse JSON string
                            )
                        )

            if chunk.choices[0].finish_reason:
                yield ProviderStreamEvent(
                    type="done",
                    finish_reason=chunk.choices[0].finish_reason
                )

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "openai"

    def _normalize_response(self, response) -> ProviderResponse:
        """
        Normalize OpenAI response to ProviderResponse format.

        Args:
            response: Raw OpenAI API response

        Returns:
            Normalized ProviderResponse
        """
        response_message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # Extract content
        content = response_message.content

        # Extract tool calls if present
        tool_calls = None
        if response_message.tool_calls:
            tool_calls = []
            for tc in response_message.tool_calls:
                import json
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                ))

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            raw_response=response
        )
