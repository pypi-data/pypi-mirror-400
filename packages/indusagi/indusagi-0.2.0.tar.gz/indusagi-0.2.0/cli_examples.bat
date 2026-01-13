@echo off
REM indus-agents CLI - Usage Examples (Windows)
REM This script demonstrates all CLI commands with various options

echo ===============================================================
echo       indus-agents CLI - Interactive Examples
echo ===============================================================
echo.

REM Example 1: Check version
echo Example 1: Check CLI Version
echo Command: python cli.py version
echo.
python cli.py version
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 2: Test API connection
echo Example 2: Test OpenAI API Connection
echo Command: python cli.py test-connection
echo.
python cli.py test-connection
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 3: List available tools
echo Example 3: List Available Tools (Simple)
echo Command: python cli.py list-tools
echo.
python cli.py list-tools
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 4: List tools with details
echo Example 4: List Available Tools (Detailed)
echo Command: python cli.py list-tools --detailed
echo.
python cli.py list-tools --detailed
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 5: List available agents
echo Example 5: List Available Agent Types
echo Command: python cli.py list-agents
echo.
python cli.py list-agents
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 6: Simple query
echo Example 6: Simple Query
echo Command: python cli.py run "What is Python?"
echo.
python cli.py run "What is Python programming language? Keep it brief."
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 7: Math calculation with tool
echo Example 7: Math Calculation (Uses calculator tool)
echo Command: python cli.py run "What is 25 * 48?"
echo.
python cli.py run "What is 25 * 48?"
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 8: Get current time
echo Example 8: Get Current Time (Uses get_time tool)
echo Command: python cli.py run "What time is it?"
echo.
python cli.py run "What time is it right now?"
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 9: Query with verbose mode
echo Example 9: Query with Verbose Output
echo Command: python cli.py run "Calculate 100 / 4" --verbose
echo.
python cli.py run "Calculate 100 divided by 4" --verbose
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 10: Query with different model
echo Example 10: Query with Different Model
echo Command: python cli.py run "Tell me a joke" --model gpt-3.5-turbo
echo.
python cli.py run "Tell me a programming joke" --model gpt-3.5-turbo
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 11: Creative query
echo Example 11: Creative Query (High Temperature)
echo Command: python cli.py run "Write a haiku" --temperature 1.5
echo.
python cli.py run "Write a haiku about coding" --temperature 1.5
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Example 12: Query without tools
echo Example 12: Query Without Tools
echo Command: python cli.py run "Explain recursion" --no-tools
echo.
python cli.py run "Explain recursion in one sentence" --no-tools
echo.
pause
echo.
echo ---------------------------------------------------------------
echo.

REM Final message
echo.
echo ===============================================================
echo                 All Examples Completed!
echo ===============================================================
echo.
echo Try interactive mode next:
echo   python cli.py interactive
echo.
echo For more information:
echo   python cli.py --help
echo   Read CLI_README.md
echo   Read QUICKSTART.md
echo.
pause
