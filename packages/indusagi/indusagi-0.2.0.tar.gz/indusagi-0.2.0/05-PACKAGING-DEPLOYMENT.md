# Packaging & Deployment Guide

## 📦 Complete Packaging & Testing Workflow

This guide covers everything from local testing to production deployment.

---

## PART 1: Local Development & Testing (15 minutes)

### Step 1: Editable Installation

```bash
# Navigate to project root
cd indusagi

# Install in editable mode (DO THIS ONCE)
uv pip install -e .

# Verify installation
pip list | grep indusagi
indusagi --help
```

**Why Editable Mode?**
- Changes to source code are immediately reflected
- No need to reinstall after every change
- Test CLI commands instantly
- Perfect for rapid development

---

### Step 2: Local Testing Workflow

```bash
# Terminal 1: Edit code
vim src/indusagi/agent.py

# Terminal 2: Test immediately (no reinstall!)
indusagi run "test query"

# Or test in Python
python -c "
from indusagi import Agent
agent = Agent('Test', 'Tester')
print(agent.process('Hello'))
"
```

**Fast Iteration Loop:**
1. Edit code
2. Save file
3. Run command
4. See results instantly

---

### Step 3: Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/indusagi --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v

# Run specific test
pytest tests/test_agent.py::test_agent_creation -v

# Watch mode (rerun on file changes)
pip install pytest-watch
ptw tests/
```

---

### Step 4: Code Quality Checks

```bash
# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type checking with mypy (optional)
pip install mypy
mypy src/
```

---

## PART 2: Building the Package (10 minutes)

### Step 1: Verify pyproject.toml

Ensure your `pyproject.toml` is complete:

```toml
[project]
name = "indusagi"
version = "0.1.0"
description = "AI indus-agents with multi-agent orchestration"
readme = "README.md"
requires-python = ">=3.9"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
license = {text = "MIT"}
keywords = ["ai", "agents", "llm", "anthropic"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "anthropic>=0.35.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[project.urls]
Homepage = "https://github.com/varunisrani/indus-agents"
Documentation = "https://github.com/varunisrani/indus-agents#readme"
Repository = "https://github.com/varunisrani/indus-agents"
Issues = "https://github.com/varunisrani/indus-agents/issues"

[project.scripts]
indusagi = "indusagi.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-ra -q"

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'

[tool.ruff]
line-length = 100
target-version = "py39"
```

---

### Step 2: Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build with UV (fastest)
uv build

# Or build with pip tools
pip install build
python -m build

# Check dist/ folder
ls -lh dist/
# Should see:
# - indusagi-0.1.0.tar.gz (source distribution)
# - indusagi-0.1.0-py3-none-any.whl (wheel)
```

---

### Step 3: Test Built Package

```bash
# Create a fresh virtual environment
python -m venv test-venv
source test-venv/bin/activate  # On Windows: test-venv\Scripts\activate

# Install from wheel
pip install dist/indusagi-0.1.0-py3-none-any.whl

# Test installation
indusagi --version
indusagi list-tools

# Set API key and test
export ANTHROPIC_API_KEY="your-key"
indusagi run "What is 2+2?"

# Cleanup
deactivate
rm -rf test-venv
```

---

## PART 3: Publishing Options (5 minutes)

### Option A: Private PyPI Server

For internal company use:

```bash
# Install twine
pip install twine

# Upload to private PyPI
twine upload --repository-url https://your-pypi-server.com dist/*
```

---

### Option B: Public PyPI

For open-source packages:

```bash
# Create account at https://pypi.org/account/register/

# Install twine
pip install twine

# Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ indusagi

# If successful, upload to production PyPI
twine upload dist/*
```

---

### Option C: GitHub Releases

For GitHub-hosted projects:

```bash
# Create release on GitHub
gh release create v0.1.0 dist/* --title "v0.1.0" --notes "Initial release"

# Users can install directly from GitHub
pip install git+https://github.com/varunisrani/indus-agents.git
```

---

## PART 4: Deployment Strategies

### Strategy 1: Direct Installation (Simplest)

**For**: Internal tools, development

```bash
# Install from source
git clone https://github.com/varunisrani/indus-agents.git
cd indusagi
pip install -e .

# Or install from PyPI
pip install indusagi
```

---

### Strategy 2: Docker Containerization

**For**: Consistent environments, cloud deployment

**Create `Dockerfile`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install uv && uv pip install .

# Copy source code
COPY src/ ./src/

# Install package
RUN pip install -e .

# Set entrypoint
ENTRYPOINT ["my-agent"]
CMD ["--help"]
```

**Build and run:**

```bash
# Build image
docker build -t indusagi:latest .

# Run container
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    indusagi:latest run "What is 2+2?"

# Interactive mode
docker run -it -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    indusagi:latest interactive
```

---

### Strategy 3: Serverless Functions

**For**: On-demand execution, auto-scaling

**AWS Lambda Example:**

```python
# lambda_handler.py
from indusagi import Orchestrator

orchestrator = Orchestrator()

def lambda_handler(event, context):
    """AWS Lambda handler."""
    user_input = event.get('query', '')

    response = orchestrator.route(user_input)

    return {
        'statusCode': 200,
        'body': response
    }
```

**Deploy:**

```bash
# Package dependencies
pip install -t package/ indusagi

# Create deployment package
cd package && zip -r ../lambda.zip . && cd ..
zip -g lambda.zip lambda_handler.py

# Upload to AWS Lambda
aws lambda create-function \
    --function-name indusagi \
    --runtime python3.11 \
    --handler lambda_handler.lambda_handler \
    --zip-file fileb://lambda.zip \
    --role arn:aws:iam::ACCOUNT:role/lambda-role
```

---

### Strategy 4: Web API with FastAPI

**For**: REST API access, multiple clients

**Create `api.py`:**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from indusagi import Orchestrator
import os

app = FastAPI(title="indus-agents API")
orchestrator = Orchestrator()

class Query(BaseModel):
    text: str
    verbose: bool = False

class Response(BaseModel):
    response: str
    agent_used: str

@app.post("/query", response_model=Response)
async def process_query(query: Query):
    """Process a user query."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=500, detail="API key not configured")

    try:
        response = orchestrator.route(query.text, verbose=query.verbose)
        return Response(response=response, agent_used="orchestrated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

**Run:**

```bash
# Install FastAPI
pip install fastapi uvicorn

# Run server
uvicorn api:app --host 0.0.0.0 --port 8000

# Test
curl -X POST "http://localhost:8000/query" \
    -H "Content-Type: application/json" \
    -d '{"text": "What is 2+2?"}'
```

---

## PART 5: Environment Configuration

### Development Environment

**`.env.development`:**

```bash
ANTHROPIC_API_KEY=sk-ant-dev-key
AGENT_MODEL=claude-sonnet-4-5-20250929
LOG_LEVEL=DEBUG
MAX_TOKENS=1024
```

**Load in code:**

```python
from dotenv import load_dotenv
import os

# Load appropriate env file
env = os.getenv("ENV", "development")
load_dotenv(f".env.{env}")
```

---

### Production Environment

**Best Practices:**

1. **Use Secret Management**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault

2. **Environment Variables**
   ```bash
   # Set in production environment
   export ANTHROPIC_API_KEY="production-key"
   export ENV="production"
   export LOG_LEVEL="INFO"
   ```

3. **Config File** (for non-secrets)
   ```yaml
   # config.yaml
   agent:
     model: "claude-sonnet-4-5-20250929"
     max_tokens: 1024
     temperature: 0.7

   orchestrator:
     default_agent: "general"
     routing_strategy: "keyword"
   ```

---

## PART 6: CI/CD Pipeline

### GitHub Actions Example

**`.github/workflows/ci.yml`:**

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install uv
        uv pip install -e ".[dev]"

    - name: Run tests
      run: |
        pytest tests/ -v --cov=src/indusagi --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        pip install black ruff

    - name: Check formatting
      run: black --check src/ tests/

    - name: Lint
      run: ruff check src/ tests/

  build:
    runs-on: ubuntu-latest
    needs: [test, lint]
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Build package
      run: |
        pip install build
        python -m build

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/
```

---

## PART 7: Monitoring & Logging

### Production Logging

```python
# src/indusagi/logging_config.py
import logging
import sys
from rich.logging import RichHandler

def setup_logging(level: str = "INFO"):
    """Configure logging for production."""

    # Create logger
    logger = logging.getLogger("indusagi")
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler (for development)
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setLevel(logging.DEBUG)

    # File handler (for production)
    file_handler = logging.FileHandler("agent.log")
    file_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Usage in agent.py
from .logging_config import setup_logging

logger = setup_logging()

class Agent:
    def process(self, user_input: str) -> str:
        logger.info(f"Processing input: {user_input[:50]}...")
        try:
            response = self.client.messages.create(...)
            logger.info("Response generated successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            raise
```

---

### Metrics & Monitoring

```python
# src/indusagi/metrics.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
import json

@dataclass
class AgentMetrics:
    """Track agent performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0

    def record_request(self, success: bool, tokens: int, cost: float, duration: float):
        """Record a request."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        self.total_tokens += tokens
        self.total_cost += cost

        # Update average
        self.avg_response_time = (
            (self.avg_response_time * (self.total_requests - 1) + duration)
            / self.total_requests
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_response_time": self.avg_response_time,
        }

    def save(self, filepath: str):
        """Save metrics to file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

# Usage in agent
metrics = AgentMetrics()

def process(self, user_input: str) -> str:
    start_time = time.time()
    try:
        response = self.client.messages.create(...)
        duration = time.time() - start_time

        # Record success
        metrics.record_request(
            success=True,
            tokens=response.usage.total_tokens,
            cost=calculate_cost(response.usage),
            duration=duration
        )

        return response.content[0].text
    except Exception as e:
        duration = time.time() - start_time
        metrics.record_request(
            success=False,
            tokens=0,
            cost=0,
            duration=duration
        )
        raise
```

---

## PART 8: Version Management

### Semantic Versioning

```bash
# Current version in pyproject.toml
version = "0.1.0"

# Patch release (bug fixes): 0.1.0 → 0.1.1
# Minor release (new features): 0.1.0 → 0.2.0
# Major release (breaking changes): 0.1.0 → 1.0.0
```

### Version Bumping

```bash
# Install bump2version
pip install bump2version

# Create .bumpversion.cfg
cat > .bumpversion.cfg << EOF
[bumpversion]
current_version = 0.1.0
commit = True
tag = True

[bumpversion:file:pyproject.toml]
[bumpversion:file:src/indusagi/__init__.py]
EOF

# Bump version
bump2version patch  # 0.1.0 → 0.1.1
bump2version minor  # 0.1.0 → 0.2.0
bump2version major  # 0.1.0 → 1.0.0

# Push tags
git push --tags
```

---

## 🎯 Deployment Checklist

### Pre-Deployment:
- [ ] All tests pass
- [ ] Code formatted and linted
- [ ] Documentation updated
- [ ] Version bumped
- [ ] CHANGELOG.md updated
- [ ] Security vulnerabilities checked
- [ ] Dependencies updated

### Deployment:
- [ ] Build package
- [ ] Test built package in clean environment
- [ ] Upload to PyPI/server
- [ ] Create GitHub release
- [ ] Update documentation
- [ ] Announce release

### Post-Deployment:
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Gather user feedback
- [ ] Plan next iteration

---

**Next**: See **06-QUICK-REFERENCE.md** for code snippets and troubleshooting
