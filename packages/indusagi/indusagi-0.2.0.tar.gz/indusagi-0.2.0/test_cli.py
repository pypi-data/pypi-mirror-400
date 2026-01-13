"""
Test script for indus-agents CLI

This script tests the CLI functionality without requiring API calls.
Useful for verifying installation and basic functionality.
"""

import sys
import os
from pathlib import Path

# Add the project directory to the path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        import typer
        print("  ✓ typer imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import typer: {e}")
        return False

    try:
        from rich.console import Console
        print("  ✓ rich imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import rich: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("  ✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import python-dotenv: {e}")
        return False

    try:
        from pydantic import BaseModel
        print("  ✓ pydantic imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import pydantic: {e}")
        return False

    try:
        import openai
        print("  ✓ openai imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import openai: {e}")
        return False

    print("\n✓ All imports successful!\n")
    return True


def test_cli_module():
    """Test that CLI module can be imported."""
    print("Testing CLI module...")

    try:
        import cli
        print("  ✓ cli.py imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import cli: {e}")
        return False

    try:
        from cli import app
        print("  ✓ CLI app object accessible")
    except ImportError as e:
        print(f"  ✗ Failed to access CLI app: {e}")
        return False

    print("\n✓ CLI module tests passed!\n")
    return True


def test_agent_module():
    """Test that Agent module can be imported."""
    print("Testing Agent module...")

    try:
        from agent import Agent, AgentConfig
        print("  ✓ Agent classes imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import Agent: {e}")
        return False

    print("\n✓ Agent module tests passed!\n")
    return True


def test_tools_module():
    """Test that Tools module can be imported."""
    print("Testing Tools module...")

    try:
        from tools import registry, ToolRegistry
        print("  ✓ Tool registry imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import tools: {e}")
        return False

    try:
        tool_names = registry.list_tools()
        print(f"  ✓ Found {len(tool_names)} registered tools")
        for tool in tool_names[:5]:  # Show first 5
            print(f"    - {tool}")
        if len(tool_names) > 5:
            print(f"    ... and {len(tool_names) - 5} more")
    except Exception as e:
        print(f"  ✗ Failed to list tools: {e}")
        return False

    print("\n✓ Tools module tests passed!\n")
    return True


def test_config():
    """Test configuration loading."""
    print("Testing configuration...")

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
        print(f"  ✓ OPENAI_API_KEY found: {masked_key}")
    else:
        print("  ⚠ OPENAI_API_KEY not set (required for actual API calls)")

    try:
        from agent import AgentConfig
        config = AgentConfig.from_env()
        print(f"  ✓ AgentConfig loaded successfully")
        print(f"    - Model: {config.model}")
        print(f"    - Temperature: {config.temperature}")
        print(f"    - Max tokens: {config.max_tokens}")
    except Exception as e:
        print(f"  ✗ Failed to load config: {e}")
        return False

    print("\n✓ Configuration tests passed!\n")
    return True


def test_cli_help():
    """Test that CLI help command works."""
    print("Testing CLI help command...")

    try:
        from typer.testing import CliRunner
        from cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        if result.exit_code == 0:
            print("  ✓ CLI help command works")
            print("  ✓ Exit code: 0")
        else:
            print(f"  ✗ CLI help failed with exit code: {result.exit_code}")
            return False
    except Exception as e:
        print(f"  ✗ Failed to test CLI help: {e}")
        return False

    print("\n✓ CLI help tests passed!\n")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("indus-agents CLI - Test Suite")
    print("=" * 70)
    print()

    tests = [
        test_imports,
        test_cli_module,
        test_agent_module,
        test_tools_module,
        test_config,
        test_cli_help,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}\n")
            failed += 1

    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    print()

    if failed == 0:
        print("✓ All tests passed! CLI is ready to use.")
        print("\nNext steps:")
        print("  1. Set OPENAI_API_KEY in .env file")
        print("  2. Run: python cli.py test-connection")
        print("  3. Try: python cli.py run 'Hello!'")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Check that all .py files are in the project directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())
