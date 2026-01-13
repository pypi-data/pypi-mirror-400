"""
Bash Tool - Execute shell commands safely.
"""
import subprocess
import os
import sys
import threading
from typing import Optional, ClassVar
from pydantic import Field
from indusagi.tools.base import BaseTool

_bash_lock = threading.Lock()
_bash_busy = False


class Bash(BaseTool):
    """Execute bash commands with timeout and safety measures."""

    name: ClassVar[str] = "bash"
    description: ClassVar[str] = """Execute bash commands in the current working directory.

Use for: running tests, installing packages, git operations, building projects.
Do NOT use for: reading files (use Read), editing files (use Edit), searching (use Grep/Glob)."""

    command: str = Field(..., description="The bash command to execute")
    timeout: int = Field(
        120000,
        description="Timeout in milliseconds (max 600000)",
        ge=5000,
        le=600000
    )
    description_field: Optional[str] = Field(
        None,
        description="Brief description of what this command does",
        alias="command_description"
    )

    def execute(self) -> str:
        global _bash_busy

        if _bash_busy:
            return "Error: Terminal is busy. Wait for current command to complete."

        # ⚠️ VALIDATION: Detect if command looks like a description instead of actual bash command
        command_lower = self.command.lower().strip()

        # Check for common mistake patterns
        if command_lower.startswith("create project folder") or command_lower.startswith("create folder"):
            # Extract folder name if present
            parts = self.command.split()
            if len(parts) >= 3:
                # e.g., "Create project folder my_app" or "Create folder my_app"
                folder_name = parts[-1].strip()
                return (
                    f"❌ ERROR: Invalid bash command!\n\n"
                    f"You used: '{self.command}'\n"
                    f"This is a DESCRIPTION, not a bash command!\n\n"
                    f"✅ CORRECT command: mkdir {folder_name}\n\n"
                    f"Please use the actual bash command 'mkdir' to create folders."
                )
            else:
                return (
                    f"❌ ERROR: Invalid bash command!\n\n"
                    f"You used: '{self.command}'\n"
                    f"This is a DESCRIPTION, not a bash command!\n\n"
                    f"✅ To create a folder, use: mkdir <folder_name>\n\n"
                    f"Example: mkdir my_project"
                )

        # Check for other description-like patterns
        description_patterns = [
            "create a ", "make a ", "build a ", "set up ", "setup ",
            "install the", "run the", "execute the"
        ]

        if any(self.command.lower().startswith(pattern) for pattern in description_patterns):
            return (
                f"❌ ERROR: Invalid bash command!\n\n"
                f"You used: '{self.command}'\n"
                f"This looks like a DESCRIPTION, not a bash command!\n\n"
                f"Common bash commands:\n"
                f"  - mkdir <name>     (create folder)\n"
                f"  - cd <path>        (change directory)\n"
                f"  - ls               (list files)\n"
                f"  - python <file>    (run python)\n"
                f"  - npm install      (install packages)\n\n"
                f"Please use the actual bash command, not a description."
            )

        timeout_seconds = self.timeout / 1000

        with _bash_lock:
            _bash_busy = True
            try:
                # Platform-specific shell command
                if sys.platform == "win32":
                    # Windows: use cmd.exe
                    shell_cmd = ["cmd.exe", "/c", self.command]
                else:
                    # Unix/Linux/Mac: use bash
                    shell_cmd = ["/bin/bash", "-c", self.command]

                result = subprocess.run(
                    shell_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=os.getcwd(),
                    env={**os.environ, "TERM": "dumb"},
                )

                output = ""
                if result.stdout:
                    output = result.stdout
                if result.stderr:
                    if output:
                        output += "\n--- STDERR ---\n"
                    output += result.stderr

                if not output.strip():
                    return f"Exit code: {result.returncode}\n(No output)"

                # Truncate long output
                if len(output) > 30000:
                    output = output[-30000:]
                    output = "(truncated)\n" + output

                return f"Exit code: {result.returncode}\n{output.strip()}"

            except subprocess.TimeoutExpired:
                return f"Error: Command timed out after {timeout_seconds}s"
            except Exception as e:
                return f"Error executing command: {str(e)}"
            finally:
                _bash_busy = False
