# Test Suite for indus-agents

## Overview

This directory contains a comprehensive test suite for the indus-agents with 255 tests covering all major components.

## Quick Start

### Run All Tests
```bash
pytest tests/
```

### Run All Tests with Output
```bash
pytest tests/ -v
```

### Run Tests Quietly
```bash
pytest tests/ -q
```

## Test Files

- `conftest.py` - Fixtures and test configuration
- `test_agent.py` - Agent class tests (31 tests)
- `test_tools.py` - Tool system tests (45 tests)
- `test_orchestrator.py` - Orchestrator tests (33 tests)
- `test_memory.py` - Memory system tests (37 tests)
- `test_cli.py` - CLI interface tests (46 tests)
- `test_config.py` - Configuration tests (38 tests)
- `test_integration.py` - Integration tests (25 tests)

## Running Specific Tests

### Run Single Test File
```bash
pytest tests/test_agent.py
```

### Run Specific Test Class
```bash
pytest tests/test_agent.py::TestAgent
```

### Run Specific Test Method
```bash
pytest tests/test_agent.py::TestAgent::test_agent_initialization_with_defaults
```

### Run Tests by Marker
```bash
# Run integration tests only
pytest tests/ -m integration

# Skip integration tests
pytest tests/ -m "not integration"
```

## Code Coverage

### Run Tests with Coverage
```bash
pytest tests/ --cov=src/indusagi
```

### Generate HTML Coverage Report
```bash
pytest tests/ --cov=src/indusagi --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

### Generate Terminal Coverage Report
```bash
pytest tests/ --cov=src/indusagi --cov-report=term
```

## Test Markers

Available markers:
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.requires_api_key` - Tests requiring valid API key

## Fixtures Available

### Configuration Fixtures
- `sample_config` - Complete Config instance
- `agent_config` - AgentConfig instance
- `llm_config` - LLMConfig instance

### Mock OpenAI Fixtures
- `mock_openai_client` - Mocked OpenAI client
- `mock_openai_response` - Standard response
- `mock_openai_tool_response` - Response with tool calls
- `mock_openai_client_with_error` - Client that raises errors

### Tool Fixtures
- `calculator_tool` - Calculator tool for testing
- `weather_tool` - Weather tool for testing
- `failing_tool` - Tool that always fails
- `tool_list` - List of multiple tools

### Registry Fixtures
- `tool_registry` - Pre-populated tool registry
- `empty_tool_registry` - Empty registry

### Memory Fixtures
- `memory_system` - Empty memory system
- `memory_with_data` - Pre-populated memory

### Orchestrator Fixtures
- `orchestrator` - Complete orchestrator setup

### Utility Fixtures
- `temp_env_vars` - Set temporary environment variables
- `mock_api_key` - Mock OpenAI API key

## Common Test Commands

### Watch mode (requires pytest-watch)
```bash
ptw tests/
```

### Run failed tests only
```bash
pytest tests/ --lf
```

### Run tests in parallel (requires pytest-xdist)
```bash
pytest tests/ -n auto
```

### Stop at first failure
```bash
pytest tests/ -x
```

### Show test durations
```bash
pytest tests/ --durations=10
```

### Verbose output with test names
```bash
pytest tests/ -v --tb=short
```

## Test Statistics

- **Total Tests**: 255
- **Passing**: 255 (100%)
- **Code Coverage**: 92%
- **Execution Time**: < 1 second

## Key Features

- No external API dependencies (all mocked)
- Fast execution
- Comprehensive coverage
- Clear test organization
- Extensive edge case testing
- Integration test coverage

## Writing New Tests

### Test File Naming
- Name test files `test_*.py`
- Place in appropriate category directory

### Test Function Naming
- Name test functions `test_*`
- Use descriptive names: `test_agent_initialization_with_defaults`

### Test Class Naming
- Name test classes `Test*`
- Group related tests: `TestAgent`, `TestAgentEdgeCases`

### Using Fixtures
```python
def test_something(sample_config, agent_config):
    # Fixtures automatically provided
    agent = Agent(agent_config)
    assert agent.config == agent_config
```

### Async Tests
```python
@pytest.mark.asyncio
async def test_async_operation(agent_config):
    agent = Agent(agent_config)
    result = await agent.run("Test")
    assert result is not None
```

### Integration Tests
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_workflow(orchestrator):
    result = await orchestrator.execute("Test")
    assert result["success"] is True
```

## Debugging Tests

### Print debugging
```bash
pytest tests/ -s  # Don't capture output
```

### Drop into debugger on failure
```bash
pytest tests/ --pdb
```

### Show local variables on failure
```bash
pytest tests/ -l
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: pytest tests/ --cov=src/indusagi --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Performance Considerations

All tests are designed to:
- Complete in under 5 seconds total
- Run independently (no test order dependencies)
- Use mocked API calls (no network requests)
- Clean up resources properly

## Troubleshooting

### Import Errors
```bash
# Install the package in development mode
pip install -e .
```

### Fixture Not Found
Make sure you're importing from the right conftest.py:
```python
from tests.conftest import MockCalculatorTool
```

### Async Tests Not Running
Ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain coverage above 90%
4. Add integration tests for new workflows
5. Update this README if adding new test categories

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Test Suite Summary](../TEST_SUITE_SUMMARY.md)
