"""
Multi-Agent Orchestrator System for indus-agents

This module provides an intelligent orchestration system that manages multiple
specialized AI agents and routes queries to the most appropriate agent based on
context, keywords, and query analysis.

Features:
    - Multiple specialized agents (General, Math, Time/Date)
    - Intelligent routing with keyword-based scoring
    - Tool registry integration for all agents
    - Agent selection metrics and reasoning
    - Verbose debugging mode
    - Response attribution
    - Comprehensive error handling
    - Production-ready design

Architecture:
    Orchestrator
        |-- General Agent (general queries, text manipulation)
        |-- Math Agent (calculations, mathematical operations)
        |-- Time/Date Agent (time queries, date operations)

Author: indus-agents
License: MIT
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime

# Import our existing framework components
from indusagi.agent import Agent, AgentConfig
from indusagi.tools import registry


class AgentType(Enum):
    """Enumeration of available specialized agent types."""
    GENERAL = "general"
    MATH = "math"
    TIME_DATE = "time_date"


@dataclass
class RoutingDecision:
    """
    Encapsulates the routing decision with scoring metrics.

    Attributes:
        agent_type: The selected agent type
        agent_name: Human-readable name of the selected agent
        confidence_score: Routing confidence (0.0 to 1.0)
        matched_keywords: Keywords that matched in the query
        reasoning: Human-readable explanation of the decision
        scores: Raw scores for each agent type
    """
    agent_type: AgentType
    agent_name: str
    confidence_score: float
    matched_keywords: List[str]
    reasoning: str
    scores: Dict[AgentType, float]


@dataclass
class OrchestratorResponse:
    """
    Complete response from the orchestrator with metadata.

    Attributes:
        response: The actual response text from the agent
        agent_used: Name of the agent that handled the query
        agent_type: Type of the agent used
        routing_decision: Full routing decision details
        processing_time: Time taken to process (seconds)
        tools_used: List of tools that were executed
        error: Error message if processing failed
    """
    response: str
    agent_used: str
    agent_type: AgentType
    routing_decision: RoutingDecision
    processing_time: float
    tools_used: List[str]
    error: Optional[str] = None


class MultiAgentOrchestrator:
    """
    Intelligent orchestrator that manages multiple specialized AI agents.

    The orchestrator analyzes incoming queries and routes them to the most
    appropriate specialized agent based on keyword matching, context analysis,
    and scoring algorithms. All agents have access to the shared tool registry.

    Attributes:
        agents: Dictionary mapping agent types to Agent instances
        config: Configuration for agent initialization
        verbose: Enable detailed logging for debugging
        routing_keywords: Keyword patterns for each agent type

    Example:
        >>> orchestrator = MultiAgentOrchestrator(verbose=True)
        >>> response = orchestrator.process("What is 25 * 4?")
        >>> print(response.response)
        "The result of 25 * 4 is 100."
        >>> print(response.agent_used)
        "Math Specialist"
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        verbose: bool = False
    ) -> None:
        """
        Initialize the multi-agent orchestrator.

        Args:
            config: Configuration for agent initialization (uses defaults if None)
            verbose: Enable verbose logging for debugging

        Raises:
            ValueError: If OPENAI_API_KEY is not set
        """
        self.config = config or AgentConfig.from_env()
        self.verbose = verbose
        self.agents: Dict[AgentType, Agent] = {}

        # Define routing keywords for each agent type
        self.routing_keywords = self._initialize_routing_keywords()

        # Initialize specialized agents
        self._initialize_agents()

        if self.verbose:
            print("[Orchestrator] Initialized with agents:", list(self.agents.keys()))

    def _initialize_routing_keywords(self) -> Dict[AgentType, Dict[str, float]]:
        """
        Initialize keyword patterns and weights for routing decisions.

        Returns:
            Dictionary mapping agent types to keyword-weight mappings

        Note:
            Higher weights indicate stronger relevance to the agent type.
            Weights range from 1.0 (weak match) to 5.0 (strong match).
        """
        return {
            AgentType.MATH: {
                # Strong math indicators (weight: 5.0)
                r'\bcalculat(e|ion|or)\b': 5.0,
                r'\bmath(s|ematical)?\b': 5.0,
                r'\bsolve\b': 4.0,
                r'\bequation\b': 4.0,

                # Math operations (weight: 4.0)
                r'\b(add|subtract|multiply|divide|sum|difference|product|quotient)\b': 4.0,
                r'\bwhat is\s+\d+': 4.0,

                # Math symbols and numbers (weight: 3.0)
                r'[\d\+\-\*/\(\)]+': 3.0,
                r'\b\d+\s*(plus|minus|times|divided by)\s*\d+\b': 5.0,
            },

            AgentType.TIME_DATE: {
                # Strong time/date indicators (weight: 5.0)
                r'\b(time|date|datetime|clock)\b': 5.0,
                r'\b(today|now|current)\b': 4.0,
                r'\bwhat.*time\b': 5.0,
                r'\bwhat.*date\b': 5.0,

                # Temporal references (weight: 4.0)
                r'\b(yesterday|tomorrow|hour|minute|second|day|week|month|year)\b': 4.0,
                r'\b(morning|afternoon|evening|night)\b': 3.0,

                # Time-related questions (weight: 4.0)
                r'\bwhen\b': 3.0,
                r'\bhow long\b': 3.0,
            },

            AgentType.GENERAL: {
                # General conversation patterns (weight: 2.0)
                r'\b(hello|hi|hey|greetings)\b': 2.0,
                r'\b(help|assist|support)\b': 2.0,
                r'\b(explain|describe|tell me)\b': 2.0,
                r'\b(what|how|why|who|where)\b': 1.5,

                # Text manipulation (weight: 3.0)
                r'\b(uppercase|lowercase|reverse|titlecase)\b': 3.0,
                r'\b(count|words|characters|lines)\b': 3.0,
            }
        }

    def _initialize_agents(self) -> None:
        """
        Initialize all specialized agents with custom system prompts.

        Creates three specialized agents:
            - General Agent: Handles general queries and text manipulation
            - Math Agent: Handles mathematical operations and calculations
            - Time/Date Agent: Handles time and date queries

        Each agent has access to the shared tool registry.
        """
        # General Agent: Handles broad range of queries
        self.agents[AgentType.GENERAL] = Agent(
            name="General Assistant",
            role="General purpose AI assistant",
            config=self.config,
            system_prompt=(
                "You are a helpful general-purpose AI assistant. "
                "You can handle a wide variety of queries including general questions, "
                "text manipulation, and providing information. "
                "Use available tools when appropriate to provide accurate responses. "
                "Be conversational, helpful, and clear in your responses."
            )
        )

        # Math Agent: Specialized for mathematical operations
        self.agents[AgentType.MATH] = Agent(
            name="Math Specialist",
            role="Mathematical computation expert",
            config=self.config,
            system_prompt=(
                "You are a specialized mathematics assistant focused on calculations "
                "and mathematical operations. When users ask mathematical questions, "
                "ALWAYS use the calculator tool to compute accurate results. "
                "Explain your calculations clearly and show your work. "
                "For complex problems, break them down into steps. "
                "Always prioritize accuracy and precision in your mathematical responses."
            )
        )

        # Time/Date Agent: Specialized for temporal queries
        self.agents[AgentType.TIME_DATE] = Agent(
            name="Time & Date Specialist",
            role="Time and date information expert",
            config=self.config,
            system_prompt=(
                "You are a specialized assistant for time and date queries. "
                "ALWAYS use the available time and date tools (get_time, get_date, get_datetime) "
                "to provide current, accurate information. Never guess or estimate times or dates. "
                "Format your responses clearly and include relevant context when helpful. "
                "If asked about time zones or date calculations, be explicit about your assumptions."
            )
        )

        if self.verbose:
            for agent_type, agent in self.agents.items():
                print(f"[Orchestrator] Initialized {agent_type.value}: {agent.name}")

    def _analyze_query(self, query: str) -> Dict[AgentType, float]:
        """
        Analyze query and compute relevance scores for each agent type.

        This method uses keyword matching with weighted scoring to determine
        which agent is most suitable for handling the query.

        Args:
            query: User's input query

        Returns:
            Dictionary mapping agent types to relevance scores (0.0 to 1.0)

        Algorithm:
            1. Convert query to lowercase for case-insensitive matching
            2. For each agent type, check all keyword patterns
            3. Accumulate weighted scores for matching patterns
            4. Normalize scores to 0.0-1.0 range
            5. Apply minimum threshold and fallback logic
        """
        query_lower = query.lower()
        scores = {agent_type: 0.0 for agent_type in AgentType}

        # Calculate raw scores for each agent type
        for agent_type, keywords in self.routing_keywords.items():
            score = 0.0
            for pattern, weight in keywords.items():
                if re.search(pattern, query_lower):
                    score += weight

            scores[agent_type] = score

        # Normalize scores to 0.0-1.0 range
        max_score = max(scores.values()) if max(scores.values()) > 0 else 1.0
        normalized_scores = {
            agent_type: score / max_score
            for agent_type, score in scores.items()
        }

        # If no clear match, give slight preference to general agent
        if max_score < 2.0:
            normalized_scores[AgentType.GENERAL] = max(
                normalized_scores[AgentType.GENERAL],
                0.3  # Minimum baseline for general agent
            )

        if self.verbose:
            print(f"[Orchestrator] Query analysis scores: {normalized_scores}")

        return normalized_scores

    def _get_matched_keywords(
        self,
        query: str,
        agent_type: AgentType
    ) -> List[str]:
        """
        Get list of keywords that matched for a specific agent type.

        Args:
            query: User's input query
            agent_type: Agent type to check keywords for

        Returns:
            List of matched keyword patterns
        """
        query_lower = query.lower()
        matched = []

        for pattern in self.routing_keywords[agent_type].keys():
            if re.search(pattern, query_lower):
                # Extract the readable part of the pattern (remove regex syntax)
                readable_pattern = re.sub(r'[\\^\$\(\)\[\]\{\}\|\*\+\?]', '', pattern)
                readable_pattern = readable_pattern.replace('b', '').strip()
                if readable_pattern:
                    matched.append(readable_pattern)

        return matched[:5]  # Return top 5 matches

    def route_query(self, query: str) -> RoutingDecision:
        """
        Determine which agent should handle the query.

        This method implements the core routing logic, analyzing the query
        and selecting the most appropriate agent based on multiple factors.

        Args:
            query: User's input query

        Returns:
            RoutingDecision with complete routing information

        Decision Process:
            1. Analyze query for keyword matches
            2. Calculate confidence scores for each agent
            3. Select agent with highest score
            4. Generate human-readable reasoning
            5. Return complete decision with metadata
        """
        # Get relevance scores for each agent
        scores = self._analyze_query(query)

        # Select agent with highest score
        selected_type = max(scores.items(), key=lambda x: x[1])[0]
        confidence = scores[selected_type]

        # Get matched keywords
        matched_keywords = self._get_matched_keywords(query, selected_type)

        # Generate reasoning
        reasoning = self._generate_routing_reasoning(
            query, selected_type, confidence, matched_keywords, scores
        )

        decision = RoutingDecision(
            agent_type=selected_type,
            agent_name=self.agents[selected_type].name,
            confidence_score=confidence,
            matched_keywords=matched_keywords,
            reasoning=reasoning,
            scores=scores
        )

        if self.verbose:
            print(f"\n[Orchestrator] Routing Decision:")
            print(f"  Selected Agent: {decision.agent_name} ({decision.agent_type.value})")
            print(f"  Confidence: {decision.confidence_score:.2f}")
            print(f"  Matched Keywords: {decision.matched_keywords}")
            print(f"  Reasoning: {decision.reasoning}")
            print(f"  All Scores: {decision.scores}\n")

        return decision

    def _generate_routing_reasoning(
        self,
        query: str,
        selected_type: AgentType,
        confidence: float,
        matched_keywords: List[str],
        all_scores: Dict[AgentType, float]
    ) -> str:
        """
        Generate human-readable explanation for routing decision.

        Args:
            query: Original user query
            selected_type: Selected agent type
            confidence: Confidence score (0.0 to 1.0)
            matched_keywords: Keywords that matched
            all_scores: All agent scores

        Returns:
            Human-readable reasoning string
        """
        agent_name = self.agents[selected_type].name

        if confidence >= 0.8:
            confidence_text = "high confidence"
        elif confidence >= 0.5:
            confidence_text = "moderate confidence"
        else:
            confidence_text = "low confidence (fallback)"

        if matched_keywords:
            keywords_text = f" Matched keywords: {', '.join(matched_keywords)}."
        else:
            keywords_text = " No specific keywords matched, using default routing."

        # Add score comparison if there were close alternatives
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[1][1] > 0.3:
            runner_up = sorted_scores[1][0]
            score_diff = confidence - sorted_scores[1][1]
            comparison = (
                f" (Note: {runner_up.value} agent scored {sorted_scores[1][1]:.2f}, "
                f"difference of {score_diff:.2f})"
            )
        else:
            comparison = ""

        reasoning = (
            f"Routed to {agent_name} with {confidence_text} "
            f"(score: {confidence:.2f}).{keywords_text}{comparison}"
        )

        return reasoning

    def process(self, query: str, use_tools: bool = True) -> OrchestratorResponse:
        """
        Process a query through the orchestration system.

        This is the main entry point for the orchestrator. It routes the query
        to the appropriate agent and returns a comprehensive response with
        metadata about the processing.

        Args:
            query: User's input query
            use_tools: Whether to allow tool usage (default: True)

        Returns:
            OrchestratorResponse with result and metadata

        Example:
            >>> orchestrator = MultiAgentOrchestrator(verbose=True)
            >>> response = orchestrator.process("What is 15 * 23?")
            >>> print(response.response)
            "15 * 23 equals 345"
            >>> print(response.agent_used)
            "Math Specialist"
            >>> print(response.routing_decision.confidence_score)
            0.95
        """
        start_time = datetime.now()
        tools_used = []
        error = None

        try:
            # Step 1: Route the query
            routing_decision = self.route_query(query)
            selected_agent = self.agents[routing_decision.agent_type]

            if self.verbose:
                print(f"[Orchestrator] Processing query with {selected_agent.name}")

            # Step 2: Process with the selected agent
            if use_tools:
                # Create a wrapper to track tool usage
                original_execute = registry.execute

                def tracked_execute(name: str, **kwargs) -> Any:
                    tools_used.append(name)
                    if self.verbose:
                        print(f"[Orchestrator] Tool used: {name}")
                    return original_execute(name, **kwargs)

                # Temporarily replace execute method
                registry.execute = tracked_execute

                try:
                    response_text = selected_agent.process_with_tools(
                        user_input=query,
                        tools=registry.schemas,
                        tool_executor=registry,
                        max_turns=10
                    )
                finally:
                    # Restore original execute method
                    registry.execute = original_execute
            else:
                response_text = selected_agent.process(query)

            # Step 3: Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            if self.verbose:
                print(f"[Orchestrator] Processing completed in {processing_time:.2f}s")
                if tools_used:
                    print(f"[Orchestrator] Tools used: {tools_used}")

        except Exception as e:
            # Error handling
            error = str(e)
            response_text = f"I apologize, but I encountered an error while processing your request: {error}"
            routing_decision = self.route_query(query)
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            if self.verbose:
                print(f"[Orchestrator] ERROR: {error}")

        # Build and return comprehensive response
        return OrchestratorResponse(
            response=response_text,
            agent_used=routing_decision.agent_name,
            agent_type=routing_decision.agent_type,
            routing_decision=routing_decision,
            processing_time=processing_time,
            tools_used=tools_used,
            error=error
        )

    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the orchestrator and its agents.

        Returns:
            Dictionary containing orchestrator statistics

        Example:
            >>> stats = orchestrator.get_agent_stats()
            >>> print(stats['total_agents'])
            3
            >>> print(stats['agents'][0]['name'])
            'General Assistant'
        """
        stats = {
            "total_agents": len(self.agents),
            "agent_types": [t.value for t in self.agents.keys()],
            "agents": [],
            "total_tools_available": len(registry.list_tools()),
            "available_tools": registry.list_tools()
        }

        for agent_type, agent in self.agents.items():
            agent_info = {
                "type": agent_type.value,
                "name": agent.name,
                "role": agent.role,
                "model": agent.config.model,
                "message_history_length": len(agent.messages),
                "token_estimate": agent.get_token_count_estimate()
            }
            stats["agents"].append(agent_info)

        return stats

    def clear_all_histories(self) -> None:
        """
        Clear conversation history for all agents.

        Useful for starting fresh or managing memory usage.

        Example:
            >>> orchestrator.clear_all_histories()
            >>> stats = orchestrator.get_agent_stats()
            >>> print(stats['agents'][0]['message_history_length'])
            0
        """
        for agent in self.agents.values():
            agent.clear_history()

        if self.verbose:
            print("[Orchestrator] Cleared all agent histories")

    def get_agent(self, agent_type: AgentType) -> Agent:
        """
        Get direct access to a specific agent.

        Args:
            agent_type: Type of agent to retrieve

        Returns:
            The requested Agent instance

        Raises:
            KeyError: If agent type not found

        Example:
            >>> math_agent = orchestrator.get_agent(AgentType.MATH)
            >>> response = math_agent.process("What is 2+2?")
        """
        return self.agents[agent_type]

    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        return (
            f"MultiAgentOrchestrator("
            f"agents={len(self.agents)}, "
            f"tools={len(registry.list_tools())}, "
            f"verbose={self.verbose})"
        )


# ============================================================================
# Convenience Functions
# ============================================================================


def create_orchestrator(verbose: bool = False) -> MultiAgentOrchestrator:
    """
    Factory function to create a configured orchestrator.

    Args:
        verbose: Enable verbose logging

    Returns:
        Configured MultiAgentOrchestrator instance

    Example:
        >>> orchestrator = create_orchestrator(verbose=True)
        >>> response = orchestrator.process("What time is it?")
    """
    return MultiAgentOrchestrator(verbose=verbose)


# ============================================================================
# Testing and Demonstration
# ============================================================================


if __name__ == "__main__":
    """
    Test suite and demonstration of the multi-agent orchestrator.
    """
    print("=" * 80)
    print("Multi-Agent Orchestrator - Test Suite")
    print("=" * 80)

    try:
        # Create orchestrator with verbose mode
        print("\n[TEST 1] Creating orchestrator...")
        orchestrator = create_orchestrator(verbose=True)
        print(f"Created: {orchestrator}")

        # Test 2: General queries
        print("\n" + "=" * 80)
        print("[TEST 2] Testing General Agent")
        print("=" * 80)

        test_queries_general = [
            "Hello! How are you?",
            "Can you help me with something?",
            "Convert 'hello world' to uppercase"
        ]

        for query in test_queries_general:
            print(f"\nQuery: {query}")
            response = orchestrator.process(query)
            print(f"Agent: {response.agent_used}")
            print(f"Response: {response.response}")
            print(f"Confidence: {response.routing_decision.confidence_score:.2f}")
            print(f"Processing time: {response.processing_time:.2f}s")
            if response.tools_used:
                print(f"Tools used: {response.tools_used}")

        # Test 3: Math queries
        print("\n" + "=" * 80)
        print("[TEST 3] Testing Math Agent")
        print("=" * 80)

        test_queries_math = [
            "What is 25 * 4?",
            "Calculate 100 divided by 5",
            "Solve: (15 + 25) * 2"
        ]

        for query in test_queries_math:
            print(f"\nQuery: {query}")
            response = orchestrator.process(query)
            print(f"Agent: {response.agent_used}")
            print(f"Response: {response.response}")
            print(f"Confidence: {response.routing_decision.confidence_score:.2f}")
            print(f"Processing time: {response.processing_time:.2f}s")
            if response.tools_used:
                print(f"Tools used: {response.tools_used}")

        # Test 4: Time/Date queries
        print("\n" + "=" * 80)
        print("[TEST 4] Testing Time/Date Agent")
        print("=" * 80)

        test_queries_time = [
            "What time is it?",
            "What's today's date?",
            "Tell me the current date and time"
        ]

        for query in test_queries_time:
            print(f"\nQuery: {query}")
            response = orchestrator.process(query)
            print(f"Agent: {response.agent_used}")
            print(f"Response: {response.response}")
            print(f"Confidence: {response.routing_decision.confidence_score:.2f}")
            print(f"Processing time: {response.processing_time:.2f}s")
            if response.tools_used:
                print(f"Tools used: {response.tools_used}")

        # Test 5: Get statistics
        print("\n" + "=" * 80)
        print("[TEST 5] Orchestrator Statistics")
        print("=" * 80)

        stats = orchestrator.get_agent_stats()
        print(f"\nTotal Agents: {stats['total_agents']}")
        print(f"Agent Types: {stats['agent_types']}")
        print(f"Total Tools Available: {stats['total_tools_available']}")
        print(f"Available Tools: {stats['available_tools']}")

        print("\nAgent Details:")
        for agent_info in stats['agents']:
            print(f"\n  {agent_info['name']}:")
            print(f"    Type: {agent_info['type']}")
            print(f"    Role: {agent_info['role']}")
            print(f"    Model: {agent_info['model']}")
            print(f"    Messages: {agent_info['message_history_length']}")
            print(f"    Tokens: {agent_info['token_estimate']}")

        # Test 6: Clear histories
        print("\n" + "=" * 80)
        print("[TEST 6] Clear All Histories")
        print("=" * 80)

        orchestrator.clear_all_histories()
        stats_after = orchestrator.get_agent_stats()
        total_messages = sum(
            agent['message_history_length']
            for agent in stats_after['agents']
        )
        print(f"Total messages after clearing: {total_messages}")

        print("\n" + "=" * 80)
        print("All tests completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        print("\nMake sure OPENAI_API_KEY is set in your environment:")
        print("  export OPENAI_API_KEY='your-key-here'")


# ============================================================================
# Usage Examples and Integration Guide
# ============================================================================

"""
USAGE EXAMPLES
==============

1. Basic Usage
--------------
from orchestrator import create_orchestrator

# Create orchestrator
orchestrator = create_orchestrator(verbose=False)

# Process a query
response = orchestrator.process("What is 15 * 23?")
print(response.response)


2. With Verbose Mode
--------------------
orchestrator = create_orchestrator(verbose=True)

# Detailed logging will show:
# - Routing decisions
# - Confidence scores
# - Tool usage
# - Processing times

response = orchestrator.process("What time is it?")


3. Accessing Response Metadata
-------------------------------
response = orchestrator.process("Calculate 100 / 5")

print(f"Response: {response.response}")
print(f"Agent: {response.agent_used}")
print(f"Type: {response.agent_type}")
print(f"Confidence: {response.routing_decision.confidence_score}")
print(f"Time: {response.processing_time}s")
print(f"Tools: {response.tools_used}")


4. Manual Agent Selection
--------------------------
from orchestrator import AgentType

# Get specific agent directly
math_agent = orchestrator.get_agent(AgentType.MATH)
result = math_agent.process_with_tools(
    "What is 50 * 2?",
    tools=registry.schemas,
    tool_executor=registry
)


5. Routing Analysis
--------------------
# Analyze routing without processing
decision = orchestrator.route_query("What is 2+2?")

print(f"Selected: {decision.agent_name}")
print(f"Confidence: {decision.confidence_score}")
print(f"Keywords: {decision.matched_keywords}")
print(f"Reasoning: {decision.reasoning}")
print(f"All scores: {decision.scores}")


6. Statistics and Monitoring
-----------------------------
stats = orchestrator.get_agent_stats()

print(f"Total agents: {stats['total_agents']}")
print(f"Total tools: {stats['total_tools_available']}")

for agent in stats['agents']:
    print(f"{agent['name']}: {agent['message_history_length']} messages")


7. History Management
---------------------
# Clear all agent histories
orchestrator.clear_all_histories()

# Or clear individual agent history
math_agent = orchestrator.get_agent(AgentType.MATH)
math_agent.clear_history()


8. Custom Configuration
-----------------------
from agent import AgentConfig

# Create custom config
config = AgentConfig(
    model="gpt-4o",
    temperature=0.3,
    max_tokens=2048
)

# Use with orchestrator
orchestrator = MultiAgentOrchestrator(
    config=config,
    verbose=True
)


9. Error Handling
-----------------
response = orchestrator.process("invalid query")

if response.error:
    print(f"Error occurred: {response.error}")
    print(f"Partial response: {response.response}")


10. Integration with Web Application
-------------------------------------
from flask import Flask, request, jsonify

app = Flask(__name__)
orchestrator = create_orchestrator(verbose=False)

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data.get('query')

    response = orchestrator.process(query)

    return jsonify({
        'response': response.response,
        'agent': response.agent_used,
        'confidence': response.routing_decision.confidence_score,
        'tools_used': response.tools_used,
        'processing_time': response.processing_time
    })


ROUTING ALGORITHM
=================

The orchestrator uses a multi-stage routing algorithm:

1. Keyword Extraction
   - Extract keywords from query using regex patterns
   - Case-insensitive matching
   - Support for complex patterns (numbers, operators, temporal words)

2. Score Calculation
   - Each matched keyword contributes weighted score
   - Weights range from 1.0 (weak) to 5.0 (strong)
   - Scores accumulated per agent type

3. Normalization
   - Scores normalized to 0.0-1.0 range
   - Ensures fair comparison across agent types

4. Agent Selection
   - Agent with highest score selected
   - Minimum threshold of 0.3 for general agent (fallback)
   - Confidence score reflects certainty of routing

5. Reasoning Generation
   - Human-readable explanation created
   - Includes matched keywords and score comparisons
   - Helps with debugging and transparency


ADDING NEW AGENTS
==================

To add a new specialized agent:

1. Define Agent Type
--------------------
class AgentType(Enum):
    GENERAL = "general"
    MATH = "math"
    TIME_DATE = "time_date"
    WEATHER = "weather"  # New agent type


2. Add Routing Keywords
------------------------
def _initialize_routing_keywords(self):
    keywords = {
        # ... existing keywords ...
        AgentType.WEATHER: {
            r'\bweather\b': 5.0,
            r'\btemperature\b': 4.0,
            r'\bforecast\b': 4.0,
            r'\b(rain|snow|sunny|cloudy)\b': 3.0,
        }
    }
    return keywords


3. Initialize Agent
-------------------
def _initialize_agents(self):
    # ... existing agents ...

    self.agents[AgentType.WEATHER] = Agent(
        name="Weather Specialist",
        role="Weather information expert",
        config=self.config,
        system_prompt="You are a weather information specialist..."
    )


4. Register Weather Tools
--------------------------
from tools import registry

@registry.register
def get_weather(location: str) -> str:
    '''Get weather for a location.'''
    # Implementation here
    return weather_data


PERFORMANCE OPTIMIZATION
========================

1. Caching
   - Cache routing decisions for similar queries
   - Cache tool results when appropriate
   - Use LRU cache for expensive computations

2. Parallel Processing
   - Process independent queries in parallel
   - Batch API calls when possible
   - Use async/await for I/O operations

3. Memory Management
   - Regularly clear agent histories
   - Limit message history length
   - Monitor token usage

4. Model Selection
   - Use faster models (gpt-3.5-turbo) for simple queries
   - Reserve powerful models (gpt-4) for complex tasks
   - Implement model selection based on query complexity


TESTING CHECKLIST
==================

Before deployment:

[ ] All agent types properly initialized
[ ] Routing keywords comprehensive and tested
[ ] Tool integration working correctly
[ ] Error handling covers edge cases
[ ] Verbose mode provides useful debugging info
[ ] Response metadata complete and accurate
[ ] Statistics tracking functional
[ ] History management working
[ ] Performance acceptable
[ ] Documentation complete


TROUBLESHOOTING
===============

Issue: Agent selection incorrect
Solution: Review and adjust keyword weights in routing_keywords

Issue: Tools not being used
Solution: Check system prompts encourage tool usage

Issue: Slow processing times
Solution: Reduce max_tokens, use faster model, or optimize tools

Issue: Memory usage high
Solution: Clear histories regularly, limit history length

Issue: Routing confidence low
Solution: Add more specific keywords for the domain


PRODUCTION DEPLOYMENT
=====================

Recommendations for production:

1. Monitoring
   - Log all routing decisions
   - Track agent performance metrics
   - Monitor tool usage patterns
   - Set up alerts for errors

2. Rate Limiting
   - Implement per-user rate limits
   - Add cooldown for expensive operations
   - Queue requests during high load

3. Security
   - Validate all user inputs
   - Sanitize tool arguments
   - Implement authentication/authorization
   - Use secure API key management

4. Scalability
   - Use connection pooling
   - Implement request queuing
   - Consider distributed deployment
   - Cache common queries

5. Testing
   - Unit tests for routing logic
   - Integration tests for agent interactions
   - Load testing for performance
   - End-to-end tests for workflows
"""
