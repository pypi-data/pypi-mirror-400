"""
Conversation Memory Management System for indus-agents.

This module provides comprehensive conversation memory management with features including:
- Circular buffer for message history
- Token counting and cost estimation
- Persistent storage (JSON)
- Message filtering and search
- Thread-safe operations
- Metadata tracking
- Summary generation capabilities

Author: indus-agents
License: MIT
"""

import json
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


# Token counting utility
def estimate_tokens(text: str) -> int:
    """
    Estimate token count for a text string.

    Uses a simple heuristic: ~4 characters per token.
    For production use with OpenAI, consider using tiktoken library.

    Args:
        text: Input text to estimate tokens for

    Returns:
        Estimated token count

    Example:
        >>> estimate_tokens("Hello, world!")
        3
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


def estimate_tokens_from_messages(messages: List[Dict[str, Any]]) -> int:
    """
    Estimate total tokens from a list of messages.

    Includes overhead for message formatting (role, etc).

    Args:
        messages: List of message dictionaries

    Returns:
        Estimated total token count

    Example:
        >>> msgs = [{"role": "user", "content": "Hi"}]
        >>> estimate_tokens_from_messages(msgs)
        5
    """
    total = 0
    for msg in messages:
        # Count content tokens
        content = msg.get("content", "")
        total += estimate_tokens(str(content))

        # Add overhead for role and formatting (~3-4 tokens per message)
        total += 4

        # If tool_calls present, count them too
        if "tool_calls" in msg and msg["tool_calls"]:
            for tool_call in msg["tool_calls"]:
                if hasattr(tool_call, "function"):
                    total += estimate_tokens(tool_call.function.name or "")
                    total += estimate_tokens(tool_call.function.arguments or "")
                elif isinstance(tool_call, dict):
                    func = tool_call.get("function", {})
                    total += estimate_tokens(func.get("name", ""))
                    total += estimate_tokens(func.get("arguments", ""))

    return total


def estimate_cost(tokens: int, model: str = "gpt-4o") -> float:
    """
    Estimate API cost based on token count and model.

    Pricing as of 2025 (approximate, check OpenAI pricing for accuracy):
    - gpt-4o: $0.005 per 1K input tokens, $0.015 per 1K output tokens
    - gpt-4-turbo: $0.01 per 1K input tokens, $0.03 per 1K output tokens
    - gpt-3.5-turbo: $0.0005 per 1K input tokens, $0.0015 per 1K output tokens

    Args:
        tokens: Number of tokens
        model: Model identifier

    Returns:
        Estimated cost in USD

    Example:
        >>> estimate_cost(1000, "gpt-4o")
        0.01
    """
    # Pricing per 1K tokens (combined input + output estimate)
    pricing = {
        "gpt-4o": 0.01,
        "gpt-4-turbo": 0.02,
        "gpt-4": 0.045,
        "gpt-3.5-turbo": 0.001,
    }

    # Default pricing if model not found
    price_per_1k = pricing.get(model, 0.01)

    return (tokens / 1000.0) * price_per_1k


class Message(BaseModel):
    """
    Represents a single message in a conversation.

    Attributes:
        role: Message role ('user', 'assistant', 'system', 'tool')
        content: Message content text
        timestamp: When the message was created
        metadata: Additional metadata (tool_calls, tokens, etc)
        message_id: Unique identifier for the message
    """

    role: str = Field(
        description="Message role: user, assistant, system, or tool"
    )
    content: Optional[str] = Field(
        default="",
        description="Message content"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Message creation timestamp"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional message metadata"
    )
    message_id: Optional[str] = Field(
        default=None,
        description="Unique message identifier"
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate that role is one of the allowed values."""
        allowed_roles = {"user", "assistant", "system", "tool", "function"}
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of {allowed_roles}, got: {v}")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert message to dictionary format.

        Returns:
            Dictionary representation of message
        """
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "message_id": self.message_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """
        Create message from dictionary.

        Args:
            data: Dictionary with message data

        Returns:
            Message instance
        """
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def get_token_count(self) -> int:
        """Get estimated token count for this message."""
        return estimate_tokens(self.content or "")

    def __str__(self) -> str:
        """String representation of message."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"[{self.role}] {content_preview}"


class ConversationMemory:
    """
    Thread-safe conversation memory manager with circular buffer.

    Features:
    - Automatic message history management with max size limit
    - Token counting and cost estimation
    - Persistent storage (save/load to JSON)
    - Message filtering and search
    - Thread-safe operations
    - Metadata tracking (tokens, costs, etc)

    Example:
        >>> memory = ConversationMemory(max_messages=100)
        >>> memory.add_message("user", "Hello!")
        >>> memory.add_message("assistant", "Hi there!")
        >>> messages = memory.get_messages()
        >>> print(len(messages))
        2
        >>> memory.save_to_file("conversation.json")
    """

    def __init__(
        self,
        max_messages: int = 1000,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize conversation memory.

        Args:
            max_messages: Maximum number of messages to store (circular buffer)
            conversation_id: Unique identifier for this conversation
            metadata: Additional conversation-level metadata
        """
        self.max_messages = max_messages
        self.conversation_id = conversation_id or self._generate_conversation_id()
        self._messages: Deque[Message] = deque(maxlen=max_messages)
        self._metadata: Dict[str, Any] = metadata or {}
        self._lock = threading.RLock()

        # Track statistics
        self._total_tokens = 0
        self._total_cost = 0.0
        self._message_count = 0

    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        return f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    def add_message(
        self,
        role: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
    ) -> Message:
        """
        Add a message to the conversation history.

        Args:
            role: Message role (user, assistant, system, tool)
            content: Message content
            metadata: Additional message metadata
            message_id: Optional custom message ID

        Returns:
            The created Message object

        Raises:
            ValueError: If role is invalid

        Example:
            >>> memory = ConversationMemory()
            >>> msg = memory.add_message("user", "Hello!")
            >>> print(msg.role)
            'user'
        """
        with self._lock:
            # Create message
            msg = Message(
                role=role,
                content=content or "",
                metadata=metadata or {},
                message_id=message_id or f"msg_{self._message_count}",
            )

            # Add to buffer
            self._messages.append(msg)

            # Update statistics
            tokens = msg.get_token_count()
            self._total_tokens += tokens
            self._message_count += 1

            return msg

    def add_messages(self, messages: List[Dict[str, Any]]) -> None:
        """
        Add multiple messages at once.

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Example:
            >>> memory = ConversationMemory()
            >>> msgs = [
            ...     {"role": "user", "content": "Hi"},
            ...     {"role": "assistant", "content": "Hello!"}
            ... ]
            >>> memory.add_messages(msgs)
        """
        with self._lock:
            for msg_data in messages:
                self.add_message(
                    role=msg_data.get("role", "user"),
                    content=msg_data.get("content", ""),
                    metadata=msg_data.get("metadata"),
                )

    def get_messages(
        self,
        limit: Optional[int] = None,
        role: Optional[str] = None,
        after_timestamp: Optional[datetime] = None,
        before_timestamp: Optional[datetime] = None,
    ) -> List[Message]:
        """
        Get messages from history with optional filtering.

        Args:
            limit: Maximum number of messages to return (most recent first)
            role: Filter by specific role
            after_timestamp: Only messages after this timestamp
            before_timestamp: Only messages before this timestamp

        Returns:
            List of Message objects matching criteria

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> memory.add_message("assistant", "Hi")
            >>> user_msgs = memory.get_messages(role="user")
            >>> print(len(user_msgs))
            1
        """
        with self._lock:
            messages = list(self._messages)

            # Apply filters
            if role:
                messages = [m for m in messages if m.role == role]

            if after_timestamp:
                messages = [m for m in messages if m.timestamp > after_timestamp]

            if before_timestamp:
                messages = [m for m in messages if m.timestamp < before_timestamp]

            # Apply limit
            if limit:
                messages = messages[-limit:]

            return messages

    def get_messages_as_dicts(
        self,
        limit: Optional[int] = None,
        include_metadata: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get messages as dictionaries (compatible with OpenAI API format).

        Args:
            limit: Maximum number of messages to return
            include_metadata: Include metadata in output

        Returns:
            List of message dictionaries

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> dicts = memory.get_messages_as_dicts()
            >>> print(dicts[0]["role"])
            'user'
        """
        messages = self.get_messages(limit=limit)

        if include_metadata:
            return [msg.to_dict() for msg in messages]
        else:
            return [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

    def search_messages(
        self,
        query: str,
        case_sensitive: bool = False,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """
        Search for messages containing a specific query string.

        Args:
            query: Search query string
            case_sensitive: Whether search should be case-sensitive
            limit: Maximum number of results to return

        Returns:
            List of matching Message objects

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "What is Python?")
            >>> results = memory.search_messages("Python")
            >>> print(len(results))
            1
        """
        with self._lock:
            messages = list(self._messages)

            # Perform search
            if not case_sensitive:
                query = query.lower()
                matches = [
                    m for m in messages
                    if query in (m.content or "").lower()
                ]
            else:
                matches = [
                    m for m in messages
                    if query in (m.content or "")
                ]

            # Apply limit
            if limit:
                matches = matches[:limit]

            return matches

    def clear(self) -> None:
        """
        Clear all messages from memory.

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> memory.clear()
            >>> print(len(memory.get_messages()))
            0
        """
        with self._lock:
            self._messages.clear()
            self._total_tokens = 0
            self._total_cost = 0.0

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get conversation statistics.

        Returns:
            Dictionary with statistics (message count, tokens, cost, etc)

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello world!")
            >>> stats = memory.get_statistics()
            >>> print(stats["message_count"])
            1
        """
        with self._lock:
            messages = list(self._messages)

            # Count messages by role
            role_counts = {}
            for msg in messages:
                role_counts[msg.role] = role_counts.get(msg.role, 0) + 1

            # Get timestamp range
            timestamps = [m.timestamp for m in messages]
            first_message = min(timestamps) if timestamps else None
            last_message = max(timestamps) if timestamps else None

            return {
                "conversation_id": self.conversation_id,
                "message_count": len(messages),
                "total_messages_processed": self._message_count,
                "max_messages": self.max_messages,
                "role_counts": role_counts,
                "total_tokens": self._total_tokens,
                "estimated_cost": self._total_cost,
                "first_message_time": first_message.isoformat() if first_message else None,
                "last_message_time": last_message.isoformat() if last_message else None,
            }

    def estimate_tokens(self, model: str = "gpt-4o") -> int:
        """
        Estimate total tokens in current conversation.

        Args:
            model: Model name (for more accurate estimation if needed)

        Returns:
            Estimated token count

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello!")
            >>> tokens = memory.estimate_tokens()
            >>> print(tokens > 0)
            True
        """
        with self._lock:
            messages_dicts = self.get_messages_as_dicts()
            return estimate_tokens_from_messages(messages_dicts)

    def estimate_cost(self, model: str = "gpt-4o") -> float:
        """
        Estimate API cost for current conversation.

        Args:
            model: Model name for cost calculation

        Returns:
            Estimated cost in USD

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello!")
            >>> cost = memory.estimate_cost("gpt-4o")
            >>> print(cost >= 0)
            True
        """
        tokens = self.estimate_tokens(model)
        return estimate_cost(tokens, model)

    def get_summary(self) -> str:
        """
        Get a text summary of the conversation.

        Returns:
            Formatted summary string

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> summary = memory.get_summary()
            >>> print("messages" in summary)
            True
        """
        stats = self.get_statistics()

        summary_lines = [
            f"Conversation ID: {stats['conversation_id']}",
            f"Messages: {stats['message_count']} (max: {stats['max_messages']})",
            f"Total processed: {stats['total_messages_processed']}",
            f"Roles: {', '.join(f'{k}: {v}' for k, v in stats['role_counts'].items())}",
            f"Estimated tokens: {stats['total_tokens']}",
            f"Estimated cost: ${stats['estimated_cost']:.4f}",
        ]

        if stats['first_message_time']:
            summary_lines.append(f"First message: {stats['first_message_time']}")
        if stats['last_message_time']:
            summary_lines.append(f"Last message: {stats['last_message_time']}")

        return "\n".join(summary_lines)

    def save_to_file(
        self,
        file_path: Union[str, Path],
        include_metadata: bool = True,
    ) -> None:
        """
        Save conversation to a JSON file.

        Args:
            file_path: Path to save file
            include_metadata: Include conversation metadata

        Raises:
            IOError: If file cannot be written

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> memory.save_to_file("conversation.json")
        """
        with self._lock:
            file_path = Path(file_path)

            # Prepare data
            data = {
                "conversation_id": self.conversation_id,
                "max_messages": self.max_messages,
                "messages": [msg.to_dict() for msg in self._messages],
                "statistics": self.get_statistics(),
            }

            if include_metadata:
                data["metadata"] = self._metadata

            # Write to file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> "ConversationMemory":
        """
        Load conversation from a JSON file.

        Args:
            file_path: Path to load file from

        Returns:
            ConversationMemory instance with loaded data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> memory.save_to_file("conversation.json")
            >>> loaded = ConversationMemory.load_from_file("conversation.json")
            >>> print(loaded.get_messages()[0].content)
            'Hello'
        """
        file_path = Path(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Create instance
        memory = cls(
            max_messages=data.get("max_messages", 1000),
            conversation_id=data.get("conversation_id"),
            metadata=data.get("metadata", {}),
        )

        # Load messages
        for msg_data in data.get("messages", []):
            msg = Message.from_dict(msg_data)
            memory._messages.append(msg)
            memory._message_count += 1

        # Recalculate statistics
        memory._total_tokens = sum(m.get_token_count() for m in memory._messages)

        return memory

    def export_to_text(
        self,
        file_path: Union[str, Path],
        include_timestamps: bool = True,
    ) -> None:
        """
        Export conversation to a human-readable text file.

        Args:
            file_path: Path to save text file
            include_timestamps: Include message timestamps

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> memory.export_to_text("conversation.txt")
        """
        with self._lock:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                # Write header
                f.write(f"Conversation: {self.conversation_id}\n")
                f.write(f"Messages: {len(self._messages)}\n")
                f.write("=" * 80 + "\n\n")

                # Write messages
                for msg in self._messages:
                    if include_timestamps:
                        timestamp_str = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp_str}] {msg.role.upper()}:\n")
                    else:
                        f.write(f"{msg.role.upper()}:\n")

                    f.write(f"{msg.content}\n\n")

                # Write statistics
                f.write("=" * 80 + "\n")
                f.write(self.get_summary() + "\n")

    def get_last_n_messages(self, n: int) -> List[Message]:
        """
        Get the last N messages from history.

        Args:
            n: Number of recent messages to retrieve

        Returns:
            List of most recent messages

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> memory.add_message("assistant", "Hi")
            >>> recent = memory.get_last_n_messages(1)
            >>> print(recent[0].role)
            'assistant'
        """
        with self._lock:
            messages = list(self._messages)
            return messages[-n:] if n > 0 else []

    def get_context_window(
        self,
        max_tokens: int,
        model: str = "gpt-4o",
    ) -> List[Dict[str, Any]]:
        """
        Get messages that fit within a token budget (for API calls).

        Retrieves the most recent messages that fit within the specified
        token limit, ensuring the context sent to the API doesn't exceed limits.

        Args:
            max_tokens: Maximum tokens allowed in context
            model: Model name (for accurate token counting)

        Returns:
            List of message dictionaries that fit within token budget

        Example:
            >>> memory = ConversationMemory()
            >>> memory.add_message("user", "Hello")
            >>> context = memory.get_context_window(100)
            >>> print(len(context) > 0)
            True
        """
        with self._lock:
            messages = list(self._messages)
            result = []
            total_tokens = 0

            # Iterate from most recent to oldest
            for msg in reversed(messages):
                msg_dict = {"role": msg.role, "content": msg.content}
                msg_tokens = estimate_tokens_from_messages([msg_dict])

                if total_tokens + msg_tokens <= max_tokens:
                    result.insert(0, msg_dict)
                    total_tokens += msg_tokens
                else:
                    break

            return result

    def __len__(self) -> int:
        """Get number of messages in memory."""
        return len(self._messages)

    def __repr__(self) -> str:
        """String representation of ConversationMemory."""
        return (
            f"ConversationMemory(id='{self.conversation_id}', "
            f"messages={len(self._messages)}/{self.max_messages}, "
            f"tokens={self._total_tokens})"
        )


# Convenience functions

def create_memory(
    max_messages: int = 1000,
    conversation_id: Optional[str] = None,
) -> ConversationMemory:
    """
    Create a new conversation memory instance.

    Args:
        max_messages: Maximum messages to store
        conversation_id: Optional conversation ID

    Returns:
        New ConversationMemory instance

    Example:
        >>> memory = create_memory(max_messages=50)
        >>> print(memory.max_messages)
        50
    """
    return ConversationMemory(
        max_messages=max_messages,
        conversation_id=conversation_id,
    )


def load_memory(file_path: Union[str, Path]) -> ConversationMemory:
    """
    Load conversation memory from file.

    Args:
        file_path: Path to JSON file

    Returns:
        Loaded ConversationMemory instance

    Example:
        >>> memory = load_memory("conversation.json")
    """
    return ConversationMemory.load_from_file(file_path)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Conversation Memory Management System - Demo")
    print("=" * 80)
    print()

    # Example 1: Basic usage
    print("Example 1: Basic Usage")
    print("-" * 40)

    memory = ConversationMemory(max_messages=10)
    print(f"Created: {memory}")
    print()

    # Add some messages
    memory.add_message("user", "Hello! How are you?")
    memory.add_message("assistant", "I'm doing well, thank you! How can I help you today?")
    memory.add_message("user", "Can you tell me about Python?")
    memory.add_message(
        "assistant",
        "Python is a high-level, interpreted programming language known for "
        "its simplicity and readability. It's widely used in web development, "
        "data science, machine learning, and automation."
    )

    print(f"Messages added: {len(memory)}")
    print()

    # Example 2: Get messages
    print("Example 2: Retrieving Messages")
    print("-" * 40)

    for msg in memory.get_messages():
        print(f"{msg.role.upper()}: {msg.content[:60]}...")
    print()

    # Example 3: Statistics
    print("Example 3: Statistics")
    print("-" * 40)

    stats = memory.get_statistics()
    print(f"Total messages: {stats['message_count']}")
    print(f"Role distribution: {stats['role_counts']}")
    print(f"Estimated tokens: {stats['total_tokens']}")
    print(f"Estimated cost: ${stats['estimated_cost']:.4f}")
    print()

    # Example 4: Search
    print("Example 4: Message Search")
    print("-" * 40)

    results = memory.search_messages("Python")
    print(f"Found {len(results)} message(s) containing 'Python':")
    for msg in results:
        print(f"  - {msg}")
    print()

    # Example 5: Filtering
    print("Example 5: Filtering Messages")
    print("-" * 40)

    user_messages = memory.get_messages(role="user")
    print(f"User messages: {len(user_messages)}")
    for msg in user_messages:
        print(f"  - {msg.content}")
    print()

    assistant_messages = memory.get_messages(role="assistant")
    print(f"Assistant messages: {len(assistant_messages)}")
    print()

    # Example 6: Context window
    print("Example 6: Context Window (Token Budget)")
    print("-" * 40)

    context = memory.get_context_window(max_tokens=100)
    print(f"Messages fitting in 100 token budget: {len(context)}")
    for msg in context:
        print(f"  - [{msg['role']}] {msg['content'][:40]}...")
    print()

    # Example 7: Persistence
    print("Example 7: Save/Load Conversation")
    print("-" * 40)

    # Save to file
    save_path = Path("example_conversation.json")
    memory.save_to_file(save_path)
    print(f"Saved conversation to: {save_path}")

    # Load from file
    loaded_memory = ConversationMemory.load_from_file(save_path)
    print(f"Loaded conversation: {loaded_memory}")
    print(f"Messages preserved: {len(loaded_memory)}")
    print()

    # Example 8: Export to text
    print("Example 8: Export to Text")
    print("-" * 40)

    text_path = Path("example_conversation.txt")
    memory.export_to_text(text_path)
    print(f"Exported to text file: {text_path}")
    print()

    # Example 9: Summary
    print("Example 9: Conversation Summary")
    print("-" * 40)

    print(memory.get_summary())
    print()

    # Example 10: Circular buffer behavior
    print("Example 10: Circular Buffer (Max Messages)")
    print("-" * 40)

    small_memory = ConversationMemory(max_messages=3)
    for i in range(5):
        small_memory.add_message("user", f"Message {i + 1}")

    print(f"Added 5 messages to memory with max_messages=3")
    print(f"Messages in memory: {len(small_memory)}")
    print("Remaining messages:")
    for msg in small_memory.get_messages():
        print(f"  - {msg.content}")
    print()

    # Example 11: Thread-safe operations
    print("Example 11: Thread-Safe Operations")
    print("-" * 40)

    import concurrent.futures

    thread_memory = ConversationMemory(max_messages=100)

    def add_messages_worker(worker_id: int, count: int):
        for i in range(count):
            thread_memory.add_message(
                "user",
                f"Message from worker {worker_id}, iteration {i}"
            )

    # Add messages from multiple threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(add_messages_worker, worker_id, 10)
            for worker_id in range(3)
        ]
        concurrent.futures.wait(futures)

    print(f"Added messages from 3 threads concurrently")
    print(f"Total messages: {len(thread_memory)}")
    print()

    # Cleanup example files
    print("Cleaning up example files...")
    if save_path.exists():
        save_path.unlink()
    if text_path.exists():
        text_path.unlink()

    print()
    print("=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)
