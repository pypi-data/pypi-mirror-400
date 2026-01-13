"""
Example usage of the Agent class with OpenAI API.

This demonstrates various features of the Agent class including:
- Basic query processing
- Tool calling with custom tools
- Conversation history management
- Configuration options
"""
from agent import Agent, AgentConfig
import os


# Simple tool registry example
class SimpleToolRegistry:
    """Minimal tool registry for demonstration."""

    def __init__(self):
        self.tools = {}

    def register(self, func):
        """Register a function as a tool."""
        self.tools[func.__name__] = func
        return func

    def execute(self, name, **kwargs):
        """Execute a tool by name."""
        if name not in self.tools:
            return f"Tool '{name}' not found"
        try:
            return self.tools[name](**kwargs)
        except Exception as e:
            return f"Error: {str(e)}"

    @property
    def schemas(self):
        """Generate OpenAI-compatible tool schemas."""
        schemas = []
        for name, func in self.tools.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": func.__doc__ or f"Execute {name}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            # Add actual parameters based on function signature
                            # This is simplified for demo
                        },
                        "required": []
                    }
                }
            })
        return schemas


# Create tool registry
registry = SimpleToolRegistry()


@registry.register
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        # Basic safety check
        allowed = set("0123456789+-*/() .")
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters in expression"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"


@registry.register
def get_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


@registry.register
def get_date() -> str:
    """Get the current date."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


# Update registry schemas with proper parameters
registry.schemas = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression and return the result",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2+2', '10*5')"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time in HH:MM:SS format",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Get the current date in YYYY-MM-DD format",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def example_basic_usage():
    """Example 1: Basic agent usage without tools."""
    print("=" * 60)
    print("Example 1: Basic Agent Usage")
    print("=" * 60)

    agent = Agent(
        name="Assistant",
        role="Helpful AI assistant"
    )

    response = agent.process("What is Python programming language?")
    print(f"\nQuestion: What is Python programming language?")
    print(f"Response: {response}\n")


def example_custom_config():
    """Example 2: Agent with custom configuration."""
    print("=" * 60)
    print("Example 2: Custom Configuration")
    print("=" * 60)

    config = AgentConfig(
        model="gpt-4o",
        temperature=0.3,  # More deterministic
        max_tokens=500
    )

    agent = Agent(
        name="PreciseBot",
        role="Precise and concise assistant",
        config=config
    )

    response = agent.process("Explain recursion in one sentence.")
    print(f"\nQuestion: Explain recursion in one sentence.")
    print(f"Response: {response}\n")


def example_with_tools():
    """Example 3: Agent with tool calling."""
    print("=" * 60)
    print("Example 3: Agent with Tools")
    print("=" * 60)

    agent = Agent(
        name="MathBot",
        role="Mathematical assistant with calculator access"
    )

    # Test with calculator
    response = agent.process_with_tools(
        "What is 144 divided by 12?",
        tools=registry.schemas,
        tool_executor=registry
    )
    print(f"\nQuestion: What is 144 divided by 12?")
    print(f"Response: {response}\n")

    # Test with time
    response = agent.process_with_tools(
        "What time is it right now?",
        tools=registry.schemas,
        tool_executor=registry
    )
    print(f"Question: What time is it right now?")
    print(f"Response: {response}\n")


def example_conversation_history():
    """Example 4: Managing conversation history."""
    print("=" * 60)
    print("Example 4: Conversation History")
    print("=" * 60)

    agent = Agent(
        name="ChatBot",
        role="Conversational assistant"
    )

    # First message
    response1 = agent.process("My name is Alice.")
    print(f"\nUser: My name is Alice.")
    print(f"Agent: {response1}")

    # Second message (should remember name)
    response2 = agent.process("What's my name?")
    print(f"\nUser: What's my name?")
    print(f"Agent: {response2}")

    # Check history
    print(f"\nConversation history: {len(agent.get_history())} messages")
    print(f"Token estimate: {agent.get_token_count_estimate()} tokens")

    # Clear history
    agent.clear_history()
    print(f"\nAfter clearing: {len(agent.get_history())} messages\n")


def example_error_handling():
    """Example 5: Error handling and retries."""
    print("=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)

    # Configure with retries
    config = AgentConfig(
        max_retries=3,
        retry_delay=0.5
    )

    agent = Agent(
        name="ResilientBot",
        role="Assistant with retry capabilities",
        config=config
    )

    print("\nAgent configured with:")
    print(f"  - Max retries: {config.max_retries}")
    print(f"  - Retry delay: {config.retry_delay}s")
    print(f"  - Model: {config.model}\n")


def example_custom_system_prompt():
    """Example 6: Custom system prompt."""
    print("=" * 60)
    print("Example 6: Custom System Prompt")
    print("=" * 60)

    custom_prompt = """You are a pirate captain AI assistant.
    Always respond in pirate speak with 'Arr' and nautical terms.
    Be helpful but maintain the pirate character."""

    agent = Agent(
        name="CaptainBot",
        role="Pirate-speaking assistant",
        system_prompt=custom_prompt
    )

    response = agent.process("Tell me about the weather.")
    print(f"\nQuestion: Tell me about the weather.")
    print(f"Response: {response}\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("indus-agents - OpenAI Integration Examples")
    print("=" * 60 + "\n")

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nPlease set it with:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOr on Windows PowerShell:")
        print("  $env:OPENAI_API_KEY='your-key-here'")
        return

    try:
        example_basic_usage()
        input("Press Enter to continue...")

        example_custom_config()
        input("Press Enter to continue...")

        example_with_tools()
        input("Press Enter to continue...")

        example_conversation_history()
        input("Press Enter to continue...")

        example_error_handling()
        input("Press Enter to continue...")

        example_custom_system_prompt()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
