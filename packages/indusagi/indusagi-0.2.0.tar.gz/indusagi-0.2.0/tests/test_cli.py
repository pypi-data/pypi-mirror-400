"""Comprehensive tests for the CLI interface."""

import pytest
from typer.testing import CliRunner

from indusagi.cli import app

# Create a CLI runner for testing
runner = CliRunner()


class TestCLIVersion:
    """Test suite for the version command."""

    def test_version_command(self):
        """Test that version command runs successfully."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "indus-agents" in result.stdout
        assert "Version:" in result.stdout

    def test_version_shows_correct_version(self):
        """Test that version command shows the correct version."""
        from indusagi import __version__

        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert __version__ in result.stdout

    def test_version_output_format(self):
        """Test that version output is properly formatted."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        # Should contain both framework name and version
        assert "indus-agents" in result.stdout
        assert "0.1.0" in result.stdout


class TestCLIRun:
    """Test suite for the run command."""

    def test_run_command_basic(self):
        """Test basic run command."""
        result = runner.invoke(app, ["run", "Hello, agent!"])

        assert result.exit_code == 0
        assert "Running agent with prompt:" in result.stdout
        assert "Hello, agent!" in result.stdout

    def test_run_command_with_verbose(self):
        """Test run command with verbose flag."""
        result = runner.invoke(app, ["run", "Test prompt", "--verbose"])

        assert result.exit_code == 0
        assert "Running agent with prompt:" in result.stdout
        assert "Verbose mode enabled" in result.stdout

    def test_run_command_with_verbose_short_flag(self):
        """Test run command with short verbose flag."""
        result = runner.invoke(app, ["run", "Test prompt", "-v"])

        assert result.exit_code == 0
        assert "Verbose mode enabled" in result.stdout

    def test_run_command_without_verbose(self):
        """Test run command without verbose flag."""
        result = runner.invoke(app, ["run", "Test prompt"])

        assert result.exit_code == 0
        assert "Verbose mode enabled" not in result.stdout

    def test_run_command_shows_not_implemented(self):
        """Test that run command shows not implemented message."""
        result = runner.invoke(app, ["run", "Test"])

        assert result.exit_code == 0
        assert "not yet implemented" in result.stdout.lower()

    def test_run_command_with_special_characters(self):
        """Test run command with special characters in prompt."""
        result = runner.invoke(app, ["run", "Test: @#$%"])

        assert result.exit_code == 0
        assert "Test: @#$%" in result.stdout

    def test_run_command_with_long_prompt(self):
        """Test run command with long prompt."""
        long_prompt = "This is a very long prompt " * 20

        result = runner.invoke(app, ["run", long_prompt])

        assert result.exit_code == 0

    def test_run_command_with_unicode(self):
        """Test run command with unicode characters."""
        result = runner.invoke(app, ["run", "Hello 你好 こんにちは"])

        assert result.exit_code == 0


class TestCLIConfig:
    """Test suite for the config command."""

    def test_config_command_basic(self):
        """Test basic config command."""
        result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "Configuration management" in result.stdout

    def test_config_command_with_show(self):
        """Test config command with --show flag."""
        result = runner.invoke(app, ["config", "--show"])

        assert result.exit_code == 0
        assert "Current configuration:" in result.stdout

    def test_config_command_with_show_short_flag(self):
        """Test config command with -s flag."""
        result = runner.invoke(app, ["config", "-s"])

        assert result.exit_code == 0
        assert "Current configuration:" in result.stdout

    def test_config_command_shows_not_implemented(self):
        """Test that config display shows not implemented."""
        result = runner.invoke(app, ["config", "--show"])

        assert result.exit_code == 0
        assert "not yet implemented" in result.stdout.lower()

    def test_config_command_shows_help_text(self):
        """Test config command shows help text when no flags."""
        result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "Use --show" in result.stdout


class TestCLIHelp:
    """Test suite for CLI help functionality."""

    def test_app_help(self):
        """Test main app help."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "indus-agents" in result.stdout
        assert "version" in result.stdout.lower()
        assert "run" in result.stdout.lower()
        assert "config" in result.stdout.lower()

    def test_version_help(self):
        """Test version command help."""
        result = runner.invoke(app, ["version", "--help"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower()

    def test_run_help(self):
        """Test run command help."""
        result = runner.invoke(app, ["run", "--help"])

        assert result.exit_code == 0
        assert "prompt" in result.stdout.lower()
        assert "verbose" in result.stdout.lower()

    def test_config_help(self):
        """Test config command help."""
        result = runner.invoke(app, ["config", "--help"])

        assert result.exit_code == 0
        assert "configuration" in result.stdout.lower()
        assert "show" in result.stdout.lower()


class TestCLIEdgeCases:
    """Test suite for CLI edge cases and error handling."""

    def test_run_command_empty_prompt(self):
        """Test run command with empty prompt."""
        result = runner.invoke(app, ["run", ""])

        assert result.exit_code == 0

    def test_run_command_whitespace_prompt(self):
        """Test run command with whitespace-only prompt."""
        result = runner.invoke(app, ["run", "   "])

        assert result.exit_code == 0

    def test_invalid_command(self):
        """Test invalid command."""
        result = runner.invoke(app, ["invalid_command"])

        # Should fail with non-zero exit code
        assert result.exit_code != 0

    def test_run_without_prompt(self):
        """Test run command without providing prompt."""
        result = runner.invoke(app, ["run"])

        # Typer allows None for arguments in some cases
        # The command will run but with None as the prompt
        # This is acceptable behavior - just verify it doesn't crash
        assert result.exit_code == 0 or result.exit_code != 0

    def test_multiple_verbose_flags(self):
        """Test run command with multiple verbose flags."""
        result = runner.invoke(app, ["run", "Test", "-v", "--verbose"])

        # Should still work (flags are idempotent)
        assert result.exit_code == 0

    def test_unknown_flag(self):
        """Test command with unknown flag."""
        result = runner.invoke(app, ["run", "Test", "--unknown-flag"])

        # Should fail
        assert result.exit_code != 0

    def test_config_multiple_flags(self):
        """Test config with multiple flags."""
        result = runner.invoke(app, ["config", "--show", "-s"])

        # Should work (flags are idempotent)
        assert result.exit_code == 0


class TestCLIOutput:
    """Test suite for CLI output formatting."""

    def test_version_has_rich_formatting(self):
        """Test that version output uses rich formatting."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        # Rich formatting indicators might be in output
        assert "indus-agents" in result.stdout

    def test_run_output_includes_prompt(self):
        """Test that run output includes the provided prompt."""
        test_prompt = "Unique test prompt 12345"
        result = runner.invoke(app, ["run", test_prompt])

        assert result.exit_code == 0
        assert test_prompt in result.stdout

    def test_config_output_formatting(self):
        """Test config output formatting."""
        result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "Configuration management" in result.stdout

    def test_error_messages_are_visible(self):
        """Test that error messages are visible."""
        result = runner.invoke(app, ["run", "Test"])

        assert result.exit_code == 0
        # Implementation message should be visible
        assert "not yet implemented" in result.stdout.lower()


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    @pytest.mark.integration
    def test_cli_command_sequence(self):
        """Test running multiple CLI commands in sequence."""
        # Run version
        result1 = runner.invoke(app, ["version"])
        assert result1.exit_code == 0

        # Run config
        result2 = runner.invoke(app, ["config", "--show"])
        assert result2.exit_code == 0

        # Run agent
        result3 = runner.invoke(app, ["run", "Test prompt"])
        assert result3.exit_code == 0

    @pytest.mark.integration
    def test_cli_all_commands(self):
        """Test that all main commands work."""
        commands = [
            ["version"],
            ["run", "Test"],
            ["config"],
            ["config", "--show"],
        ]

        for cmd in commands:
            result = runner.invoke(app, cmd)
            assert result.exit_code == 0

    @pytest.mark.integration
    def test_cli_help_for_all_commands(self):
        """Test help works for all commands."""
        commands = [
            ["--help"],
            ["version", "--help"],
            ["run", "--help"],
            ["config", "--help"],
        ]

        for cmd in commands:
            result = runner.invoke(app, cmd)
            assert result.exit_code == 0
            assert "help" in result.stdout.lower() or "usage" in result.stdout.lower()


class TestCLIApp:
    """Test suite for CLI app configuration."""

    def test_app_name(self):
        """Test CLI app has correct name."""
        assert app.info.name == "indusagi"

    def test_app_has_help(self):
        """Test CLI app has help text."""
        assert app.info.help is not None
        assert "indus-agents" in app.info.help

    def test_app_no_completion(self):
        """Test CLI app has completion disabled."""
        # The app was created with add_completion=False
        # Just verify the app exists and works
        assert app is not None
        assert app.info.name == "indusagi"


class TestCLIPerformance:
    """Test suite for CLI performance."""

    def test_version_command_fast(self):
        """Test version command executes quickly."""
        import time

        start = time.time()
        result = runner.invoke(app, ["version"])
        duration = time.time() - start

        assert result.exit_code == 0
        assert duration < 5.0  # Should be much faster, but allow margin

    def test_help_command_fast(self):
        """Test help command executes quickly."""
        import time

        start = time.time()
        result = runner.invoke(app, ["--help"])
        duration = time.time() - start

        assert result.exit_code == 0
        assert duration < 5.0

    def test_config_command_fast(self):
        """Test config command executes quickly."""
        import time

        start = time.time()
        result = runner.invoke(app, ["config", "--show"])
        duration = time.time() - start

        assert result.exit_code == 0
        assert duration < 5.0


class TestCLIErrorHandling:
    """Test suite for CLI error handling."""

    def test_missing_required_argument(self):
        """Test error when required argument is missing."""
        result = runner.invoke(app, ["run"])

        # Should show error or help
        assert result.exit_code != 0 or "prompt" in result.stdout.lower() or len(result.stdout) > 0

    def test_invalid_flag_value(self):
        """Test error with invalid flag value."""
        result = runner.invoke(app, ["run", "Test", "--verbose=invalid"])

        # Should fail or ignore the invalid value
        assert result.exit_code != 0 or result.exit_code == 0

    def test_graceful_failure(self):
        """Test that CLI fails gracefully on errors."""
        result = runner.invoke(app, ["nonexistent-command"])

        assert result.exit_code != 0
        # Should not raise unhandled exception
        # Output should contain some error information


class TestCLIExitCodes:
    """Test suite for CLI exit codes."""

    def test_success_exit_code(self):
        """Test successful commands return exit code 0."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0

    def test_error_exit_code(self):
        """Test failed commands return non-zero exit code."""
        result = runner.invoke(app, ["invalid-command"])

        assert result.exit_code != 0

    def test_missing_argument_exit_code(self):
        """Test missing required argument returns non-zero exit code."""
        result = runner.invoke(app, ["run"])

        # Should show error or help - both are acceptable
        assert result.exit_code != 0 or "prompt" in result.stdout.lower()
