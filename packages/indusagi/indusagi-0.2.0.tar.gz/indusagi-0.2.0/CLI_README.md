# indus-agents CLI

A professional, beautiful command-line interface for interacting with AI agents powered by OpenAI. Built with Typer and Rich for an exceptional user experience.

## Features

- **Beautiful UI**: Rich formatting with markdown rendering, panels, tables, and spinners
- **Interactive Chat**: Maintain conversation history across multiple exchanges
- **Tool Integration**: Agents can use registered tools automatically
- **Error Handling**: Comprehensive error messages with helpful suggestions
- **API Validation**: Validates OpenAI API key before operations
- **Multiple Commands**: Single queries, interactive mode, tool management, and more
- **Customization**: Model selection, temperature control, verbose mode
- **Graceful Interrupts**: Handles Ctrl+C cleanly

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individual packages:

```bash
pip install openai pydantic python-dotenv typer rich
```

### 2. Set Up API Key

Create a `.env` file in the project directory:

```env
OPENAI_API_KEY=your-key-here
```

Or set as environment variable:

**Linux/Mac:**
```bash
export OPENAI_API_KEY='your-key-here'
```

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY='your-key-here'
```

**Windows CMD:**
```cmd
set OPENAI_API_KEY=your-key-here
```

### 3. Install CLI (Optional)

For system-wide access to `indusagi` command:

```bash
pip install -e .
```

## Usage

### Running the CLI

**If installed:**
```bash
indusagi [COMMAND] [OPTIONS]
```

**If not installed:**
```bash
python cli.py [COMMAND] [OPTIONS]
```

### Available Commands

#### 1. `run` - Single Query Execution

Execute a single query and get a response.

```bash
# Basic usage
indusagi run "What is Python?"

# With specific model
indusagi run "Explain quantum computing" --model gpt-4o

# With temperature control (higher = more creative)
indusagi run "Write a poem" --temperature 1.5

# Disable tools
indusagi run "Just chat" --no-tools

# Verbose mode
indusagi run "Calculate 25 * 48" --verbose
```

**Options:**
- `--model, -m`: OpenAI model (e.g., gpt-4o, gpt-4-turbo)
- `--temperature, -t`: Temperature 0.0-2.0 (default: 0.7)
- `--no-tools`: Disable tool usage
- `--verbose, -v`: Show detailed information

#### 2. `interactive` - Chat Mode

Start an interactive chat session with conversation history.

```bash
# Start interactive mode
indusagi interactive

# With custom settings
indusagi interactive --model gpt-4o --temperature 0.3

# Disable tools in chat
indusagi interactive --no-tools
```

**Special Commands in Chat:**
- `/quit` or `/exit` - Exit the chat
- `/clear` - Clear conversation history
- `/history` - Show message history
- `/tokens` - Show token usage estimate
- `/help` - Show help message

**Options:**
- `--model, -m`: OpenAI model
- `--temperature, -t`: Temperature 0.0-2.0
- `--no-tools`: Disable tool usage
- `--verbose, -v`: Verbose output

#### 3. `version` - Version Information

Display version information about the framework.

```bash
indusagi version
```

Shows:
- Framework version
- Python version
- OpenAI SDK version
- Rich and Typer versions
- API key configuration status

#### 4. `list-tools` - Available Tools

Display all registered tools that agents can use.

```bash
# Simple list
indusagi list-tools

# Detailed view with parameters
indusagi list-tools --detailed
```

**Options:**
- `--detailed, -d`: Show detailed tool information including parameters
- `--verbose, -v`: Verbose output

#### 5. `test-connection` - API Connectivity Test

Verify that your OpenAI API key works and you can connect.

```bash
# Test with default model
indusagi test-connection

# Test with specific model
indusagi test-connection --model gpt-4o

# Verbose mode
indusagi test-connection --verbose
```

**Options:**
- `--model, -m`: Model to test with
- `--verbose, -v`: Show detailed test information

#### 6. `list-agents` - Available Agent Types

Show predefined agent configurations and their capabilities.

```bash
indusagi list-agents
```

## Examples

### Example 1: Quick Math

```bash
indusagi run "What is 144 divided by 12?"
```

The agent will use the calculator tool automatically and provide the answer.

### Example 2: Interactive Conversation

```bash
indusagi interactive
```

```
You: My name is Alice and I love Python programming.
Agent: Nice to meet you, Alice! Python is a wonderful language...

You: What's my name?
Agent: Your name is Alice!

You: /tokens
Token Usage: Messages: 4, Estimated tokens: 156

You: /quit
```

### Example 3: Creative Writing

```bash
indusagi run "Write a haiku about coding" --temperature 1.2
```

Higher temperature produces more creative responses.

### Example 4: Current Time

```bash
indusagi run "What time is it?"
```

The agent will use the `get_time` tool to provide the current time.

### Example 5: Test Everything

```bash
# Test API connection
indusagi test-connection

# List available tools
indusagi list-tools --detailed

# Check version
indusagi version

# Try a query
indusagi run "Tell me a programming joke" --verbose
```

## Configuration

### Environment Variables

You can configure the agent using environment variables:

```env
# Required
OPENAI_API_KEY=sk-...

# Optional
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=1024
OPENAI_TEMPERATURE=0.7
VERBOSE=1
```

### Model Options

Supported OpenAI models:
- `gpt-4o` (default) - Most capable, balanced
- `gpt-4-turbo` - Fast and capable
- `gpt-4` - Original GPT-4
- `gpt-3.5-turbo` - Fast and economical

### Temperature Guide

- **0.0-0.3**: Focused, deterministic, factual
- **0.4-0.7**: Balanced (default: 0.7)
- **0.8-1.2**: Creative, varied
- **1.3-2.0**: Very creative, unpredictable

## Built-in Tools

The framework includes several built-in tools:

### Mathematical Tools
- `calculator`: Evaluate mathematical expressions
  - Example: "2 + 2", "10 * 5", "(3 + 7) / 2"

### Time/Date Tools
- `get_time`: Get current time
- `get_date`: Get current date
- `get_datetime`: Get current date and time

### Text Manipulation Tools
- `text_uppercase`: Convert text to uppercase
- `text_lowercase`: Convert text to lowercase
- `text_reverse`: Reverse text
- `text_title_case`: Convert to title case
- `text_count_words`: Count words, characters, and lines

## Adding Custom Tools

You can add your own tools to the registry:

```python
from tools import registry

@registry.register
def my_tool(param: str) -> str:
    """
    Description of your tool.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    return f"Processed: {param}"
```

The tool will be automatically available to agents!

## Error Handling

The CLI provides helpful error messages:

### API Key Not Set
```
OpenAI API key not found!

Please set your API key using one of these methods:
1. Environment variable: export OPENAI_API_KEY='your-key-here'
2. Windows PowerShell: $env:OPENAI_API_KEY='your-key-here'
3. .env file: OPENAI_API_KEY=your-key-here
```

### Connection Issues
```
Connection test failed: Invalid authentication

Common issues:
  • Invalid API key
  • Network connectivity problems
  • Insufficient API credits
  • Model not available for your account
```

### Invalid Model
```
Configuration error: Model 'gpt-5' not found
```

## Troubleshooting

### Import Errors

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Verify installation
python -c "import typer, rich; print('All packages installed')"
```

### API Key Issues

```bash
# Test if API key is set
python -c "import os; print('Set' if os.getenv('OPENAI_API_KEY') else 'Not set')"

# Test connection
indusagi test-connection --verbose
```

### Module Not Found

```bash
# Ensure you're in the project directory
cd /path/to/agent-framework-build-plan

# Run directly with Python
python cli.py version
```

## Advanced Usage

### Piping Input

```bash
echo "Explain quantum computing" | indusagi run -
```

### Batch Processing

```bash
# Create a file with queries
cat queries.txt
What is 2+2?
What time is it?
Tell me a joke

# Process each line
while read query; do
    indusagi run "$query"
done < queries.txt
```

### Environment-Specific Configs

```bash
# Development
export OPENAI_MODEL=gpt-3.5-turbo
export OPENAI_TEMPERATURE=0.5

# Production
export OPENAI_MODEL=gpt-4o
export OPENAI_TEMPERATURE=0.7
```

## Best Practices

1. **Use verbose mode** when debugging: `--verbose`
2. **Test connection** before important queries: `test-connection`
3. **Clear history** in interactive mode for new topics: `/clear`
4. **Monitor tokens** to manage costs: `/tokens`
5. **Use appropriate temperature** for your task
6. **Disable tools** if not needed for faster responses: `--no-tools`

## Performance Tips

1. Use `gpt-3.5-turbo` for simple tasks (faster and cheaper)
2. Use `gpt-4o` for complex reasoning
3. Lower temperature (0.3) for factual queries
4. Higher temperature (1.2) for creative tasks
5. Clear history regularly to reduce token usage

## Security Notes

- Never commit `.env` file with API keys
- Use environment variables in production
- Validate tool inputs (built into framework)
- Monitor API usage on OpenAI dashboard
- Use rate limiting for production tools

## Support

For issues and questions:
- Check the main README.md
- Review error messages carefully
- Use `--verbose` flag for details
- Test with `test-connection` command

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Test your changes
2. Update documentation
3. Follow existing code style
4. Add examples for new features

---

**Happy chatting with your AI agents!** 🤖
