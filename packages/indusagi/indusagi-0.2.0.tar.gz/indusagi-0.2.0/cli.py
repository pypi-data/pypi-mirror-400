"""
Professional CLI Interface for indus-agents

A beautiful, production-ready command-line interface built with Typer and Rich.
Provides intuitive commands for interacting with AI agents, managing tools,
and maintaining conversation history.

Features:
- Rich formatting with beautiful output
- Markdown rendering for agent responses
- Loading spinners during API calls
- Comprehensive error handling
- Interactive chat mode with history
- API key validation
- Verbose logging support
- Model selection options

Author: indus-agents
License: MIT
"""

import os
import sys
import signal
from typing import Optional, List
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.spinner import Spinner
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.theme import Theme
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from dotenv import load_dotenv

from agent import Agent, AgentConfig
from tools import registry, ToolRegistry

# ============================================================================
# Application Setup
# ============================================================================

# Load environment variables from .env file if it exists
load_dotenv()

# Create custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "agent": "bold magenta",
    "user": "bold blue",
    "tool": "bold yellow",
})

# Initialize Rich console with custom theme
console = Console(theme=custom_theme)

# Initialize Typer app
app = typer.Typer(
    name="agent-cli",
    help="Professional indus-agents CLI - Interact with intelligent agents powered by OpenAI",
    add_completion=False,
    rich_markup_mode="rich",
)

# Global state for signal handling
should_exit = False


# ============================================================================
# Utility Functions
# ============================================================================

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global should_exit
    should_exit = True
    console.print("\n\n[warning]Interrupted by user. Exiting gracefully...[/warning]")
    sys.exit(0)


# Register signal handler
signal.signal(signal.SIGINT, signal_handler)


def print_banner():
    """Display a beautiful welcome banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║            INDUS-AGENTS - CLI Interface                       ║
    ║                                                               ║
    ║              Intelligent Agents Powered by OpenAI             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def validate_api_key() -> bool:
    """
    Validate that OpenAI API key is configured.

    Returns:
        True if API key is set, False otherwise
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        console.print(Panel(
            "[error]OpenAI API key not found![/error]\n\n"
            "Please set your API key using one of these methods:\n\n"
            "1. Environment variable:\n"
            "   [info]export OPENAI_API_KEY='your-key-here'[/info]\n\n"
            "2. Windows PowerShell:\n"
            "   [info]$env:OPENAI_API_KEY='your-key-here'[/info]\n\n"
            "3. .env file in project directory:\n"
            "   [info]OPENAI_API_KEY=your-key-here[/info]\n\n"
            "Get your API key from: https://platform.openai.com/api-keys",
            title="API Key Required",
            border_style="error"
        ))
        return False

    # Mask the API key for display (show only first 7 and last 4 characters)
    masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"

    if os.getenv("VERBOSE"):
        console.print(f"[success]API key found:[/success] {masked_key}")

    return True


def print_error(message: str, title: str = "Error"):
    """Print a formatted error message."""
    console.print(Panel(
        f"[error]{message}[/error]",
        title=title,
        border_style="error"
    ))


def print_success(message: str, title: str = "Success"):
    """Print a formatted success message."""
    console.print(Panel(
        f"[success]{message}[/success]",
        title=title,
        border_style="success"
    ))


def print_info(message: str, title: str = "Info"):
    """Print a formatted info message."""
    console.print(Panel(
        f"[info]{message}[/info]",
        title=title,
        border_style="info"
    ))


def render_markdown_response(content: str, title: str = "Agent Response"):
    """
    Render agent response as markdown in a beautiful panel.

    Args:
        content: Response text to render
        title: Panel title
    """
    if not content:
        content = "*No response generated*"

    md = Markdown(content)
    console.print(Panel(
        md,
        title=f"[agent]{title}[/agent]",
        border_style="agent",
        padding=(1, 2)
    ))


def create_agent_from_options(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    verbose: bool = False
) -> Agent:
    """
    Create an Agent instance with specified options.

    Args:
        model: OpenAI model to use
        temperature: Sampling temperature
        verbose: Enable verbose output

    Returns:
        Configured Agent instance
    """
    # Create config from environment defaults
    config = AgentConfig.from_env()

    # Override with provided options
    if model:
        config.model = model
    if temperature is not None:
        config.temperature = temperature

    # Display configuration in verbose mode
    if verbose:
        config_table = Table(title="Agent Configuration", box=box.ROUNDED)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="yellow")

        config_table.add_row("Model", config.model)
        config_table.add_row("Max Tokens", str(config.max_tokens))
        config_table.add_row("Temperature", str(config.temperature))
        config_table.add_row("Top P", str(config.top_p))
        config_table.add_row("Max Retries", str(config.max_retries))

        console.print(config_table)
        console.print()

    # Create agent
    agent = Agent(
        name="CLI-Agent",
        role="Helpful AI assistant with tool access",
        config=config
    )

    return agent


# ============================================================================
# CLI Commands
# ============================================================================

@app.command()
def run(
    prompt: str = typer.Argument(..., help="Query to send to the agent"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="OpenAI model to use (e.g., gpt-4o, gpt-4-turbo)"),
    temperature: Optional[float] = typer.Option(None, "--temperature", "-t", help="Temperature for response generation (0.0-2.0)"),
    no_tools: bool = typer.Option(False, "--no-tools", help="Disable tool usage"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    Execute a single query with the AI agent.

    Examples:

        agent-cli run "What is 25 * 48?"

        agent-cli run "Explain quantum computing" --model gpt-4o

        agent-cli run "Creative story" --temperature 1.5
    """
    # Set verbose environment variable
    if verbose:
        os.environ["VERBOSE"] = "1"

    # Validate API key
    if not validate_api_key():
        raise typer.Exit(1)

    try:
        # Create agent
        agent = create_agent_from_options(model, temperature, verbose)

        # Display query
        console.print(Panel(
            f"[user]{prompt}[/user]",
            title="Your Query",
            border_style="user"
        ))
        console.print()

        # Process with loading spinner
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(description="Agent is thinking...", total=None)

            if no_tools:
                response = agent.process(prompt)
            else:
                response = agent.process_with_tools(
                    prompt,
                    tools=registry.schemas,
                    tool_executor=registry
                )

        # Display response
        console.print()
        render_markdown_response(response)

        # Show token usage in verbose mode
        if verbose:
            token_estimate = agent.get_token_count_estimate()
            console.print(f"\n[info]Estimated tokens used: {token_estimate}[/info]")

    except ValueError as e:
        print_error(str(e), "Configuration Error")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}", "Runtime Error")
        if verbose:
            import traceback
            console.print("\n[error]Full traceback:[/error]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def interactive(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="OpenAI model to use"),
    temperature: Optional[float] = typer.Option(None, "--temperature", "-t", help="Temperature (0.0-2.0)"),
    no_tools: bool = typer.Option(False, "--no-tools", help="Disable tool usage"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    Start an interactive chat session with the agent.

    Maintains conversation history across multiple exchanges.

    Special Commands:

        /quit or /exit - Exit the chat

        /clear - Clear conversation history

        /history - Show conversation history

        /tokens - Show estimated token usage

        /help - Show help message

    Example:

        agent-cli interactive

        agent-cli interactive --model gpt-4o --temperature 0.3
    """
    # Set verbose environment variable
    if verbose:
        os.environ["VERBOSE"] = "1"

    # Validate API key
    if not validate_api_key():
        raise typer.Exit(1)

    # Display banner
    print_banner()
    console.print()

    try:
        # Create agent
        agent = create_agent_from_options(model, temperature, verbose)

        # Welcome message
        welcome_text = (
            "Welcome to [agent]Interactive Chat Mode[/agent]!\n\n"
            "Chat naturally with the AI agent. Your conversation history is maintained.\n\n"
            "Special commands:\n"
            "  [info]/quit[/info] or [info]/exit[/info] - Exit chat\n"
            "  [info]/clear[/info] - Clear history\n"
            "  [info]/history[/info] - Show history\n"
            "  [info]/tokens[/info] - Show token usage\n"
            "  [info]/help[/info] - Show this help\n\n"
            "Type your message and press Enter to chat!"
        )
        console.print(Panel(welcome_text, border_style="info", title="Getting Started"))
        console.print()

        # Chat loop
        message_count = 0

        while not should_exit:
            try:
                # Get user input
                user_input = Prompt.ask("\n[user]You[/user]")

                # Handle empty input
                if not user_input.strip():
                    continue

                # Handle special commands
                if user_input.strip().lower() in ["/quit", "/exit"]:
                    if Confirm.ask("[warning]Are you sure you want to exit?[/warning]"):
                        console.print("\n[success]Thank you for using indus-agents CLI![/success]\n")
                        break
                    continue

                elif user_input.strip().lower() == "/clear":
                    agent.clear_history()
                    message_count = 0
                    print_success("Conversation history cleared!", "History Cleared")
                    continue

                elif user_input.strip().lower() == "/history":
                    history = agent.get_history()
                    if not history:
                        print_info("No conversation history yet.", "History")
                    else:
                        history_table = Table(title="Conversation History", box=box.ROUNDED)
                        history_table.add_column("#", style="cyan", width=4)
                        history_table.add_column("Role", style="yellow", width=10)
                        history_table.add_column("Content", style="white")

                        for idx, msg in enumerate(history, 1):
                            role = msg.get("role", "unknown")
                            content = msg.get("content", "")
                            # Truncate long messages
                            if len(content) > 100:
                                content = content[:97] + "..."
                            history_table.add_row(str(idx), role, content)

                        console.print(history_table)
                    continue

                elif user_input.strip().lower() == "/tokens":
                    token_estimate = agent.get_token_count_estimate()
                    message_count_display = len(agent.get_history())
                    print_info(
                        f"Messages: {message_count_display}\n"
                        f"Estimated tokens: {token_estimate}",
                        "Token Usage"
                    )
                    continue

                elif user_input.strip().lower() == "/help":
                    console.print(Panel(welcome_text, border_style="info", title="Help"))
                    continue

                # Process regular input
                console.print()
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    progress.add_task(description="Agent is thinking...", total=None)

                    if no_tools:
                        response = agent.process(user_input)
                    else:
                        response = agent.process_with_tools(
                            user_input,
                            tools=registry.schemas,
                            tool_executor=registry
                        )

                # Display response
                console.print()
                render_markdown_response(response, "Agent")

                message_count += 1

            except KeyboardInterrupt:
                console.print("\n\n[warning]Use /quit to exit gracefully[/warning]")
                continue
            except EOFError:
                console.print("\n\n[success]Goodbye![/success]\n")
                break

    except ValueError as e:
        print_error(str(e), "Configuration Error")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}", "Runtime Error")
        if verbose:
            import traceback
            console.print("\n[error]Full traceback:[/error]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def version():
    """
    Display version information about indus-agents.
    """
    version_info = Table(title="indus-agents - Version Info", box=box.DOUBLE)
    version_info.add_column("Component", style="cyan", width=20)
    version_info.add_column("Version/Info", style="yellow")

    version_info.add_row("Framework", "1.0.0")
    version_info.add_row("CLI Version", "1.0.0")
    version_info.add_row("Python", f"{sys.version.split()[0]}")

    try:
        import openai
        version_info.add_row("OpenAI SDK", openai.__version__)
    except:
        version_info.add_row("OpenAI SDK", "Not installed")

    try:
        from rich import __version__ as rich_version
        version_info.add_row("Rich", rich_version)
    except:
        version_info.add_row("Rich", "Unknown")

    try:
        import typer
        version_info.add_row("Typer", typer.__version__)
    except:
        version_info.add_row("Typer", "Unknown")

    # Check if API key is configured
    api_key_status = "Configured" if os.getenv("OPENAI_API_KEY") else "Not configured"
    version_info.add_row("API Key", api_key_status)

    console.print(version_info)
    console.print()


@app.command("list-tools")
def list_tools(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed tool information"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    Display all available tools that agents can use.

    Examples:

        agent-cli list-tools

        agent-cli list-tools --detailed
    """
    tool_names = registry.list_tools()

    if not tool_names:
        print_info("No tools registered.", "Available Tools")
        return

    if detailed:
        # Detailed view with descriptions
        for tool_name in tool_names:
            try:
                info = registry.get_tool_info(tool_name)
                schema = info["schema"]
                func_info = schema["function"]

                # Create a panel for each tool
                tool_details = f"[bold]Description:[/bold] {func_info['description']}\n\n"

                params = func_info["parameters"]["properties"]
                required = func_info["parameters"]["required"]

                if params:
                    tool_details += "[bold]Parameters:[/bold]\n"
                    for param_name, param_info in params.items():
                        param_type = param_info.get("type", "unknown")
                        param_desc = param_info.get("description", "No description")
                        required_badge = " [red](required)[/red]" if param_name in required else " [dim](optional)[/dim]"
                        tool_details += f"  • [cyan]{param_name}[/cyan] ({param_type}){required_badge}\n"
                        tool_details += f"    {param_desc}\n"
                else:
                    tool_details += "[dim]No parameters[/dim]\n"

                if info["dangerous"]:
                    tool_details += "\n[red]⚠ WARNING: This is a dangerous tool[/red]"

                console.print(Panel(
                    tool_details,
                    title=f"[tool]{tool_name}[/tool]",
                    border_style="tool",
                    padding=(1, 2)
                ))
                console.print()

            except Exception as e:
                if verbose:
                    console.print(f"[error]Error loading tool '{tool_name}': {e}[/error]")
    else:
        # Simple list view
        tools_table = Table(
            title=f"Available Tools ({len(tool_names)})",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        tools_table.add_column("#", style="dim", width=4)
        tools_table.add_column("Tool Name", style="tool")
        tools_table.add_column("Description", style="white")

        for idx, tool_name in enumerate(tool_names, 1):
            try:
                info = registry.get_tool_info(tool_name)
                description = info["schema"]["function"]["description"]
                # Truncate long descriptions
                if len(description) > 80:
                    description = description[:77] + "..."
                tools_table.add_row(str(idx), tool_name, description)
            except:
                tools_table.add_row(str(idx), tool_name, "[dim]No description[/dim]")

        console.print(tools_table)
        console.print(f"\n[info]Tip: Use --detailed flag for more information[/info]\n")


@app.command("test-connection")
def test_connection(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to test with"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    Test connectivity to OpenAI API.

    Verifies that your API key is valid and you can communicate with OpenAI.

    Example:

        agent-cli test-connection

        agent-cli test-connection --model gpt-4o
    """
    # Validate API key first
    if not validate_api_key():
        raise typer.Exit(1)

    console.print(Panel(
        "[info]Testing connection to OpenAI API...[/info]",
        title="Connection Test",
        border_style="info"
    ))
    console.print()

    try:
        # Create a simple agent for testing
        config = AgentConfig.from_env()
        if model:
            config.model = model

        if verbose:
            console.print(f"[info]Testing with model: {config.model}[/info]")
            console.print()

        agent = Agent(
            name="TestAgent",
            role="Connection tester",
            config=config
        )

        # Send a simple test query
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(description="Sending test query...", total=None)
            response = agent.process("Say 'Connection successful' and nothing else.")

        console.print()

        # Display results
        results_table = Table(title="Connection Test Results", box=box.ROUNDED)
        results_table.add_column("Check", style="cyan", width=25)
        results_table.add_column("Status", style="green", width=15)
        results_table.add_column("Details", style="white")

        results_table.add_row(
            "API Key",
            "[success]Valid[/success]",
            "Authentication successful"
        )
        results_table.add_row(
            "Model",
            "[success]Available[/success]",
            config.model
        )
        results_table.add_row(
            "Response",
            "[success]Received[/success]",
            response[:50] + "..." if len(response) > 50 else response
        )

        console.print(results_table)
        console.print()
        print_success(
            "Connection test completed successfully!\nYou're ready to use indus-agents.",
            "Test Passed"
        )

    except ValueError as e:
        print_error(f"Configuration error: {str(e)}", "Test Failed")
        raise typer.Exit(1)
    except Exception as e:
        print_error(
            f"Connection test failed: {str(e)}\n\n"
            "Common issues:\n"
            "  • Invalid API key\n"
            "  • Network connectivity problems\n"
            "  • Insufficient API credits\n"
            "  • Model not available for your account",
            "Test Failed"
        )
        if verbose:
            import traceback
            console.print("\n[error]Full traceback:[/error]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command("list-agents")
def list_agents():
    """
    Show available agent configurations.

    Displays pre-configured agent types and their capabilities.
    """
    agents_table = Table(
        title="Available Agent Configurations",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    agents_table.add_column("Agent Type", style="agent", width=20)
    agents_table.add_column("Role", style="yellow", width=30)
    agents_table.add_column("Capabilities", style="white")

    # Predefined agent configurations
    agent_configs = [
        {
            "type": "General Assistant",
            "role": "Helpful AI assistant",
            "capabilities": "General knowledge, conversation, problem-solving"
        },
        {
            "type": "Math Assistant",
            "role": "Mathematical problem solver",
            "capabilities": "Calculator, numerical analysis, equations"
        },
        {
            "type": "Data Analyst",
            "role": "Data analysis and insights",
            "capabilities": "Text analysis, statistics, data interpretation"
        },
        {
            "type": "Code Helper",
            "role": "Programming assistant",
            "capabilities": "Code explanation, debugging, best practices"
        },
        {
            "type": "Creative Writer",
            "role": "Creative content generation",
            "capabilities": "Stories, poetry, creative text (high temperature)"
        },
    ]

    for agent_config in agent_configs:
        agents_table.add_row(
            agent_config["type"],
            agent_config["role"],
            agent_config["capabilities"]
        )

    console.print(agents_table)
    console.print()
    console.print(Panel(
        "[info]Note:[/info] All agents have access to the same tool registry.\n"
        "The role and system prompt determine their behavior and focus.",
        border_style="info"
    ))
    console.print()


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n\n[warning]Interrupted by user[/warning]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[error]Unexpected error: {str(e)}[/error]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
