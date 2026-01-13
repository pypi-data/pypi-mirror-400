# Multi-Agent Orchestrator System - Complete Guide

## Overview

The Multi-Agent Orchestrator is an intelligent routing system that manages multiple specialized AI agents and directs queries to the most appropriate agent based on context analysis and keyword matching.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MultiAgentOrchestrator                │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │          Intelligent Routing System             │    │
│  │  • Keyword matching with weighted scoring       │    │
│  │  • Confidence calculation                       │    │
│  │  • Agent selection logic                        │    │
│  └────────────────────────────────────────────────┘    │
│                          │                               │
│         ┌────────────────┼────────────────┐            │
│         ▼                ▼                ▼            │
│  ┌───────────┐   ┌──────────┐   ┌──────────────┐     │
│  │  General  │   │   Math   │   │  Time/Date   │     │
│  │  Agent    │   │  Agent   │   │   Agent      │     │
│  └───────────┘   └──────────┘   └──────────────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘            │
│                          ▼                              │
│              ┌─────────────────────┐                   │
│              │   Tool Registry     │                   │
│              │  • calculator       │                   │
│              │  • get_time         │                   │
│              │  • get_date         │                   │
│              │  • text_uppercase   │                   │
│              │  • text_lowercase   │                   │
│              │  • text_reverse     │                   │
│              │  • text_count_words │                   │
│              │  • text_title_case  │                   │
│              │  • get_datetime     │                   │
│              └─────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

## Features

### 1. Three Specialized Agents

#### **General Agent**
- Handles general conversations and queries
- Text manipulation operations
- Broad knowledge questions
- Default fallback for ambiguous queries

**System Prompt:**
> "You are a helpful general-purpose AI assistant. You can handle a wide variety of queries including general questions, text manipulation, and providing information..."

#### **Math Agent**
- Mathematical calculations and operations
- Expression evaluation
- Arithmetic problem solving
- Always uses the calculator tool for accuracy

**System Prompt:**
> "You are a specialized mathematics assistant focused on calculations and mathematical operations. When users ask mathematical questions, ALWAYS use the calculator tool..."

#### **Time/Date Agent**
- Current time queries
- Date information
- Temporal questions
- Always uses time/date tools for accuracy

**System Prompt:**
> "You are a specialized assistant for time and date queries. ALWAYS use the available time and date tools (get_time, get_date, get_datetime)..."

### 2. Intelligent Routing System

The orchestrator uses a sophisticated multi-stage routing algorithm:

#### **Stage 1: Keyword Extraction**
- Regex-based pattern matching
- Case-insensitive matching
- Support for complex patterns (numbers, operators, temporal words)

#### **Stage 2: Weighted Scoring**
Each matched keyword contributes a weighted score:
- **5.0**: Strong match (e.g., "calculate", "math", "time")
- **4.0**: Moderate match (e.g., "solve", "today", "add")
- **3.0**: Weak match (e.g., "when", "number pattern")
- **2.0**: Generic match (e.g., "help", "explain")

#### **Stage 3: Score Normalization**
- Scores normalized to 0.0-1.0 range
- Fair comparison across agent types
- Minimum threshold of 0.3 for general agent (fallback)

#### **Stage 4: Agent Selection**
- Agent with highest score selected
- Confidence score reflects routing certainty
- Fallback to general agent if no clear winner

#### **Stage 5: Reasoning Generation**
- Human-readable explanation of decision
- Includes matched keywords and score comparisons
- Aids debugging and transparency

### 3. Response Metadata

Every response includes comprehensive metadata:

```python
@dataclass
class OrchestratorResponse:
    response: str                          # Actual response text
    agent_used: str                        # Agent name
    agent_type: AgentType                  # Agent type enum
    routing_decision: RoutingDecision      # Complete routing info
    processing_time: float                 # Time in seconds
    tools_used: List[str]                  # Tools that were called
    error: Optional[str]                   # Error if any
```

### 4. Routing Decision Details

```python
@dataclass
class RoutingDecision:
    agent_type: AgentType                  # Selected agent
    agent_name: str                        # Human-readable name
    confidence_score: float                # 0.0 to 1.0
    matched_keywords: List[str]            # Keywords that matched
    reasoning: str                         # Explanation
    scores: Dict[AgentType, float]         # All agent scores
```

## Quick Start

### Basic Usage

```python
from orchestrator import create_orchestrator

# Create orchestrator
orchestrator = create_orchestrator(verbose=False)

# Process a query
response = orchestrator.process("What is 25 * 4?")

print(response.response)        # "The result of 25 * 4 is 100."
print(response.agent_used)      # "Math Specialist"
print(response.confidence)      # 0.95
```

### With Verbose Mode (Debugging)

```python
# Enable detailed logging
orchestrator = create_orchestrator(verbose=True)

response = orchestrator.process("What time is it?")

# Output includes:
# [Orchestrator] Query analysis scores: {...}
# [Orchestrator] Routing Decision:
#   Selected Agent: Time & Date Specialist (time_date)
#   Confidence: 0.92
#   Matched Keywords: ['time', 'what time']
#   ...
# [Time & Date Specialist] Using tool: get_time with args: {}
# [Orchestrator] Processing completed in 1.23s
```

### Accessing Response Metadata

```python
response = orchestrator.process("Calculate 100 / 5")

# Response text
print(f"Response: {response.response}")

# Agent information
print(f"Agent: {response.agent_used}")
print(f"Type: {response.agent_type.value}")

# Routing metrics
decision = response.routing_decision
print(f"Confidence: {decision.confidence_score:.2%}")
print(f"Keywords: {decision.matched_keywords}")
print(f"Reasoning: {decision.reasoning}")

# Performance metrics
print(f"Processing Time: {response.processing_time:.2f}s")
print(f"Tools Used: {response.tools_used}")

# All agent scores
for agent_type, score in decision.scores.items():
    print(f"{agent_type.value}: {score:.2f}")
```

### Direct Agent Access

```python
from orchestrator import AgentType

# Get specific agent
math_agent = orchestrator.get_agent(AgentType.MATH)

# Use directly with tools
response = math_agent.process_with_tools(
    "What is 50 * 2?",
    tools=registry.schemas,
    tool_executor=registry
)
```

### Routing Analysis (Without Processing)

```python
# Analyze routing without executing
decision = orchestrator.route_query("What is 2+2?")

print(f"Would route to: {decision.agent_name}")
print(f"Confidence: {decision.confidence_score:.2%}")
print(f"Keywords: {decision.matched_keywords}")
print(f"Reasoning: {decision.reasoning}")

# View all scores
for agent_type, score in decision.scores.items():
    print(f"{agent_type.value}: {score:.2f}")
```

## Statistics and Monitoring

### Get Orchestrator Statistics

```python
stats = orchestrator.get_agent_stats()

print(f"Total Agents: {stats['total_agents']}")
print(f"Agent Types: {stats['agent_types']}")
print(f"Total Tools: {stats['total_tools_available']}")
print(f"Available Tools: {stats['available_tools']}")

# Per-agent statistics
for agent in stats['agents']:
    print(f"\n{agent['name']}:")
    print(f"  Type: {agent['type']}")
    print(f"  Model: {agent['model']}")
    print(f"  Messages: {agent['message_history_length']}")
    print(f"  Tokens: {agent['token_estimate']}")
```

### History Management

```python
# Clear all agent histories
orchestrator.clear_all_histories()

# Clear individual agent history
math_agent = orchestrator.get_agent(AgentType.MATH)
math_agent.clear_history()
```

## Configuration

### Custom Configuration

```python
from agent import AgentConfig
from orchestrator import MultiAgentOrchestrator

# Create custom config
config = AgentConfig(
    model="gpt-4o",
    temperature=0.3,      # Lower for more deterministic
    max_tokens=2048,
    top_p=0.9,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    max_retries=3,
    retry_delay=1.0
)

# Use with orchestrator
orchestrator = MultiAgentOrchestrator(
    config=config,
    verbose=True
)
```

### Environment Variables

```bash
# Required
export OPENAI_API_KEY='your-api-key-here'

# Optional (defaults shown)
export OPENAI_MODEL='gpt-4o'
export OPENAI_MAX_TOKENS='1024'
export OPENAI_TEMPERATURE='0.7'
```

## Routing Examples

### Math Queries (→ Math Agent)

```python
queries = [
    "What is 25 * 4?",                    # Strong: numbers + operator
    "Calculate 100 divided by 5",         # Strong: "calculate"
    "Solve: (15 + 25) * 2",              # Strong: "solve" + math
    "What is 50 plus 30?",               # Strong: numbers + "plus"
    "How much is 12 times 12?",          # Moderate: "how much" + numbers
]

for query in queries:
    response = orchestrator.process(query)
    # All route to Math Specialist with high confidence
```

### Time/Date Queries (→ Time/Date Agent)

```python
queries = [
    "What time is it?",                   # Strong: "time"
    "What's today's date?",               # Strong: "date" + "today"
    "Tell me the current time and date",  # Strong: "time" + "date"
    "What day is it?",                    # Moderate: temporal reference
    "When is it?",                        # Weak: "when"
]

for query in queries:
    response = orchestrator.process(query)
    # All route to Time & Date Specialist
```

### General Queries (→ General Agent)

```python
queries = [
    "Hello! How are you?",                # Greeting
    "Can you help me?",                   # General help
    "Convert 'hello' to uppercase",       # Text manipulation
    "Explain quantum physics",            # Explanation request
    "Tell me about Python",               # General knowledge
]

for query in queries:
    response = orchestrator.process(query)
    # All route to General Assistant
```

## Advanced Usage

### Custom Tool Integration

```python
from tools import registry

# Register custom tool
@registry.register
def custom_tool(param: str) -> str:
    """Custom tool description."""
    return f"Processed: {param}"

# All agents automatically have access
response = orchestrator.process("Use the custom tool with 'test'")
```

### Error Handling

```python
response = orchestrator.process("some query")

if response.error:
    print(f"Error occurred: {response.error}")
    print(f"Partial response: {response.response}")
    # Handle error...
else:
    print(f"Success: {response.response}")
```

### Performance Monitoring

```python
import time

# Track response times
queries = ["query1", "query2", "query3"]
times = []

for query in queries:
    start = time.time()
    response = orchestrator.process(query)
    elapsed = time.time() - start
    times.append(elapsed)

    print(f"Query: {query}")
    print(f"  Response time: {elapsed:.2f}s")
    print(f"  Agent: {response.agent_used}")

avg_time = sum(times) / len(times)
print(f"\nAverage response time: {avg_time:.2f}s")
```

## Adding New Agents

To add a new specialized agent:

### 1. Define Agent Type

```python
class AgentType(Enum):
    GENERAL = "general"
    MATH = "math"
    TIME_DATE = "time_date"
    WEATHER = "weather"  # New agent
```

### 2. Add Routing Keywords

```python
def _initialize_routing_keywords(self):
    return {
        # ... existing keywords ...
        AgentType.WEATHER: {
            r'\bweather\b': 5.0,
            r'\btemperature\b': 4.0,
            r'\bforecast\b': 4.0,
            r'\b(rain|snow|sunny|cloudy)\b': 3.0,
            r'\b(hot|cold|warm|cool)\b': 2.0,
        }
    }
```

### 3. Initialize Agent

```python
def _initialize_agents(self):
    # ... existing agents ...

    self.agents[AgentType.WEATHER] = Agent(
        name="Weather Specialist",
        role="Weather information expert",
        config=self.config,
        system_prompt=(
            "You are a weather information specialist. "
            "Use available weather tools to provide accurate "
            "weather data and forecasts..."
        )
    )
```

### 4. Register Tools (Optional)

```python
from tools import registry

@registry.register
def get_weather(location: str) -> str:
    """Get weather for a location."""
    # Implementation
    return weather_data
```

## Integration Examples

### Web Application (Flask)

```python
from flask import Flask, request, jsonify
from orchestrator import create_orchestrator

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
        'agent_type': response.agent_type.value,
        'confidence': response.routing_decision.confidence_score,
        'tools_used': response.tools_used,
        'processing_time': response.processing_time,
        'error': response.error
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### Command-Line Interface

```python
from orchestrator import create_orchestrator

def main():
    orchestrator = create_orchestrator(verbose=False)

    print("Multi-Agent Assistant")
    print("Type 'quit' to exit\n")

    while True:
        query = input("You: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            break

        if not query:
            continue

        response = orchestrator.process(query)

        print(f"[{response.agent_used}]: {response.response}")
        print(f"(Confidence: {response.routing_decision.confidence_score:.0%})")
        print()

if __name__ == '__main__':
    main()
```

### Batch Processing

```python
from orchestrator import create_orchestrator
import csv

orchestrator = create_orchestrator(verbose=False)

# Process queries from CSV
results = []

with open('queries.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        query = row['query']
        response = orchestrator.process(query)

        results.append({
            'query': query,
            'response': response.response,
            'agent': response.agent_used,
            'confidence': response.routing_decision.confidence_score,
            'processing_time': response.processing_time
        })

# Save results
with open('results.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
```

## Testing

### Run Demo

```bash
python demo_orchestrator.py
```

This runs 7 comprehensive demonstrations:
1. Basic query processing
2. Routing analysis with metrics
3. Verbose debugging mode
4. Agent statistics and monitoring
5. Direct agent access
6. Error handling
7. Performance metrics

### Run Unit Tests

```bash
# Test orchestrator initialization
python -c "from orchestrator import create_orchestrator; o = create_orchestrator(); print('✓ Success')"

# Test agent routing
python -c "from orchestrator import create_orchestrator; o = create_orchestrator(); d = o.route_query('What is 2+2?'); print(f'Routed to: {d.agent_name}')"

# Test processing
python -c "from orchestrator import create_orchestrator; o = create_orchestrator(); r = o.process('Hello!'); print(f'Response: {r.response}')"
```

## Troubleshooting

### Issue: Wrong Agent Selected

**Symptom:** Query routed to incorrect agent

**Solutions:**
1. Check routing keywords weights
2. Add more specific keywords for domain
3. Review query patterns
4. Enable verbose mode to see scoring

```python
# Debug routing
decision = orchestrator.route_query("your query")
print(decision.scores)  # See all scores
print(decision.matched_keywords)  # See what matched
```

### Issue: Tools Not Being Used

**Symptom:** Agent doesn't call available tools

**Solutions:**
1. Check system prompt encourages tool usage
2. Verify tools are in registry
3. Ensure tool schemas are correct
4. Try more explicit tool-related query

```python
# Verify tools available
from tools import registry
print(registry.list_tools())

# Check agent has access
response = orchestrator.process("Use calculator for 2+2")
print(response.tools_used)  # Should show ['calculator']
```

### Issue: Slow Response Times

**Symptom:** Processing takes too long

**Solutions:**
1. Reduce max_tokens in config
2. Use faster model (gpt-3.5-turbo)
3. Clear agent histories regularly
4. Optimize tool implementations

```python
# Use faster config
from agent import AgentConfig

config = AgentConfig(
    model="gpt-3.5-turbo",
    max_tokens=512,
    temperature=0.5
)

orchestrator = MultiAgentOrchestrator(config=config)
```

### Issue: High Memory Usage

**Symptom:** Memory grows over time

**Solutions:**
1. Clear histories regularly
2. Limit message history length
3. Monitor token usage

```python
# Regular cleanup
orchestrator.clear_all_histories()

# Check memory usage
stats = orchestrator.get_agent_stats()
for agent in stats['agents']:
    print(f"{agent['name']}: {agent['token_estimate']} tokens")
```

## Best Practices

### 1. Always Handle Errors

```python
try:
    response = orchestrator.process(query)
    if response.error:
        # Handle error case
        log_error(response.error)
        return fallback_response
except Exception as e:
    # Handle unexpected errors
    log_exception(e)
    return error_response
```

### 2. Monitor Performance

```python
# Track metrics
response = orchestrator.process(query)

metrics = {
    'query': query,
    'agent': response.agent_used,
    'confidence': response.routing_decision.confidence_score,
    'processing_time': response.processing_time,
    'tools_used': len(response.tools_used),
    'error': response.error is not None
}

# Log or store metrics
log_metrics(metrics)
```

### 3. Use Verbose Mode in Development

```python
# Development
orchestrator = create_orchestrator(verbose=True)

# Production
orchestrator = create_orchestrator(verbose=False)
```

### 4. Regular History Cleanup

```python
# After N queries or time period
if query_count % 100 == 0:
    orchestrator.clear_all_histories()
```

### 5. Validate Inputs

```python
def process_safe(query: str):
    if not query or not query.strip():
        return "Please provide a valid query."

    if len(query) > 1000:
        return "Query too long. Please keep under 1000 characters."

    response = orchestrator.process(query)
    return response.response
```

## API Reference

### Classes

- **MultiAgentOrchestrator**: Main orchestrator class
- **AgentType**: Enum of available agent types
- **RoutingDecision**: Routing decision with metrics
- **OrchestratorResponse**: Complete response with metadata

### Functions

- **create_orchestrator(verbose)**: Factory function for orchestrator
- **process(query, use_tools)**: Process query through system
- **route_query(query)**: Analyze routing without processing
- **get_agent_stats()**: Get statistics
- **clear_all_histories()**: Clear all agent histories
- **get_agent(agent_type)**: Get specific agent

## Performance Benchmarks

Typical response times (on standard hardware):

- **General queries**: 0.5-1.5s
- **Math queries**: 0.8-2.0s (includes tool execution)
- **Time/Date queries**: 0.6-1.8s (includes tool execution)

Factors affecting performance:
- Model selection (GPT-4 slower than GPT-3.5-turbo)
- Network latency to OpenAI API
- Tool execution time
- Message history length

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Review code comments in orchestrator.py
- Run demo_orchestrator.py for examples
- Check agent.py and tools.py for core functionality
