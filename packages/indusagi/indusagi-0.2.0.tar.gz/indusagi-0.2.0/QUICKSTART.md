# Quick Start Guide - indus-agents CLI

Get up and running with the indus-agents CLI in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

This installs:
- `openai` - OpenAI API client
- `pydantic` - Configuration management
- `python-dotenv` - Environment variables
- `typer` - CLI framework
- `rich` - Beautiful terminal output

## Step 2: Set Your API Key (1 minute)

Choose one method:

### Method A: .env file (Recommended)

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### Method B: Environment variable

**Linux/Mac:**
```bash
export OPENAI_API_KEY='sk-your-actual-key-here'
```

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY='sk-your-actual-key-here'
```

**Windows CMD:**
```cmd
set OPENAI_API_KEY=sk-your-actual-key-here
```

Get your API key from: https://platform.openai.com/api-keys

## Step 3: Test Connection (30 seconds)

```bash
python cli.py test-connection
```

You should see:
```
Connection Test Results
┌─────────────────────────┬─────────────────┬────────────────────────────┐
│ Check                   │ Status          │ Details                    │
├─────────────────────────┼─────────────────┼────────────────────────────┤
│ API Key                 │ Valid           │ Authentication successful  │
│ Model                   │ Available       │ gpt-4o                     │
│ Response                │ Received        │ Connection successful      │
└─────────────────────────┴─────────────────┴────────────────────────────┘
```

## Step 4: Try Your First Query (1 minute)

```bash
python cli.py run "What is 25 * 48?"
```

The agent will use the calculator tool and respond:
```
Agent Response
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The result of 25 * 48 is 1200.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 5: Start Interactive Chat (2 minutes)

```bash
python cli.py interactive
```

Try these commands in chat:
```
You: Hello! My name is Alice.
Agent: Hello Alice! Nice to meet you...

You: What time is it?
Agent: [Uses get_time tool] The current time is 14:30:45 PM.

You: What's my name?
Agent: Your name is Alice!

You: /help
[Shows help message]

You: /quit
```

## You're Ready!

### Next Steps

1. **Explore all commands:**
   ```bash
   python cli.py --help
   ```

2. **List available tools:**
   ```bash
   python cli.py list-tools --detailed
   ```

3. **Try different models:**
   ```bash
   python cli.py run "Tell me a joke" --model gpt-3.5-turbo
   ```

4. **Adjust creativity:**
   ```bash
   python cli.py run "Write a haiku" --temperature 1.5
   ```

5. **Install globally (optional):**
   ```bash
   pip install -e .
   indusagi --help
   ```

## Common Commands Cheat Sheet

```bash
# Single query
python cli.py run "your question here"

# Interactive chat
python cli.py interactive

# Test connection
python cli.py test-connection

# List tools
python cli.py list-tools

# Show version
python cli.py version

# With options
python cli.py run "question" --model gpt-4o --temperature 0.7 --verbose
```

## Troubleshooting

### "OPENAI_API_KEY not set"
- Make sure your .env file is in the project directory
- Or set the environment variable
- Verify: `echo $OPENAI_API_KEY` (Linux/Mac) or `echo %OPENAI_API_KEY%` (Windows)

### "Module not found"
- Run: `pip install -r requirements.txt`
- Make sure you're in the project directory

### "API Error"
- Verify your API key is correct
- Check you have API credits: https://platform.openai.com/usage
- Try: `python cli.py test-connection --verbose`

## Tips

1. Use **verbose mode** to see what's happening: `--verbose`
2. **Clear history** in chat to start fresh: `/clear`
3. **Lower temperature** (0.3) for factual answers
4. **Higher temperature** (1.2) for creative responses
5. Use `gpt-3.5-turbo` for faster, cheaper responses
6. Check `/tokens` in chat to monitor usage

## Getting Help

```bash
# General help
python cli.py --help

# Command-specific help
python cli.py run --help
python cli.py interactive --help
```

## What's Next?

- Read the full CLI_README.md for detailed documentation
- Explore the built-in tools
- Add your own custom tools to tools.py
- Try different agent configurations
- Build your own automation scripts

**Happy chatting with your AI agents!** 🚀
