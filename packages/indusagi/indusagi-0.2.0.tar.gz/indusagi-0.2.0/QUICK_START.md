# Quick Start Guide

Get up and running with indus-agents in 5 minutes.

## Installation

### For Users

```bash
# Using pip
pip install indusagi

# Using uv (faster)
uv pip install indusagi
```

### For Developers

```bash
# Clone the repository
git clone https://github.com/varunisrani/indus-agents.git
cd indus-agents

# Install with development dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# Required: OPENAI_API_KEY=your_key_here
```

## Basic Usage

### Using the CLI

```bash
# Check version
indusagi version

# Run agent with a prompt
indusagi run "What is the capital of France?"

# Run with verbose output
indusagi run "Explain Python" --verbose
```

### Using Python API

```python
import asyncio
from indusagi import Agent, AgentConfig

async def main():
    # Create agent
    config = AgentConfig(name="Assistant", model="gpt-4")
    agent = Agent(config=config)

    # Run agent
    response = await agent.run("Hello, world!")
    print(response)

asyncio.run(main())
```

### With Tools

```python
from indusagi import Agent, BaseTool, ToolConfig, ToolResult

class CalculatorTool(BaseTool):
    def __init__(self):
        config = ToolConfig(
            name="calculator",
            description="Performs arithmetic",
            parameters={
                "operation": {"type": "string"},
                "a": {"type": "number"},
                "b": {"type": "number"}
            }
        )
        super().__init__(config)

    async def execute(self, operation: str, a: float, b: float) -> ToolResult:
        operations = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else None
        }
        result = operations.get(operation)

        if result is None:
            return ToolResult(success=False, result=None, error="Invalid operation")

        return ToolResult(success=True, result=result)

# Use tool
agent = Agent()
agent.add_tool(CalculatorTool())
```

## Development

### Common Commands

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=indusagi

# Format code
black src tests

# Lint code
ruff check src tests

# Fix linting issues
ruff check --fix src tests

# Type check
mypy src

# Install pre-commit hooks
pre-commit install

# Run pre-commit checks
pre-commit run --all-files
```

### Project Structure

```
src/indusagi/
├── agent/          # Agent implementations
├── core/           # Core functionality
├── tools/          # Tool system
└── utils/          # Utilities
```

## Publishing

### Build Package

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check build
python -m twine check dist/*
```

### Test on TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ indusagi
```

### Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Create release tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

## Docker

### Build Image

```bash
# Build Docker image
docker build -t indusagi:latest .

# Run container
docker run --rm \
  -e OPENAI_API_KEY=your_key \
  indusagi:latest version
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Common Tasks

### Create New Tool

```python
from indusagi.tools.base import BaseTool, ToolConfig, ToolResult

class MyTool(BaseTool):
    def __init__(self):
        config = ToolConfig(
            name="my_tool",
            description="What the tool does",
            parameters={"param": {"type": "string"}}
        )
        super().__init__(config)

    async def execute(self, param: str) -> ToolResult:
        # Tool logic here
        return ToolResult(success=True, result="Done")
```

### Create Custom Agent

```python
from indusagi.agent.base import BaseAgent, AgentConfig

class MyAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)

    async def run(self, prompt: str, **kwargs) -> str:
        # Custom agent logic
        return "Response"

    async def step(self, **kwargs):
        # Custom step logic
        return {"status": "success"}
```

## Troubleshooting

### Import Errors

```bash
# Verify installation
pip show indusagi

# Reinstall
pip install --force-reinstall indusagi
```

### API Key Issues

```bash
# Check environment variable
echo $OPENAI_API_KEY  # Unix
echo %OPENAI_API_KEY%  # Windows

# Load from .env
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Test Failures

```bash
# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_agent/test_base.py -v

# Clear cache and retry
pytest --cache-clear
```

## Resources

- **Full Documentation**: [README.md](README.md)
- **API Reference**: See inline documentation
- **Examples**: [examples/](examples/) directory
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## Getting Help

- Check [GitHub Issues](https://github.com/varunisrani/indus-agents/issues)
- Read [documentation](README.md)
- Join [discussions](https://github.com/varunisrani/indus-agents/discussions)

## Next Steps

1. Read the [full documentation](README.md)
2. Check out [examples](examples/)
3. Join the community
4. Start building!

---

**Quick Links**:
- [Installation](#installation)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Development](#development)
- [Publishing](#publishing)
- [Troubleshooting](#troubleshooting)
