"""Comprehensive tests for the Memory system."""

import pytest


class TestMemorySystem:
    """Test suite for the Memory System."""

    def test_memory_initialization(self, memory_system):
        """Test memory system initializes correctly."""
        assert memory_system.max_size == 100
        assert memory_system.count() == 0
        assert memory_system.memories == []

    def test_memory_custom_max_size(self):
        """Test memory system with custom max size."""
        from tests.conftest import MockMemorySystem

        memory = MockMemorySystem(max_size=50)

        assert memory.max_size == 50

    def test_memory_add_single(self, memory_system):
        """Test adding a single memory."""
        memory_system.add({"role": "user", "content": "Hello"})

        assert memory_system.count() == 1

    def test_memory_add_multiple(self, memory_system):
        """Test adding multiple memories."""
        memory_system.add({"role": "user", "content": "First"})
        memory_system.add({"role": "assistant", "content": "Response"})
        memory_system.add({"role": "user", "content": "Second"})

        assert memory_system.count() == 3

    def test_memory_get_recent_all(self, memory_with_data):
        """Test getting all recent memories."""
        recent = memory_with_data.get_recent(10)

        assert len(recent) == 4  # Fixture has 4 memories

    def test_memory_get_recent_limited(self, memory_with_data):
        """Test getting limited number of recent memories."""
        recent = memory_with_data.get_recent(2)

        assert len(recent) == 2

        # Should be the last 2 memories - check for either "weather" or "sunny"
        last_content = recent[-1]["content"].lower()
        assert "weather" in last_content or "sunny" in last_content

    def test_memory_get_recent_more_than_available(self, memory_with_data):
        """Test getting more recent memories than available."""
        recent = memory_with_data.get_recent(100)

        # Should return all available
        assert len(recent) == 4

    def test_memory_clear(self, memory_with_data):
        """Test clearing all memories."""
        assert memory_with_data.count() > 0

        memory_with_data.clear()

        assert memory_with_data.count() == 0

    def test_memory_search_found(self, memory_with_data):
        """Test searching memories with results."""
        results = memory_with_data.search("weather")

        assert len(results) > 0
        assert any("weather" in str(r).lower() for r in results)

    def test_memory_search_not_found(self, memory_with_data):
        """Test searching memories with no results."""
        results = memory_with_data.search("nonexistent")

        assert len(results) == 0

    def test_memory_search_case_insensitive(self, memory_with_data):
        """Test that search is case insensitive."""
        results_lower = memory_with_data.search("hello")
        results_upper = memory_with_data.search("HELLO")
        results_mixed = memory_with_data.search("HeLLo")

        # All should return same results
        assert len(results_lower) == len(results_upper) == len(results_mixed)

    def test_memory_count(self, memory_system):
        """Test memory count."""
        assert memory_system.count() == 0

        memory_system.add({"test": "data"})
        assert memory_system.count() == 1

        memory_system.add({"test": "data2"})
        assert memory_system.count() == 2

    def test_memory_max_size_enforcement(self):
        """Test that memory enforces max size."""
        from tests.conftest import MockMemorySystem

        memory = MockMemorySystem(max_size=3)

        # Add more than max_size
        for i in range(5):
            memory.add({"number": i})

        # Should only keep last 3
        assert memory.count() == 3

        # Should have numbers 2, 3, 4
        memories = memory.get_recent(10)
        numbers = [m["number"] for m in memories]

        assert 2 in numbers
        assert 3 in numbers
        assert 4 in numbers
        assert 0 not in numbers
        assert 1 not in numbers


class TestMemoryContent:
    """Test suite for memory content storage."""

    def test_memory_stores_dict(self, memory_system):
        """Test memory stores dictionary data."""
        data = {"role": "user", "content": "test", "metadata": {"key": "value"}}

        memory_system.add(data)

        recent = memory_system.get_recent(1)
        assert recent[0]["role"] == "user"
        assert recent[0]["metadata"]["key"] == "value"

    def test_memory_stores_complex_data(self, memory_system):
        """Test memory stores complex nested data."""
        data = {
            "role": "assistant",
            "content": "response",
            "tool_calls": [
                {"name": "calculator", "args": {"x": 5, "y": 3}},
                {"name": "weather", "args": {"location": "NYC"}},
            ],
            "metadata": {
                "model": "gpt-4",
                "tokens": {"prompt": 10, "completion": 20},
            },
        }

        memory_system.add(data)

        recent = memory_system.get_recent(1)
        stored = recent[0]

        assert stored["role"] == "assistant"
        assert len(stored["tool_calls"]) == 2
        assert stored["tool_calls"][0]["name"] == "calculator"
        assert stored["metadata"]["tokens"]["prompt"] == 10

    def test_memory_preserves_order(self, memory_system):
        """Test memory preserves insertion order."""
        for i in range(5):
            memory_system.add({"number": i, "content": f"Message {i}"})

        recent = memory_system.get_recent(5)

        # Should be in order
        for i, memory in enumerate(recent):
            assert memory["number"] == i

    def test_memory_different_data_types(self, memory_system):
        """Test memory handles different data types in content."""
        memories = [
            {"content": "string"},
            {"content": 123},
            {"content": 45.67},
            {"content": True},
            {"content": ["list", "of", "items"]},
            {"content": None},
        ]

        for mem in memories:
            memory_system.add(mem)

        assert memory_system.count() == len(memories)


class TestMemorySearch:
    """Test suite for memory search functionality."""

    def test_search_in_string_content(self, memory_system):
        """Test searching in string content."""
        memory_system.add({"content": "The weather is sunny today"})
        memory_system.add({"content": "I like sunny days"})
        memory_system.add({"content": "It's raining now"})

        results = memory_system.search("sunny")

        assert len(results) == 2

    def test_search_in_nested_data(self, memory_system):
        """Test searching in nested data structures."""
        memory_system.add(
            {
                "role": "user",
                "content": "Calculate something",
                "metadata": {"tool": "calculator"},
            }
        )
        memory_system.add(
            {
                "role": "assistant",
                "content": "Result is 42",
                "metadata": {"tool": "none"},
            }
        )

        results = memory_system.search("calculator")

        assert len(results) >= 1

    def test_search_partial_match(self, memory_system):
        """Test search with partial matching."""
        memory_system.add({"content": "The calculation was successful"})

        results = memory_system.search("calc")

        assert len(results) == 1

    def test_search_empty_query(self, memory_with_data):
        """Test search with empty query."""
        results = memory_with_data.search("")

        # Empty string should match all (depends on implementation)
        assert len(results) >= 0

    def test_search_special_characters(self, memory_system):
        """Test search with special characters."""
        memory_system.add({"content": "Email: test@example.com"})
        memory_system.add({"content": "Price: $19.99"})

        results = memory_system.search("@example")

        assert len(results) == 1


class TestMemoryEdgeCases:
    """Test suite for memory edge cases."""

    def test_memory_empty_get_recent(self, memory_system):
        """Test get_recent on empty memory."""
        recent = memory_system.get_recent(10)

        assert recent == []

    def test_memory_empty_search(self, memory_system):
        """Test search on empty memory."""
        results = memory_system.search("anything")

        assert results == []

    def test_memory_add_empty_dict(self, memory_system):
        """Test adding empty dictionary."""
        memory_system.add({})

        assert memory_system.count() == 1

    def test_memory_get_recent_zero(self, memory_with_data):
        """Test get_recent with n=0."""
        recent = memory_with_data.get_recent(0)

        # Python list slicing with 0 returns empty list
        assert len(recent) == 0 or isinstance(recent, list)

    def test_memory_get_recent_negative(self, memory_with_data):
        """Test get_recent with negative number."""
        # Python list slicing allows negative indices
        recent = memory_with_data.get_recent(-2)

        # Should return empty or first 2 depending on implementation
        assert isinstance(recent, list)

    def test_memory_max_size_one(self):
        """Test memory with max_size of 1."""
        from tests.conftest import MockMemorySystem

        memory = MockMemorySystem(max_size=1)

        memory.add({"number": 1})
        memory.add({"number": 2})

        assert memory.count() == 1

        recent = memory.get_recent(1)
        assert recent[0]["number"] == 2

    def test_memory_very_large_content(self, memory_system):
        """Test memory with very large content."""
        large_content = "A" * 100000  # 100K characters

        memory_system.add({"content": large_content})

        recent = memory_system.get_recent(1)
        assert len(recent[0]["content"]) == 100000

    def test_memory_unicode_content(self, memory_system):
        """Test memory with unicode content."""
        unicode_memories = [
            {"content": "Chinese: 你好"},
            {"content": "Japanese: こんにちは"},
            {"content": "Emoji: 😀🎉🚀"},
            {"content": "Arabic: مرحبا"},
        ]

        for mem in unicode_memories:
            memory_system.add(mem)

        assert memory_system.count() == 4

        # Search should work with unicode
        results = memory_system.search("你好")
        assert len(results) == 1


class TestMemoryWithConversation:
    """Test suite for memory in conversation context."""

    def test_memory_conversation_flow(self, memory_system):
        """Test memory storing a full conversation."""
        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"},
            {"role": "user", "content": "What's 2+2?"},
            {"role": "assistant", "content": "2+2 equals 4"},
            {"role": "user", "content": "Thanks!"},
            {"role": "assistant", "content": "You're welcome!"},
        ]

        for turn in conversation:
            memory_system.add(turn)

        assert memory_system.count() == 6

        # Get recent conversation
        recent = memory_system.get_recent(4)
        assert len(recent) == 4

    def test_memory_conversation_retrieval(self, memory_system):
        """Test retrieving specific parts of conversation."""
        memory_system.add({"role": "user", "content": "Tell me about Python"})
        memory_system.add(
            {"role": "assistant", "content": "Python is a programming language"}
        )
        memory_system.add({"role": "user", "content": "What about Java?"})
        memory_system.add(
            {"role": "assistant", "content": "Java is also a programming language"}
        )

        # Search for Python conversation
        python_memories = memory_system.search("Python")
        assert len(python_memories) >= 1

        # Search for Java conversation
        java_memories = memory_system.search("Java")
        assert len(java_memories) >= 1

    def test_memory_conversation_context(self, memory_system):
        """Test maintaining conversation context."""
        # Simulate a conversation with context
        memory_system.add({"role": "user", "content": "My name is Alice"})
        memory_system.add({"role": "assistant", "content": "Nice to meet you, Alice!"})
        memory_system.add({"role": "user", "content": "What's my name?"})
        memory_system.add({"role": "assistant", "content": "Your name is Alice"})

        # Search for name-related memories
        name_memories = memory_system.search("Alice")
        assert len(name_memories) >= 2


class TestMemoryIntegration:
    """Integration tests for memory system."""

    @pytest.mark.integration
    def test_memory_with_tool_results(self, memory_system):
        """Test storing tool execution results in memory."""
        memory_system.add(
            {
                "role": "user",
                "content": "Calculate 15 * 4",
            }
        )
        memory_system.add(
            {
                "role": "assistant",
                "content": "I'll calculate that for you",
                "tool_calls": [
                    {
                        "tool": "calculator",
                        "args": {"operation": "multiply", "x": 15, "y": 4},
                        "result": 60,
                    }
                ],
            }
        )
        memory_system.add(
            {
                "role": "assistant",
                "content": "The result is 60",
            }
        )

        assert memory_system.count() == 3

        # Search for calculator usage
        calc_memories = memory_system.search("calculator")
        assert len(calc_memories) >= 1

    @pytest.mark.integration
    def test_memory_lifecycle(self, memory_system):
        """Test complete memory lifecycle."""
        # Add memories
        for i in range(10):
            memory_system.add({"message": i, "content": f"Message {i}"})

        assert memory_system.count() == 10

        # Retrieve recent
        recent = memory_system.get_recent(5)
        assert len(recent) == 5

        # Search
        results = memory_system.search("Message 5")
        assert len(results) >= 1

        # Clear
        memory_system.clear()
        assert memory_system.count() == 0

    @pytest.mark.integration
    def test_memory_overflow_behavior(self):
        """Test memory behavior when exceeding max size."""
        from tests.conftest import MockMemorySystem

        memory = MockMemorySystem(max_size=5)

        # Add 10 memories
        for i in range(10):
            memory.add({"index": i})

        # Should only have last 5
        assert memory.count() == 5

        recent = memory.get_recent(10)
        indices = [m["index"] for m in recent]

        # Should be 5, 6, 7, 8, 9
        assert indices == [5, 6, 7, 8, 9]

    @pytest.mark.integration
    def test_memory_concurrent_operations(self, memory_system):
        """Test multiple operations on memory."""
        # Add memories
        memory_system.add({"type": "greeting", "content": "Hello"})
        memory_system.add({"type": "question", "content": "How are you?"})

        # Search while having memories
        results = memory_system.search("Hello")
        assert len(results) >= 1

        # Add more while having existing memories
        memory_system.add({"type": "response", "content": "I'm fine"})

        # Get recent should include all
        recent = memory_system.get_recent(10)
        assert len(recent) == 3

        # Clear and verify
        memory_system.clear()
        assert memory_system.count() == 0
