"""
Real-world example: Customer Support Chat Bot with Memory Management

This example demonstrates a customer support bot that:
- Maintains conversation history
- Searches past conversations
- Tracks costs
- Saves sessions for later resumption
- Manages context windows for API calls
"""

import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import ConversationMemory, estimate_cost


class CustomerSupportBot:
    """
    Customer support bot with conversation memory management.

    Features:
    - Persistent conversation sessions
    - Search conversation history
    - Cost tracking
    - Context window management
    - Session analytics
    """

    def __init__(self, sessions_dir: str = "support_sessions"):
        """
        Initialize customer support bot.

        Args:
            sessions_dir: Directory to store conversation sessions
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        self.current_memory = None
        self.current_customer_id = None

    def start_session(self, customer_id: str):
        """
        Start or resume a customer support session.

        Args:
            customer_id: Unique customer identifier
        """
        self.current_customer_id = customer_id
        session_file = self.sessions_dir / f"customer_{customer_id}.json"

        if session_file.exists():
            # Resume existing session
            self.current_memory = ConversationMemory.load_from_file(session_file)
            print(f"Resumed session for customer {customer_id}")
            print(f"Previous messages: {len(self.current_memory)}")
        else:
            # Create new session
            self.current_memory = ConversationMemory(
                max_messages=500,
                conversation_id=f"customer_{customer_id}_{datetime.now().strftime('%Y%m%d')}",
                metadata={
                    "customer_id": customer_id,
                    "start_time": datetime.now().isoformat(),
                    "channel": "chat",
                }
            )
            print(f"Started new session for customer {customer_id}")

    def add_message(self, role: str, content: str, metadata: dict = None):
        """
        Add a message to the current session.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata
        """
        if self.current_memory is None:
            raise ValueError("No active session. Call start_session() first.")

        self.current_memory.add_message(role, content, metadata or {})

    def process_customer_message(self, message: str) -> str:
        """
        Process customer message and generate response.

        Args:
            message: Customer's message

        Returns:
            Bot response
        """
        # Add customer message
        self.add_message("user", message, {"timestamp": datetime.now().isoformat()})

        # In a real implementation, this would call an LLM API
        # For this example, we'll generate a simple response
        response = self._generate_response(message)

        # Add bot response
        self.add_message("assistant", response, {"timestamp": datetime.now().isoformat()})

        # Auto-save every 5 messages
        if len(self.current_memory) % 5 == 0:
            self.save_session()

        return response

    def _generate_response(self, message: str) -> str:
        """
        Generate response to customer message.

        In production, this would call an LLM API with conversation context.
        """
        message_lower = message.lower()

        # Simple keyword-based responses for demo
        if "order" in message_lower or "tracking" in message_lower:
            return "I can help you track your order. Could you please provide your order number?"

        elif "return" in message_lower or "refund" in message_lower:
            return "I'd be happy to help with your return. Our return policy allows returns within 30 days. What item would you like to return?"

        elif "account" in message_lower or "password" in message_lower:
            return "For account-related issues, I can help you reset your password or update your information. What would you like to do?"

        elif any(word in message_lower for word in ["hi", "hello", "hey"]):
            return f"Hello! Welcome to customer support. How can I help you today?"

        elif any(word in message_lower for word in ["thank", "thanks"]):
            return "You're welcome! Is there anything else I can help you with?"

        else:
            return "I understand. Let me help you with that. Could you provide more details about your issue?"

    def search_conversation(self, query: str) -> list:
        """
        Search current conversation for specific topics.

        Args:
            query: Search query

        Returns:
            List of matching messages
        """
        if not self.current_memory:
            return []

        return self.current_memory.search_messages(query)

    def get_session_summary(self) -> str:
        """
        Get summary of current session.

        Returns:
            Formatted summary string
        """
        if not self.current_memory:
            return "No active session"

        return self.current_memory.get_summary()

    def get_cost_estimate(self) -> float:
        """
        Get estimated cost for current session.

        Returns:
            Estimated cost in USD
        """
        if not self.current_memory:
            return 0.0

        return self.current_memory.estimate_cost("gpt-4o")

    def save_session(self):
        """Save current session to disk."""
        if not self.current_memory or not self.current_customer_id:
            return

        session_file = self.sessions_dir / f"customer_{self.current_customer_id}.json"
        self.current_memory.save_to_file(session_file)

    def end_session(self):
        """End current session and save."""
        if self.current_memory:
            # Add session metadata
            stats = self.current_memory.get_statistics()
            print("\nSession Summary:")
            print(f"  Customer: {self.current_customer_id}")
            print(f"  Messages: {stats['message_count']}")
            print(f"  Duration: {stats['first_message_time']} to {stats['last_message_time']}")
            print(f"  Estimated cost: ${stats['estimated_cost']:.4f}")

            # Save final session
            self.save_session()

            # Export readable log
            log_file = self.sessions_dir / f"customer_{self.current_customer_id}_log.txt"
            self.current_memory.export_to_text(log_file)

            print(f"\nSession saved to: {self.sessions_dir}")

        self.current_memory = None
        self.current_customer_id = None

    def list_sessions(self) -> list:
        """
        List all customer sessions.

        Returns:
            List of customer IDs with sessions
        """
        sessions = []
        for file in self.sessions_dir.glob("customer_*.json"):
            customer_id = file.stem.replace("customer_", "")
            sessions.append(customer_id)
        return sessions

    def get_session_stats(self, customer_id: str) -> dict:
        """
        Get statistics for a specific customer session.

        Args:
            customer_id: Customer identifier

        Returns:
            Session statistics dictionary
        """
        session_file = self.sessions_dir / f"customer_{customer_id}.json"

        if not session_file.exists():
            return {}

        memory = ConversationMemory.load_from_file(session_file)
        return memory.get_statistics()


def demo_customer_support_session():
    """Demonstrate a complete customer support session."""
    print("=" * 80)
    print("Customer Support Bot - Demo Session")
    print("=" * 80)
    print()

    # Initialize bot
    bot = CustomerSupportBot(sessions_dir="demo_support_sessions")

    # Simulate customer interaction
    customer_id = "CUST12345"

    print(f"Starting session for customer: {customer_id}\n")
    bot.start_session(customer_id)

    # Simulate conversation
    conversation = [
        ("user", "Hi, I need help with my order"),
        ("user", "I want to track order #9876"),
        ("user", "Also, I might need to return one item"),
        ("user", "Thanks for your help!"),
    ]

    print("Conversation:")
    print("-" * 80)

    for role, message in conversation:
        if role == "user":
            print(f"\nCustomer: {message}")
            response = bot.process_customer_message(message)
            print(f"Bot: {response}")

    print("-" * 80)
    print()

    # Show session analytics
    print("\nSession Analytics:")
    print("-" * 80)
    print(bot.get_session_summary())
    print()

    # Search conversation
    print("\nSearching for 'order':")
    print("-" * 80)
    results = bot.search_conversation("order")
    for msg in results:
        print(f"  [{msg.role}] {msg.content}")
    print()

    # Cost tracking
    print("\nCost Tracking:")
    print("-" * 80)
    cost = bot.get_cost_estimate()
    print(f"Estimated session cost: ${cost:.4f}")
    print()

    # End session
    print("\nEnding Session:")
    print("-" * 80)
    bot.end_session()
    print()


def demo_session_management():
    """Demonstrate session management across multiple customers."""
    print("=" * 80)
    print("Session Management Demo")
    print("=" * 80)
    print()

    bot = CustomerSupportBot(sessions_dir="demo_support_sessions")

    # Create multiple customer sessions
    customers = ["CUST001", "CUST002", "CUST003"]

    print("Creating sessions for multiple customers...")
    print()

    for customer_id in customers:
        bot.start_session(customer_id)
        bot.process_customer_message("Hello, I need help")
        bot.end_session()

    # List all sessions
    print("\nActive Sessions:")
    print("-" * 80)
    sessions = bot.list_sessions()
    for session in sessions:
        print(f"  Customer: {session}")
        stats = bot.get_session_stats(session)
        if stats:
            print(f"    Messages: {stats.get('message_count', 0)}")
            print(f"    Cost: ${stats.get('estimated_cost', 0):.4f}")
    print()

    # Cleanup demo files
    print("\nCleaning up demo files...")
    import shutil
    if Path("demo_support_sessions").exists():
        shutil.rmtree("demo_support_sessions")
    print("Done!")
    print()


def demo_context_window_management():
    """Demonstrate context window management for API calls."""
    print("=" * 80)
    print("Context Window Management Demo")
    print("=" * 80)
    print()

    memory = ConversationMemory(max_messages=100)

    # Add a long conversation
    print("Simulating long conversation...")
    for i in range(20):
        memory.add_message("user", f"User message number {i + 1}: " + "x" * 50)
        memory.add_message("assistant", f"Assistant response {i + 1}: " + "y" * 50)

    print(f"Total messages: {len(memory)}")
    print(f"Total tokens: {memory.estimate_tokens()}")
    print()

    # Test different context window sizes
    print("Context Window Sizes:")
    print("-" * 80)

    for max_tokens in [100, 500, 1000, 2000]:
        context = memory.get_context_window(max_tokens=max_tokens)
        actual_tokens = sum(len(msg["content"]) // 4 for msg in context)

        print(f"\nMax tokens: {max_tokens}")
        print(f"  Messages included: {len(context)}")
        print(f"  Actual tokens: ~{actual_tokens}")

        if context:
            first_msg = context[0]["content"][:30]
            last_msg = context[-1]["content"][:30]
            print(f"  First message: {first_msg}...")
            print(f"  Last message: {last_msg}...")

    print()


def main():
    """Run all demo scenarios."""
    print("\n")
    print("=" * 80)
    print("CUSTOMER SUPPORT BOT WITH MEMORY MANAGEMENT")
    print("Real-World Usage Examples")
    print("=" * 80)
    print()

    try:
        # Demo 1: Complete customer support session
        demo_customer_support_session()

        # Demo 2: Multi-customer session management
        demo_session_management()

        # Demo 3: Context window management
        demo_context_window_management()

        print("=" * 80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()

        print("Key features demonstrated:")
        print("  [PASS] Customer session management")
        print("  [PASS] Conversation persistence")
        print("  [PASS] Message search")
        print("  [PASS] Cost tracking")
        print("  [PASS] Context window management")
        print("  [PASS] Session analytics")
        print("  [PASS] Multi-customer support")
        print()

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
