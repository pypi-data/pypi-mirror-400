"""
Base provider interface for LLM APIs.

Defines the abstract base class that all provider implementations must follow.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Iterator


@dataclass
class ToolCall:
    """
    Normalized tool call representation.

    Attributes:
        id: Unique identifier for the tool call
        name: Name of the tool/function to call
        arguments: Dictionary of arguments to pass to the tool
    """
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ProviderResponse:
    """
    Normalized response from any LLM provider.

    Attributes:
        content: Text content of the response (if any)
        tool_calls: List of tool calls requested by the model (if any)
        finish_reason: Normalized reason for completion
                       ('stop', 'tool_calls', 'length', 'error')
        raw_response: Original provider-specific response object
    """
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]]
    finish_reason: str
    raw_response: Any


@dataclass
class ProviderStreamEvent:
    """
    Normalized streaming event from any provider.

    Attributes:
        type: Event type ('content', 'tool_call', 'done', 'error')
        content: Text content delta (for 'content' events)
        tool_call: Tool call information (for 'tool_call' events)
        finish_reason: Completion reason (for 'done' events)
        error: Error message (for 'error' events)
    """
    type: str
    content: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    finish_reason: Optional[str] = None
    error: Optional[str] = None


class BaseProvider(ABC):
    """
    Abstract base class for LLM provider implementations.

    All provider adapters (OpenAI, Anthropic, etc.) must implement this interface
    to ensure consistent behavior across different LLM APIs.
    """

    @abstractmethod
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the provider with API credentials.

        Args:
            api_key: API key for authentication
            base_url: Optional custom API endpoint URL

        Raises:
            ValueError: If api_key is not provided
        """
        pass

    @abstractmethod
    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> ProviderResponse:
        """
        Create a completion (non-streaming) with the provider's API.

        Args:
            messages: List of conversation messages in OpenAI format
            system_prompt: System prompt/instructions for the model
            config: Agent configuration with model parameters
            tools: Optional list of tool schemas in OpenAI format

        Returns:
            ProviderResponse with normalized response data

        Raises:
            Exception: If API call fails
        """
        pass

    @abstractmethod
    def create_streaming_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Iterator[ProviderStreamEvent]:
        """
        Create a streaming completion with the provider's API.

        Args:
            messages: List of conversation messages in OpenAI format
            system_prompt: System prompt/instructions for the model
            config: Agent configuration with model parameters
            tools: Optional list of tool schemas in OpenAI format

        Yields:
            ProviderStreamEvent objects with streaming updates

        Raises:
            Exception: If API call fails
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.

        Returns:
            Provider name (e.g., 'openai', 'anthropic')
        """
        pass
