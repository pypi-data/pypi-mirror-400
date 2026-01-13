# Conversation Memory - Quick Start Guide

## 5-Minute Setup

### Installation
No additional dependencies needed! Uses existing Pydantic from the framework.

### Basic Usage

```python
from memory import ConversationMemory

# Create memory
memory = ConversationMemory(max_messages=1000)

# Add messages
memory.add_message("user", "Hello!")
memory.add_message("assistant", "Hi there!")

# Get messages
messages = memory.get_messages()
print(f"Total: {len(messages)}")
```

## Common Patterns

### Pattern 1: Simple Chat Bot

```python
from memory import ConversationMemory

memory = ConversationMemory(max_messages=100)

def chat(user_input):
    memory.add_message("user", user_input)
    # Your LLM call here
    response = "Response from LLM"
    memory.add_message("assistant", response)
    return response
```

### Pattern 2: Persistent Sessions

```python
from pathlib import Path
from memory import ConversationMemory

def get_session(user_id):
    file = Path(f"sessions/{user_id}.json")
    if file.exists():
        return ConversationMemory.load_from_file(file)
    return ConversationMemory(max_messages=500)

def save_session(user_id, memory):
    memory.save_to_file(f"sessions/{user_id}.json")
```

### Pattern 3: Context Window Management

```python
# Get messages that fit in token budget
context = memory.get_context_window(max_tokens=4000)

# Use with API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        *context  # Recent messages that fit
    ]
)
```

### Pattern 4: Search and Analytics

```python
# Search conversations
results = memory.search_messages("Python")
print(f"Found {len(results)} messages about Python")

# Get statistics
stats = memory.get_statistics()
print(f"Messages: {stats['message_count']}")
print(f"Cost: ${stats['estimated_cost']:.4f}")

# Get summary
print(memory.get_summary())
```

### Pattern 5: Integration with Agent

```python
from agent import Agent
from memory import ConversationMemory

class SmartAgent(Agent):
    def __init__(self, name, role):
        super().__init__(name, role)
        self.memory = ConversationMemory(max_messages=1000)

    def process(self, user_input):
        self.memory.add_message("user", user_input)
        response = super().process(user_input)
        self.memory.add_message("assistant", response)

        # Auto-save every 10 messages
        if len(self.memory) % 10 == 0:
            self.memory.save_to_file("autosave.json")

        return response
```

## Essential Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `add_message(role, content)` | Add message | `memory.add_message("user", "Hi")` |
| `get_messages(limit=N)` | Get last N messages | `memory.get_messages(limit=10)` |
| `search_messages(query)` | Search content | `memory.search_messages("Python")` |
| `get_statistics()` | Get stats | `stats = memory.get_statistics()` |
| `save_to_file(path)` | Save to JSON | `memory.save_to_file("chat.json")` |
| `load_from_file(path)` | Load from JSON | `ConversationMemory.load_from_file("chat.json")` |
| `clear()` | Clear all | `memory.clear()` |
| `estimate_cost(model)` | Get cost | `cost = memory.estimate_cost("gpt-4o")` |

## Filtering Options

```python
# By role
user_msgs = memory.get_messages(role="user")
assistant_msgs = memory.get_messages(role="assistant")

# By time
from datetime import datetime, timedelta
today = datetime.now() - timedelta(days=1)
recent = memory.get_messages(after_timestamp=today)

# Last N messages
last_10 = memory.get_messages(limit=10)
```

## File Operations

```python
# Save to JSON (full data)
memory.save_to_file("conversation.json")

# Load from JSON
memory = ConversationMemory.load_from_file("conversation.json")

# Export to text (human-readable)
memory.export_to_text("conversation.txt")
```

## Cost Tracking

```python
# Estimate tokens
tokens = memory.estimate_tokens()

# Estimate cost
cost = memory.estimate_cost("gpt-4o")
print(f"Estimated cost: ${cost:.4f}")

# Check before API call
if memory.estimate_cost("gpt-4o") > 1.0:
    print("Warning: Conversation cost exceeds $1")
```

## Circular Buffer

```python
# Memory automatically manages size
memory = ConversationMemory(max_messages=100)

# Add 150 messages - only last 100 kept
for i in range(150):
    memory.add_message("user", f"Message {i}")

print(len(memory))  # 100 (max_messages)

# Check total processed
stats = memory.get_statistics()
print(stats['total_messages_processed'])  # 150
```

## Thread Safety

```python
# Safe to use from multiple threads
from concurrent.futures import ThreadPoolExecutor

memory = ConversationMemory()

def add_messages(worker_id):
    for i in range(100):
        memory.add_message("user", f"Worker {worker_id}: {i}")

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(add_messages, range(5))

print(f"Total: {len(memory)}")  # All messages added safely
```

## Common Pitfalls

### ❌ Don't: Modify messages directly

```python
messages = memory.get_messages()
messages[0].content = "Changed"  # Changes Message object
# But doesn't update memory!
```

### ✅ Do: Add new messages

```python
# To "edit", add a correction message
memory.add_message("assistant", "Correction: ...")
```

### ❌ Don't: Forget to save

```python
memory.add_message("user", "Important message")
# If process crashes, message lost
```

### ✅ Do: Auto-save periodically

```python
if len(memory) % 10 == 0:
    memory.save_to_file("autosave.json")
```

### ❌ Don't: Ignore token limits

```python
# May exceed API context window
all_messages = memory.get_messages()
```

### ✅ Do: Use context window

```python
context = memory.get_context_window(max_tokens=4000)
```

## Testing

Run the demos:

```bash
# Core functionality
python memory.py

# Integration tests
python test_memory_integration.py

# Real-world example
python examples/memory_example.py
```

## Complete Example

```python
from memory import ConversationMemory
from pathlib import Path

# Setup
session_dir = Path("sessions")
session_dir.mkdir(exist_ok=True)

def chat_session(user_id):
    # Load or create session
    session_file = session_dir / f"{user_id}.json"

    if session_file.exists():
        memory = ConversationMemory.load_from_file(session_file)
        print(f"Resumed session: {len(memory)} messages")
    else:
        memory = ConversationMemory(max_messages=500)
        print("New session started")

    # Chat loop
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        # Add user message
        memory.add_message("user", user_input)

        # Get AI response (mock for example)
        response = f"Echo: {user_input}"
        memory.add_message("assistant", response)

        print(f"Bot: {response}")

        # Auto-save every 5 messages
        if len(memory) % 5 == 0:
            memory.save_to_file(session_file)
            print("[Saved]")

    # Final save
    memory.save_to_file(session_file)

    # Show stats
    print("\nSession Stats:")
    print(memory.get_summary())

# Run
if __name__ == "__main__":
    chat_session("user_123")
```

## Help & Documentation

- **Full docs**: `MEMORY_SYSTEM_README.md`
- **Implementation**: `MEMORY_IMPLEMENTATION_SUMMARY.md`
- **Examples**: `examples/memory_example.py`
- **Tests**: `test_memory_integration.py`

## Quick Troubleshooting

**Q: Messages not saving?**
A: Call `memory.save_to_file(path)` explicitly

**Q: Running out of memory?**
A: Set lower `max_messages` limit

**Q: Search not finding messages?**
A: Search is case-insensitive by default

**Q: Token count seems wrong?**
A: It's an estimate. Use tiktoken for accuracy.

**Q: Can I use with async?**
A: Yes, but methods are sync. Consider async wrapper.

---

**Next Steps:**
1. Read `MEMORY_SYSTEM_README.md` for complete API
2. Run `python examples/memory_example.py` for demo
3. Integrate with your Agent class
4. Test with `python test_memory_integration.py`

**Ready to use!** 🚀
