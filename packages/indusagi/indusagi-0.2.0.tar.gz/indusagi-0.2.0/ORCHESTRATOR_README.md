# Multi-Agent Orchestrator System

> Intelligent routing system for managing multiple specialized AI agents

## Quick Start

```python
from orchestrator import create_orchestrator

# Create orchestrator (one line!)
orchestrator = create_orchestrator()

# Process any query
response = orchestrator.process("What is 25 * 4?")

print(response.response)        # "25 * 4 equals 100"
print(response.agent_used)      # "Math Specialist"
print(response.confidence)      # 0.95
```

## What Is This?

The Multi-Agent Orchestrator is an intelligent system that manages three specialized AI agents and automatically routes queries to the most appropriate agent based on context analysis.

### Three Specialized Agents

1. **General Agent** - General conversations, text manipulation
2. **Math Agent** - Mathematical calculations and operations
3. **Time/Date Agent** - Time and date queries

### Intelligent Routing

The orchestrator analyzes each query and scores it against all agents using keyword matching and weighted scoring. The agent with the highest confidence score handles the query.

## Installation

No additional installation needed. The orchestrator integrates with your existing framework:

```python
# Required files (already in your project)
agent.py            # Agent class
tools.py            # Tool registry
orchestrator.py     # Orchestrator system
```

## Features

- **Intelligent Routing**: Keyword-based scoring with confidence metrics
- **Tool Integration**: All agents share the same tool registry
- **Response Metadata**: Complete information about routing and processing
- **Verbose Mode**: Detailed debugging information
- **Error Handling**: Comprehensive error management
- **Performance Metrics**: Processing time and tool usage tracking
- **Agent Statistics**: Monitor agent usage and performance

## Basic Usage

### Process a Query

```python
from orchestrator import create_orchestrator

orchestrator = create_orchestrator()
response = orchestrator.process("What time is it?")

print(response.response)
```

### With Metadata

```python
response = orchestrator.process("Calculate 100 / 5")

print(f"Response: {response.response}")
print(f"Agent: {response.agent_used}")
print(f"Confidence: {response.routing_decision.confidence_score:.0%}")
print(f"Processing Time: {response.processing_time:.2f}s")
print(f"Tools Used: {response.tools_used}")
```

### Verbose Mode (Debugging)

```python
orchestrator = create_orchestrator(verbose=True)
response = orchestrator.process("What is 2+2?")

# Shows:
# - Query analysis scores
# - Routing decision details
# - Tool execution
# - Processing time
```

## Examples

### Math Queries → Math Agent

```python
queries = [
    "What is 25 * 4?",
    "Calculate 100 divided by 5",
    "Solve: (15 + 25) * 2"
]

for query in queries:
    response = orchestrator.process(query)
    # Routes to Math Specialist
```

### Time/Date Queries → Time/Date Agent

```python
queries = [
    "What time is it?",
    "What's today's date?",
    "Tell me the current time and date"
]

for query in queries:
    response = orchestrator.process(query)
    # Routes to Time & Date Specialist
```

### General Queries → General Agent

```python
queries = [
    "Hello! How are you?",
    "Can you help me?",
    "Convert 'hello' to uppercase"
]

for query in queries:
    response = orchestrator.process(query)
    # Routes to General Assistant
```

## Advanced Usage

### Routing Analysis

```python
# Analyze without processing
decision = orchestrator.route_query("What is 2+2?")

print(f"Would route to: {decision.agent_name}")
print(f"Confidence: {decision.confidence_score:.0%}")
print(f"Keywords: {decision.matched_keywords}")
print(f"Reasoning: {decision.reasoning}")

# View all scores
for agent_type, score in decision.scores.items():
    print(f"{agent_type.value}: {score:.2f}")
```

### Direct Agent Access

```python
from orchestrator import AgentType

# Get specific agent
math_agent = orchestrator.get_agent(AgentType.MATH)

# Use directly
response = math_agent.process_with_tools(
    "What is 50 * 2?",
    tools=registry.schemas,
    tool_executor=registry
)
```

### Statistics

```python
stats = orchestrator.get_agent_stats()

print(f"Total Agents: {stats['total_agents']}")
print(f"Total Tools: {stats['total_tools_available']}")

for agent in stats['agents']:
    print(f"{agent['name']}: {agent['message_history_length']} messages")
```

### History Management

```python
# Clear all histories
orchestrator.clear_all_histories()

# Clear specific agent
math_agent = orchestrator.get_agent(AgentType.MATH)
math_agent.clear_history()
```

## Testing

### Run Quick Start Demo

```bash
python quick_start_orchestrator.py
```

Shows basic usage with minimal setup.

### Run Full Demo

```bash
python demo_orchestrator.py
```

Comprehensive demonstration with 7 test scenarios:
1. Basic query processing
2. Routing analysis with metrics
3. Verbose debugging mode
4. Agent statistics
5. Direct agent access
6. Error handling
7. Performance metrics

### Run Integration Tests

```bash
python test_orchestrator_integration.py
```

Comprehensive test suite with 10 tests covering:
- Imports and initialization
- Agent setup
- Tool integration
- Routing system
- Query processing
- Response metadata
- Statistics
- History management
- Error handling

## Response Structure

Every response includes complete metadata:

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

Routing decision includes:

```python
@dataclass
class RoutingDecision:
    agent_type: AgentType                  # Selected agent
    agent_name: str                        # Human-readable name
    confidence_score: float                # 0.0 to 1.0
    matched_keywords: List[str]            # Keywords that matched
    reasoning: str                         # Human-readable explanation
    scores: Dict[AgentType, float]         # All agent scores
```

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY='your-api-key-here'

# Optional (defaults shown)
export OPENAI_MODEL='gpt-4o'
export OPENAI_MAX_TOKENS='1024'
export OPENAI_TEMPERATURE='0.7'
```

### Custom Configuration

```python
from agent import AgentConfig
from orchestrator import MultiAgentOrchestrator

config = AgentConfig(
    model="gpt-4o",
    temperature=0.3,
    max_tokens=2048
)

orchestrator = MultiAgentOrchestrator(
    config=config,
    verbose=True
)
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, request, jsonify
from orchestrator import create_orchestrator

app = Flask(__name__)
orchestrator = create_orchestrator()

@app.route('/query', methods=['POST'])
def handle_query():
    query = request.json.get('query')
    response = orchestrator.process(query)

    return jsonify({
        'response': response.response,
        'agent': response.agent_used,
        'confidence': response.routing_decision.confidence_score
    })
```

### Command-Line Interface

```python
orchestrator = create_orchestrator()

while True:
    query = input("You: ")
    if query.lower() in ['quit', 'exit']:
        break

    response = orchestrator.process(query)
    print(f"[{response.agent_used}]: {response.response}")
```

## Documentation

### Quick Reference

- **ORCHESTRATOR_README.md** (this file) - Quick start guide
- **ORCHESTRATOR_GUIDE.md** - Complete comprehensive guide
- **ORCHESTRATOR_IMPLEMENTATION_SUMMARY.md** - Implementation details

### Code Documentation

- **orchestrator.py** - Main implementation with inline docs
- **demo_orchestrator.py** - Usage demonstrations
- **quick_start_orchestrator.py** - Simple examples
- **test_orchestrator_integration.py** - Integration tests

## Architecture

```
MultiAgentOrchestrator
    │
    ├── Intelligent Routing System
    │   ├── Keyword Extraction
    │   ├── Weighted Scoring (1.0-5.0)
    │   ├── Score Normalization (0.0-1.0)
    │   ├── Agent Selection
    │   └── Reasoning Generation
    │
    ├── Specialized Agents
    │   ├── General Agent
    │   ├── Math Agent
    │   └── Time/Date Agent
    │
    └── Tool Registry (Shared)
        ├── calculator
        ├── get_time, get_date, get_datetime
        └── text manipulation tools
```

## Performance

Typical response times on standard hardware:

- **General queries**: 0.5-1.5s
- **Math queries**: 0.8-2.0s (includes tool execution)
- **Time/Date queries**: 0.6-1.8s (includes tool execution)

Factors:
- Model selection (GPT-4 vs GPT-3.5-turbo)
- Network latency to OpenAI API
- Tool execution time
- Message history length

## Error Handling

```python
try:
    response = orchestrator.process(query)
    if response.error:
        print(f"Error: {response.error}")
        # Handle error
    else:
        print(f"Success: {response.response}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Always handle errors** - Check `response.error`
2. **Monitor performance** - Track `response.processing_time`
3. **Use verbose mode in development** - `verbose=True`
4. **Clear histories regularly** - `clear_all_histories()`
5. **Validate inputs** - Check query before processing
6. **Log routing decisions** - For analysis and debugging
7. **Test with diverse queries** - Ensure routing works correctly

## Extending

### Add Custom Agent

```python
# 1. Define agent type
class AgentType(Enum):
    GENERAL = "general"
    MATH = "math"
    TIME_DATE = "time_date"
    CUSTOM = "custom"  # New

# 2. Add routing keywords
AgentType.CUSTOM: {
    r'\bcustom_keyword\b': 5.0,
}

# 3. Initialize agent
self.agents[AgentType.CUSTOM] = Agent(
    name="Custom Agent",
    role="Custom specialist",
    config=self.config,
    system_prompt="..."
)
```

### Register Custom Tool

```python
from tools import registry

@registry.register
def custom_tool(param: str) -> str:
    """Custom tool description."""
    return f"Processed: {param}"

# All agents automatically have access
```

## Troubleshooting

### Wrong Agent Selected

**Problem**: Query routed to incorrect agent

**Solution**:
1. Enable verbose mode to see scoring
2. Check routing keywords weights
3. Add more specific keywords

```python
decision = orchestrator.route_query("your query")
print(decision.scores)  # See all scores
print(decision.matched_keywords)  # See matches
```

### Tools Not Being Used

**Problem**: Agent doesn't call available tools

**Solution**:
1. Verify tools in registry: `registry.list_tools()`
2. Check system prompt encourages tool usage
3. Try more explicit tool-related query

### Slow Response Times

**Problem**: Processing takes too long

**Solution**:
1. Use faster model (gpt-3.5-turbo)
2. Reduce max_tokens in config
3. Clear agent histories regularly

```python
config = AgentConfig(
    model="gpt-3.5-turbo",
    max_tokens=512
)
orchestrator = MultiAgentOrchestrator(config=config)
```

## Files Summary

| File | Size | Purpose |
|------|------|---------|
| `orchestrator.py` | 36 KB | Core implementation |
| `demo_orchestrator.py` | 10 KB | Comprehensive demos |
| `quick_start_orchestrator.py` | 4 KB | Quick start examples |
| `test_orchestrator_integration.py` | 12 KB | Integration tests |
| `ORCHESTRATOR_GUIDE.md` | 22 KB | Complete documentation |
| `ORCHESTRATOR_IMPLEMENTATION_SUMMARY.md` | 19 KB | Implementation details |
| `ORCHESTRATOR_README.md` | This file | Quick reference |

**Total**: ~100 KB of production-ready code and documentation

## Support

For help:
1. Read this README for quick start
2. Check ORCHESTRATOR_GUIDE.md for detailed info
3. Run demo_orchestrator.py to see examples
4. Review code comments in orchestrator.py

## License

MIT License - See LICENSE file for details

## Next Steps

1. **Get Started**: Run `python quick_start_orchestrator.py`
2. **Learn More**: Read `ORCHESTRATOR_GUIDE.md`
3. **See Demos**: Run `python demo_orchestrator.py`
4. **Test**: Run `python test_orchestrator_integration.py`
5. **Integrate**: Add to your application using examples above

---

**Status**: Production-ready and fully tested

**Last Updated**: 2025

**Author**: AI indus-agents Team
