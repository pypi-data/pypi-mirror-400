# Contributing to indus-agents

Thank you for your interest in contributing to indus-agents! We welcome contributions from the community and are grateful for any help you can provide.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Guidelines](#code-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect all contributors to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- uv (recommended) or pip
- A GitHub account

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork locally**:
   ```bash
   git clone https://github.com/varunisrani/indus-agents.git
   cd indus-agents
   ```

3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/originalowner/indusagi.git
   ```

4. **Create a virtual environment and install dependencies**:
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"

   # Or using pip
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

5. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

6. **Set up your environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Development Workflow

### Creating a Branch

Always create a new branch for your work:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications
- `chore/` - Maintenance tasks

### Making Changes

1. **Make your changes** in your feature branch

2. **Run tests frequently**:
   ```bash
   pytest
   ```

3. **Format your code**:
   ```bash
   black src tests
   ruff check --fix src tests
   ```

4. **Type check your code**:
   ```bash
   mypy src
   ```

5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "Add feature: description of feature"
   ```

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(agent): add support for streaming responses

fix(tools): correct parameter validation in BaseTool

docs(readme): update installation instructions

test(agent): add tests for tool execution
```

## Code Guidelines

### Python Style Guide

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications:

- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Formatting**: Use Black for automatic formatting
- **Linting**: Use Ruff for linting
- **Type hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings

### Code Quality Standards

1. **Type Hints**: All functions should have type hints
   ```python
   def process_data(data: str, count: int = 10) -> Dict[str, Any]:
       """Process the data."""
       pass
   ```

2. **Docstrings**: All public functions, classes, and modules should have docstrings
   ```python
   def calculate(x: int, y: int) -> int:
       """Calculate the sum of two numbers.

       Args:
           x: First number
           y: Second number

       Returns:
           Sum of x and y

       Raises:
           ValueError: If inputs are invalid
       """
       return x + y
   ```

3. **Error Handling**: Use appropriate exception handling
   ```python
   try:
       result = risky_operation()
   except SpecificError as e:
       logger.error(f"Operation failed: {e}")
       raise
   ```

4. **Logging**: Use the logger utility, not print statements
   ```python
   from indusagi.utils.logger import get_logger

   logger = get_logger(__name__)
   logger.info("Operation completed successfully")
   ```

### Project Structure

When adding new features, follow the existing structure:

```
src/indusagi/
├── agent/          # Agent implementations
├── core/           # Core functionality
├── tools/          # Tool implementations
└── utils/          # Utility functions
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory, mirroring the `src/` structure
- Name test files with `test_` prefix
- Use descriptive test function names

**Example test structure**:
```python
# tests/test_agent/test_base.py
import pytest
from indusagi.agent.base import BaseAgent, AgentConfig


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AgentConfig()
        assert config.name == "Agent"
        assert config.temperature == 0.7

    def test_custom_config(self):
        """Test custom configuration values."""
        config = AgentConfig(name="TestAgent", temperature=0.5)
        assert config.name == "TestAgent"
        assert config.temperature == 0.5


@pytest.mark.asyncio
class TestBaseAgent:
    """Tests for BaseAgent."""

    async def test_agent_initialization(self):
        """Test agent initialization."""
        # Implementation
        pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=indusagi --cov-report=html

# Run specific test file
pytest tests/test_agent/test_base.py

# Run specific test
pytest tests/test_agent/test_base.py::TestAgentConfig::test_default_config

# Run with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_agent"
```

### Test Coverage

- Aim for at least 80% code coverage
- All new features should include tests
- Bug fixes should include regression tests

## Documentation

### Code Documentation

- Add docstrings to all public modules, classes, and functions
- Use Google-style docstrings
- Include examples in docstrings when helpful

### README Updates

If your changes affect usage, update the README.md:

- Installation instructions
- Usage examples
- Configuration options
- CLI commands

### CHANGELOG Updates

Add an entry to CHANGELOG.md under the "Unreleased" section:

```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Changed feature description

### Fixed
- Bug fix description
```

## Pull Request Process

### Before Submitting

1. **Update your branch with the latest upstream changes**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Ensure all tests pass**:
   ```bash
   pytest
   ```

3. **Check code formatting**:
   ```bash
   black src tests
   ruff check src tests
   mypy src
   ```

4. **Update documentation** if needed

5. **Update CHANGELOG.md**

### Submitting the Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin your-feature-branch
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Description of changes
   - Related issue numbers (if any)
   - Type of change (feature, bugfix, etc.)
   - Checklist completion

4. **Respond to review comments** promptly

### PR Title Format

Use the same format as commit messages:

```
feat: add streaming response support
fix: correct tool parameter validation
docs: update installation guide
```

### Review Process

- At least one maintainer must approve the PR
- All CI checks must pass
- Code coverage should not decrease
- Documentation must be updated if needed

## Release Process

(For maintainers only)

1. **Update version numbers**:
   - `pyproject.toml`
   - `src/indusagi/__init__.py`

2. **Update CHANGELOG.md**:
   - Move items from "Unreleased" to new version section
   - Add release date

3. **Create release commit**:
   ```bash
   git commit -am "Release v0.2.0"
   ```

4. **Create and push tag**:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin main
   git push origin v0.2.0
   ```

5. **Build and publish** (see DEPLOYMENT.md)

## Getting Help

- Check existing [issues](https://github.com/varunisrani/indus-agents/issues)
- Join our [discussions](https://github.com/varunisrani/indus-agents/discussions)
- Read the documentation
- Ask questions in pull requests

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- The CONTRIBUTORS file

Thank you for contributing to indus-agents!

---

**Questions?** Feel free to ask in [GitHub Discussions](https://github.com/varunisrani/indus-agents/discussions).
