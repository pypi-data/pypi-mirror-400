# Deployment Guide

This guide covers building, testing, and deploying indus-agents to various environments.

## Table of Contents

- [Local Development](#local-development)
- [Building the Package](#building-the-package)
- [Testing the Package](#testing-the-package)
- [Publishing to PyPI](#publishing-to-pypi)
- [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [Production Considerations](#production-considerations)

## Local Development

### Prerequisites

- Python 3.9 or higher
- uv or pip package manager
- Git
- Virtual environment tool

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/varunisrani/indus-agents.git
cd indus-agents

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Local Testing Workflow

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=indusagi --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
start htmlcov/index.html  # On Windows

# Format code
black src tests

# Lint code
ruff check src tests

# Fix linting issues
ruff check --fix src tests

# Type checking
mypy src

# Run all checks before commit
pre-commit run --all-files
```

## Building the Package

### Install Build Tools

```bash
# Install build and twine
pip install build twine
```

### Build Distribution Packages

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build

# This creates:
# - dist/indusagi-0.1.0.tar.gz (source distribution)
# - dist/indusagi-0.1.0-py3-none-any.whl (wheel)
```

### Verify Build

```bash
# Check the distribution files
ls -lh dist/

# Verify the package metadata
python -m twine check dist/*

# Expected output:
# Checking dist/indusagi-0.1.0-py3-none-any.whl: PASSED
# Checking dist/indusagi-0.1.0.tar.gz: PASSED
```

## Testing the Package

### Test Local Installation

```bash
# Create a new test environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from wheel
pip install dist/indusagi-0.1.0-py3-none-any.whl

# Test the installation
python -c "from indusagi import Agent, __version__; print(__version__)"

# Test the CLI
indusagi version

# Deactivate and cleanup
deactivate
rm -rf test-env
```

### Test PyPI Upload (Test PyPI)

Before publishing to the real PyPI, test with TestPyPI:

```bash
# Register on TestPyPI: https://test.pypi.org/account/register/

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ indusagi

# Test the installation
python -c "from indusagi import Agent, __version__; print(__version__)"
```

## Publishing to PyPI

### Prerequisites

1. **PyPI Account**: Register at https://pypi.org/account/register/
2. **API Token**: Generate at https://pypi.org/manage/account/token/
3. **Configure credentials**:

```bash
# Create or edit ~/.pypirc
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
EOF

# Set proper permissions
chmod 600 ~/.pypirc
```

### Release Checklist

Before publishing, ensure:

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black src tests`
- [ ] Linting passes: `ruff check src tests`
- [ ] Type checking passes: `mypy src`
- [ ] Version is updated in:
  - [ ] `pyproject.toml`
  - [ ] `src/indusagi/__init__.py`
- [ ] CHANGELOG.md is updated with release notes
- [ ] Documentation is up to date
- [ ] Git tag is created: `git tag -a v0.1.0 -m "Release v0.1.0"`
- [ ] Changes are committed and pushed
- [ ] Build artifacts are clean: `rm -rf dist/ build/`

### Publish to PyPI

```bash
# Build the package
python -m build

# Verify the build
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*

# Verify the upload
pip install indusagi
python -c "from indusagi import __version__; print(__version__)"
```

### Post-Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# Create GitHub release
# Go to: https://github.com/varunisrani/indus-agents/releases/new
# - Tag: v0.1.0
# - Title: v0.1.0 - Release Title
# - Description: Copy from CHANGELOG.md
# - Attach build artifacts if needed
```

## Docker Deployment

### Create Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir .

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Run the CLI
ENTRYPOINT ["my-agent"]
CMD ["--help"]
```

### Create Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  agent:
    build: .
    image: indusagi:latest
    container_name: my-agent
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - LOG_FILE=/app/logs/agent.log
    restart: unless-stopped
```

### Build and Run

```bash
# Build the Docker image
docker build -t indusagi:latest .

# Run with docker
docker run --rm \
  -e OPENAI_API_KEY=your-key \
  indusagi:latest version

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Multi-Stage Build (Optimized)

For production, use a multi-stage build:

```dockerfile
# Multi-stage Dockerfile
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN pip install --no-cache-dir build

# Copy source
COPY . .

# Build wheel
RUN python -m build --wheel

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy wheel from builder
COPY --from=builder /build/dist/*.whl .

# Install the wheel
RUN pip install --no-cache-dir *.whl && rm *.whl

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["my-agent"]
CMD ["--help"]
```

## Environment Variables

### Required Variables

```bash
# Minimum required for OpenAI
OPENAI_API_KEY=your_key_here
```

### Recommended for Production

```bash
# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Configuration
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.7
LOG_LEVEL=WARNING
ENVIRONMENT=production

# Security
ENABLE_INPUT_SANITIZATION=true
MAX_INPUT_LENGTH=10000

# Performance
ENABLE_ASYNC=true
REQUEST_TIMEOUT=60
MAX_RETRIES=3

# Rate Limiting
ENABLE_RATE_LIMIT=true
MAX_REQUESTS_PER_MINUTE=60
```

### Loading Environment Variables

#### From .env file

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

#### From Docker

```bash
# Pass individual variables
docker run -e OPENAI_API_KEY=your_key indusagi:latest

# Pass from file
docker run --env-file .env indusagi:latest
```

#### From Kubernetes

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: your_key_here
---
apiVersion: v1
kind: Pod
metadata:
  name: my-agent
spec:
  containers:
  - name: agent
    image: indusagi:latest
    envFrom:
    - secretRef:
        name: agent-secrets
```

## Production Considerations

### Security

1. **Never commit secrets**:
   - Add `.env` to `.gitignore`
   - Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.)

2. **Validate inputs**:
   ```python
   ENABLE_INPUT_SANITIZATION=true
   MAX_INPUT_LENGTH=10000
   ```

3. **Use HTTPS**:
   - Always use HTTPS endpoints
   - Verify SSL certificates

4. **Rate limiting**:
   ```python
   ENABLE_RATE_LIMIT=true
   MAX_REQUESTS_PER_MINUTE=60
   ```

### Performance

1. **Enable async execution**:
   ```python
   ENABLE_ASYNC=true
   WORKER_POOL_SIZE=4
   ```

2. **Configure timeouts**:
   ```python
   REQUEST_TIMEOUT=60
   TOOL_TIMEOUT=30
   ```

3. **Use caching**:
   ```python
   ENABLE_TOOL_CACHE=true
   CACHE_BACKEND=redis
   REDIS_URL=redis://localhost:6379/0
   ```

### Monitoring

1. **Enable logging**:
   ```python
   LOG_LEVEL=INFO
   LOG_FILE=/var/log/agent.log
   ```

2. **Structured logging**:
   ```python
   LOG_FORMAT=json
   ```

3. **Metrics collection**:
   ```python
   ENABLE_METRICS=true
   METRICS_PORT=9090
   ```

### Scalability

1. **Horizontal scaling**:
   - Run multiple instances behind a load balancer
   - Use stateless design

2. **Database connection pooling**:
   ```python
   DB_POOL_SIZE=10
   DB_MAX_OVERFLOW=20
   ```

3. **Async operations**:
   - Use async/await throughout
   - Implement connection pooling

### Error Handling

1. **Retry logic**:
   ```python
   MAX_RETRIES=3
   RETRY_DELAY=1
   EXPONENTIAL_BACKOFF=true
   ```

2. **Graceful degradation**:
   - Handle API failures gracefully
   - Provide fallback mechanisms

3. **Error logging**:
   - Log all errors with context
   - Include request IDs for tracing

### Health Checks

Add health check endpoints:

```python
# Example health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": __version__}
```

### Backup and Recovery

1. **Data backup**:
   - Regular backups of persistent data
   - Test recovery procedures

2. **Configuration backup**:
   - Version control all configuration
   - Document deployment procedures

## Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

### Automated Testing

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: pytest --cov=indusagi

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Build Issues

```bash
# Clear build cache
rm -rf build/ dist/ *.egg-info

# Reinstall build tools
pip install --upgrade build twine
```

### Import Errors

```bash
# Verify package structure
python -m pip show indusagi

# Check installation
pip list | grep indusagi
```

### Docker Issues

```bash
# Rebuild without cache
docker build --no-cache -t indusagi:latest .

# Check logs
docker logs my-agent

# Interactive debugging
docker run -it --entrypoint /bin/bash indusagi:latest
```

## Support

For deployment issues:

- Check [GitHub Issues](https://github.com/varunisrani/indus-agents/issues)
- Review [Documentation](https://github.com/varunisrani/indus-agents#readme)
- Contact: your.email@example.com

---

**Last Updated**: 2025-01-XX
