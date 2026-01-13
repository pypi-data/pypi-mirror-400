#!/bin/bash
# indus-agents CLI - Usage Examples
# This script demonstrates all CLI commands with various options

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║       indus-agents CLI - Interactive Examples             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Function to pause between examples
pause() {
    echo ""
    read -p "Press Enter to continue to next example..."
    echo ""
    echo "─────────────────────────────────────────────────────────────"
    echo ""
}

# Example 1: Check version
echo "Example 1: Check CLI Version"
echo "Command: python cli.py version"
echo ""
python cli.py version
pause

# Example 2: Test API connection
echo "Example 2: Test OpenAI API Connection"
echo "Command: python cli.py test-connection"
echo ""
python cli.py test-connection
pause

# Example 3: List available tools
echo "Example 3: List Available Tools (Simple)"
echo "Command: python cli.py list-tools"
echo ""
python cli.py list-tools
pause

# Example 4: List tools with details
echo "Example 4: List Available Tools (Detailed)"
echo "Command: python cli.py list-tools --detailed"
echo ""
python cli.py list-tools --detailed
pause

# Example 5: List available agents
echo "Example 5: List Available Agent Types"
echo "Command: python cli.py list-agents"
echo ""
python cli.py list-agents
pause

# Example 6: Simple query
echo "Example 6: Simple Query"
echo "Command: python cli.py run 'What is Python?'"
echo ""
python cli.py run "What is Python programming language? Keep it brief."
pause

# Example 7: Math calculation with tool
echo "Example 7: Math Calculation (Uses calculator tool)"
echo "Command: python cli.py run 'What is 25 * 48?'"
echo ""
python cli.py run "What is 25 * 48?"
pause

# Example 8: Get current time (uses tool)
echo "Example 8: Get Current Time (Uses get_time tool)"
echo "Command: python cli.py run 'What time is it?'"
echo ""
python cli.py run "What time is it right now?"
pause

# Example 9: Query with verbose mode
echo "Example 9: Query with Verbose Output"
echo "Command: python cli.py run 'Calculate 100 / 4' --verbose"
echo ""
python cli.py run "Calculate 100 divided by 4" --verbose
pause

# Example 10: Query with different model
echo "Example 10: Query with Different Model"
echo "Command: python cli.py run 'Tell me a joke' --model gpt-3.5-turbo"
echo ""
python cli.py run "Tell me a programming joke" --model gpt-3.5-turbo
pause

# Example 11: Creative query with high temperature
echo "Example 11: Creative Query (High Temperature)"
echo "Command: python cli.py run 'Write a haiku' --temperature 1.5"
echo ""
python cli.py run "Write a haiku about coding" --temperature 1.5
pause

# Example 12: Query without tools
echo "Example 12: Query Without Tools"
echo "Command: python cli.py run 'Explain recursion' --no-tools"
echo ""
python cli.py run "Explain recursion in one sentence" --no-tools
pause

# Example 13: Multiple calculations
echo "Example 13: Multiple Tool Uses"
echo "Command: python cli.py run 'What is 5*5 and what time is it?'"
echo ""
python cli.py run "Calculate 5 times 5, and also tell me what time it is"
pause

# Example 14: Text manipulation
echo "Example 14: Text Manipulation"
echo "Command: python cli.py run 'Convert HELLO WORLD to lowercase'"
echo ""
python cli.py run "Convert the text 'HELLO WORLD' to lowercase"
pause

# Example 15: Help for a command
echo "Example 15: Command Help"
echo "Command: python cli.py run --help"
echo ""
python cli.py run --help
pause

# Final message
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                 All Examples Completed!                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Try interactive mode next:"
echo "  python cli.py interactive"
echo ""
echo "For more information:"
echo "  python cli.py --help"
echo "  Read CLI_README.md"
echo "  Read QUICKSTART.md"
echo ""
