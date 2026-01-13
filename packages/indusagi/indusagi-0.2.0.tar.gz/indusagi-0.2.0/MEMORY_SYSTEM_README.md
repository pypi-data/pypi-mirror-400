# Conversation Memory Management System

A production-ready conversation memory management system for AI indus-agents with advanced features including circular buffers, persistence, search, and cost estimation.

## Features

### Core Functionality
- **Circular Buffer**: Automatic message history management with configurable size limits
- **Thread-Safe**: All operations use proper locking for concurrent access
- **Persistence**: Save/load conversations to JSON files
- **Search**: Full-text search across conversation history
- **Filtering**: Filter messages by role, timestamp, or custom criteria
- **Token Counting**: Estimate token usage for API cost management
- **Cost Estimation**: Calculate approximate API costs based on usage
- **Export Formats**: JSON and human-readable text exports

### Advanced Features
- Message metadata tracking (timestamps, custom fields)
- Context window management for token budgets
- Summary generation
- Statistics tracking (message counts, roles, tokens)
- Unique conversation and message IDs
- Support for tool calls in messages

## Installation

The memory system is a standalone module with minimal dependencies:

```python
# Required dependencies (already in framework)
pip install pydantic
```

## Quick Start

### Basic Usage

```python
from memory import ConversationMemory

# Create a new conversation memory
memory = ConversationMemory(max_messages=1000)

# Add messages
memory.add_message("user", "Hello! How are you?")
memory.add_message("assistant", "I'm doing well, thank you!")

# Get all messages
messages = memory.get_messages()

# Get message count
count = len(memory)
print(f"Messages: {count}")
```

### Integration with Agent

```python
from agent import Agent, AgentConfig
from memory import ConversationMemory

# Create agent
agent = Agent("Assistant", "Helpful AI")

# Create memory
memory = ConversationMemory(max_messages=100)

# In your process loop
user_input = "What is Python?"
memory.add_message("user", user_input)

response = agent.process(user_input)
memory.add_message("assistant", response)

# Save conversation
memory.save_to_file("conversation.json")
```

### Agent with Built-in Memory

```python
from test_memory_integration import AgentWithMemory

# Create agent with integrated memory
agent = AgentWithMemory(
    name="ChatBot",
    role="Customer support",
    max_messages=500
)

# Use normally - memory is automatic
response = agent.process("Hello!")

# Access memory features
summary = agent.get_conversation_summary()
results = agent.search_conversation("Python")
agent.save_conversation("chat.json")
```

## API Reference

### ConversationMemory Class

#### Constructor

```python
ConversationMemory(
    max_messages: int = 1000,
    conversation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
)
```

**Parameters:**
- `max_messages`: Maximum number of messages to store (circular buffer)
- `conversation_id`: Unique identifier (auto-generated if None)
- `metadata`: Additional conversation-level metadata

#### Core Methods

##### add_message()

```python
add_message(
    role: str,
    content: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> Message
```

Add a message to the conversation history.

**Parameters:**
- `role`: Message role ('user', 'assistant', 'system', 'tool')
- `content`: Message content text
- `metadata`: Additional message metadata
- `message_id`: Custom message ID (auto-generated if None)

**Returns:** Created Message object

**Example:**
```python
msg = memory.add_message("user", "Hello!", metadata={"source": "web"})
```

##### get_messages()

```python
get_messages(
    limit: Optional[int] = None,
    role: Optional[str] = None,
    after_timestamp: Optional[datetime] = None,
    before_timestamp: Optional[datetime] = None
) -> List[Message]
```

Get messages with optional filtering.

**Parameters:**
- `limit`: Maximum number of messages (most recent first)
- `role`: Filter by specific role
- `after_timestamp`: Only messages after this time
- `before_timestamp`: Only messages before this time

**Returns:** List of Message objects

**Example:**
```python
# Get last 10 user messages
user_messages = memory.get_messages(limit=10, role="user")

# Get messages from today
from datetime import datetime, timedelta
today = datetime.now() - timedelta(days=1)
recent = memory.get_messages(after_timestamp=today)
```

##### search_messages()

```python
search_messages(
    query: str,
    case_sensitive: bool = False,
    limit: Optional[int] = None
) -> List[Message]
```

Search for messages containing a query string.

**Parameters:**
- `query`: Search query text
- `case_sensitive`: Whether search is case-sensitive
- `limit`: Maximum number of results

**Returns:** List of matching Message objects

**Example:**
```python
results = memory.search_messages("Python", limit=5)
for msg in results:
    print(f"[{msg.role}] {msg.content}")
```

##### get_statistics()

```python
get_statistics() -> Dict[str, Any]
```

Get conversation statistics.

**Returns:** Dictionary with:
- `conversation_id`: Unique conversation identifier
- `message_count`: Current number of messages
- `total_messages_processed`: All messages ever added
- `max_messages`: Buffer size limit
- `role_counts`: Messages per role
- `total_tokens`: Estimated total tokens
- `estimated_cost`: Estimated API cost
- `first_message_time`: First message timestamp
- `last_message_time`: Last message timestamp

**Example:**
```python
stats = memory.get_statistics()
print(f"Messages: {stats['message_count']}")
print(f"Cost: ${stats['estimated_cost']:.4f}")
```

##### clear()

```python
clear() -> None
```

Clear all messages from memory.

**Example:**
```python
memory.clear()
```

#### Token and Cost Management

##### estimate_tokens()

```python
estimate_tokens(model: str = "gpt-4o") -> int
```

Estimate total tokens in current conversation.

**Parameters:**
- `model`: Model name (for future accurate estimation)

**Returns:** Estimated token count

**Example:**
```python
tokens = memory.estimate_tokens()
print(f"Estimated tokens: {tokens}")
```

##### estimate_cost()

```python
estimate_cost(model: str = "gpt-4o") -> float
```

Estimate API cost for current conversation.

**Parameters:**
- `model`: Model name for cost calculation

**Returns:** Estimated cost in USD

**Example:**
```python
cost = memory.estimate_cost("gpt-4o")
print(f"Estimated cost: ${cost:.4f}")
```

##### get_context_window()

```python
get_context_window(
    max_tokens: int,
    model: str = "gpt-4o"
) -> List[Dict[str, Any]]
```

Get messages that fit within a token budget.

**Parameters:**
- `max_tokens`: Maximum tokens allowed
- `model`: Model name

**Returns:** List of message dicts fitting in budget

**Example:**
```python
# Get messages that fit in 4000 token context
context = memory.get_context_window(max_tokens=4000)
print(f"Messages in context: {len(context)}")
```

#### Persistence

##### save_to_file()

```python
save_to_file(
    file_path: Union[str, Path],
    include_metadata: bool = True
) -> None
```

Save conversation to JSON file.

**Parameters:**
- `file_path`: Path to save file
- `include_metadata`: Include conversation metadata

**Example:**
```python
memory.save_to_file("conversations/chat_001.json")
```

##### load_from_file() (classmethod)

```python
@classmethod
load_from_file(cls, file_path: Union[str, Path]) -> ConversationMemory
```

Load conversation from JSON file.

**Parameters:**
- `file_path`: Path to load from

**Returns:** ConversationMemory instance

**Example:**
```python
memory = ConversationMemory.load_from_file("conversations/chat_001.json")
```

##### export_to_text()

```python
export_to_text(
    file_path: Union[str, Path],
    include_timestamps: bool = True
) -> None
```

Export conversation to human-readable text file.

**Parameters:**
- `file_path`: Path to save text file
- `include_timestamps`: Include message timestamps

**Example:**
```python
memory.export_to_text("conversation.txt")
```

### Message Class

Pydantic model representing a single message.

```python
class Message(BaseModel):
    role: str  # 'user', 'assistant', 'system', 'tool'
    content: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]
    message_id: Optional[str]
```

**Methods:**
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary
- `get_token_count()`: Estimate tokens in message

### Utility Functions

#### estimate_tokens()

```python
estimate_tokens(text: str) -> int
```

Estimate token count for text (4 chars ≈ 1 token).

#### estimate_tokens_from_messages()

```python
estimate_tokens_from_messages(messages: List[Dict[str, Any]]) -> int
```

Estimate total tokens from message list.

#### estimate_cost()

```python
estimate_cost(tokens: int, model: str = "gpt-4o") -> float
```

Estimate API cost based on token count.

**Pricing (2025 estimates):**
- `gpt-4o`: $0.01 per 1K tokens (combined)
- `gpt-4-turbo`: $0.02 per 1K tokens
- `gpt-3.5-turbo`: $0.001 per 1K tokens

## Usage Examples

### Example 1: Basic Chat Bot

```python
from memory import ConversationMemory

# Initialize
memory = ConversationMemory(max_messages=100)

# Simulate conversation
conversations = [
    ("user", "What is machine learning?"),
    ("assistant", "Machine learning is a subset of AI..."),
    ("user", "Can you give an example?"),
    ("assistant", "Sure! Email spam filters use ML..."),
]

for role, content in conversations:
    memory.add_message(role, content)

# Get statistics
print(memory.get_summary())
```

### Example 2: Search and Analyze

```python
# Search for specific topics
ml_messages = memory.search_messages("machine learning")
print(f"Found {len(ml_messages)} messages about ML")

# Get user questions
questions = memory.get_messages(role="user")
print(f"User asked {len(questions)} questions")

# Check cost
cost = memory.estimate_cost("gpt-4o")
print(f"Conversation cost: ${cost:.4f}")
```

### Example 3: Persistent Sessions

```python
from pathlib import Path

# Start or resume conversation
session_file = Path("sessions/user_123.json")

if session_file.exists():
    memory = ConversationMemory.load_from_file(session_file)
    print(f"Resumed session with {len(memory)} messages")
else:
    memory = ConversationMemory(max_messages=500)
    print("Started new session")

# ... process messages ...

# Save session
memory.save_to_file(session_file)
```

### Example 4: Token Budget Management

```python
# Get context that fits in API limit
max_context_tokens = 4000
context = memory.get_context_window(max_tokens=max_context_tokens)

# Use with API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        *context  # Only recent messages that fit
    ]
)
```

### Example 5: Conversation Analytics

```python
from datetime import datetime, timedelta

# Get today's messages
today = datetime.now().replace(hour=0, minute=0, second=0)
today_msgs = memory.get_messages(after_timestamp=today)

# Analyze by role
stats = memory.get_statistics()
print(f"User messages: {stats['role_counts']['user']}")
print(f"Assistant responses: {stats['role_counts']['assistant']}")

# Find most recent
recent = memory.get_last_n_messages(5)
for msg in recent:
    print(f"[{msg.timestamp}] {msg.role}: {msg.content[:50]}...")
```

### Example 6: Multi-Format Export

```python
# Export to JSON (full data)
memory.save_to_file("backup.json", include_metadata=True)

# Export to text (human-readable)
memory.export_to_text("conversation_log.txt", include_timestamps=True)

# Get as dicts (for API)
messages_for_api = memory.get_messages_as_dicts(limit=50)
```

## Advanced Integration

### Custom Agent Integration

```python
from agent import Agent
from memory import ConversationMemory

class SmartAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = ConversationMemory(max_messages=1000)

    def process(self, user_input: str) -> str:
        # Add to memory
        self.memory.add_message("user", user_input)

        # Get context window for API
        context = self.memory.get_context_window(max_tokens=3000)

        # Process with context
        response = self._call_api(context)

        # Store response
        self.memory.add_message("assistant", response)

        # Auto-save periodically
        if len(self.memory) % 10 == 0:
            self.memory.save_to_file(f"autosave_{self.memory.conversation_id}.json")

        return response
```

### Session Management

```python
class SessionManager:
    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(exist_ok=True)

    def get_session(self, user_id: str) -> ConversationMemory:
        session_file = self.sessions_dir / f"user_{user_id}.json"

        if session_file.exists():
            return ConversationMemory.load_from_file(session_file)
        else:
            return ConversationMemory(
                max_messages=500,
                conversation_id=f"user_{user_id}"
            )

    def save_session(self, user_id: str, memory: ConversationMemory):
        session_file = self.sessions_dir / f"user_{user_id}.json"
        memory.save_to_file(session_file)

    def list_sessions(self) -> List[str]:
        return [f.stem.replace("user_", "")
                for f in self.sessions_dir.glob("user_*.json")]
```

## Thread Safety

All ConversationMemory operations are thread-safe using `threading.RLock()`:

```python
import concurrent.futures

memory = ConversationMemory()

def worker(worker_id: int):
    for i in range(100):
        memory.add_message("user", f"Worker {worker_id}: Message {i}")

# Safe concurrent access
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(worker, range(5))

print(f"Total messages: {len(memory)}")
```

## Performance Considerations

### Memory Usage

- Each message stores: role, content, timestamp, metadata
- Circular buffer automatically manages size
- Typical message: ~100-500 bytes
- 1000 messages ≈ 100-500 KB memory

### Token Counting

- Current implementation: Simple heuristic (4 chars = 1 token)
- For production: Consider using `tiktoken` library
- Accuracy: ±10-20% for estimation purposes

### File I/O

- JSON format with indent=2 for readability
- Use `include_metadata=False` for smaller files
- Consider compression for large archives

## Best Practices

### 1. Set Appropriate Buffer Sizes

```python
# Short-term chat
memory = ConversationMemory(max_messages=50)

# Long-term session
memory = ConversationMemory(max_messages=1000)

# Unlimited (use with caution)
memory = ConversationMemory(max_messages=10000)
```

### 2. Periodic Saves

```python
def process_with_autosave(memory, message, interval=10):
    memory.add_message("user", message)
    response = get_response(message)
    memory.add_message("assistant", response)

    if len(memory) % interval == 0:
        memory.save_to_file(f"autosave_{memory.conversation_id}.json")

    return response
```

### 3. Manage Context Windows

```python
# Always respect API token limits
MAX_CONTEXT = 4000  # Leave room for system prompt and response

context = memory.get_context_window(max_tokens=MAX_CONTEXT)
```

### 4. Clean Up Old Sessions

```python
from datetime import datetime, timedelta

def cleanup_old_sessions(sessions_dir: Path, days: int = 30):
    cutoff = datetime.now() - timedelta(days=days)

    for session_file in sessions_dir.glob("*.json"):
        if session_file.stat().st_mtime < cutoff.timestamp():
            session_file.unlink()
            print(f"Deleted old session: {session_file.name}")
```

### 5. Monitor Costs

```python
def process_with_cost_limit(memory, message, cost_limit=1.0):
    estimated_cost = memory.estimate_cost("gpt-4o")

    if estimated_cost > cost_limit:
        raise ValueError(f"Cost limit exceeded: ${estimated_cost:.4f}")

    # Process message...
```

## Error Handling

The memory system includes comprehensive error handling:

```python
from pathlib import Path

try:
    # Load conversation
    memory = ConversationMemory.load_from_file("conversation.json")
except FileNotFoundError:
    print("Session not found, creating new")
    memory = ConversationMemory()
except json.JSONDecodeError:
    print("Corrupted session file")
    memory = ConversationMemory()

try:
    # Add message with validation
    memory.add_message("invalid_role", "content")
except ValueError as e:
    print(f"Invalid message: {e}")
```

## Testing

Run the test suite:

```bash
# Basic functionality test
python memory.py

# Integration tests
python test_memory_integration.py
```

Expected output: All tests pass with statistics showing successful operations.

## Future Enhancements

Potential improvements for future versions:

1. **Accurate Token Counting**: Integrate `tiktoken` for OpenAI models
2. **Embeddings Support**: Store and search by semantic similarity
3. **Compression**: Compress old messages to save space
4. **Database Backend**: Optional SQLite/PostgreSQL storage
5. **Async Operations**: Async versions of save/load methods
6. **Message Summarization**: Automatic summarization of old context
7. **Multi-Format Search**: Regex, fuzzy matching
8. **Analytics Dashboard**: Web UI for conversation analysis

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please refer to the main framework documentation.

## Changelog

### Version 1.0.0 (2025-11-07)
- Initial release
- Core conversation memory management
- Circular buffer implementation
- JSON persistence
- Search and filtering
- Token counting and cost estimation
- Thread-safe operations
- Text export functionality
- Comprehensive test suite
