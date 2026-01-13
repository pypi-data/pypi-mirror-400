"""
Grep Tool - Content search using ripgrep.
"""
import os
import subprocess
from typing import Literal, Optional, ClassVar
from pydantic import Field
from indusagi.tools.base import BaseTool


class Grep(BaseTool):
    """
    A powerful search tool built on ripgrep.

    Usage:
    - ALWAYS use Grep for search tasks. NEVER invoke `grep` or `rg` as a Bash command
    - Supports full regex syntax (e.g., "log.*Error", "function\\s+\\w+")
    - Filter files with glob parameter (e.g., "*.js", "**/*.tsx") or type parameter
    - Output modes: "content" shows matching lines, "files_with_matches" shows only file paths, "count" shows match counts
    - Pattern syntax: Uses ripgrep (not grep) - literal braces need escaping
    - Multiline matching: By default patterns match within single lines only
    """

    name: ClassVar[str] = "grep"
    description: ClassVar[str] = """Search for patterns in files using ripgrep.

Supports regex patterns and various output modes.
Respects .gitignore by default."""

    pattern: str = Field(
        ..., description="The regular expression pattern to search for in file contents"
    )
    path: Optional[str] = Field(
        None,
        description="File or directory to search in. Defaults to current working directory.",
    )
    glob: Optional[str] = Field(
        None,
        description="Glob pattern to filter files (e.g. '*.js', '*.{ts,tsx}')",
    )
    output_mode: Optional[Literal["content", "files_with_matches", "count"]] = Field(
        "files_with_matches",
        description="Output mode: 'content' shows matching lines, 'files_with_matches' shows file paths, 'count' shows match counts.",
    )
    B: Optional[int] = Field(
        None,
        description="Number of lines to show before each match (requires output_mode: 'content').",
        alias="-B",
    )
    A: Optional[int] = Field(
        None,
        description="Number of lines to show after each match (requires output_mode: 'content').",
        alias="-A",
    )
    C: Optional[int] = Field(
        None,
        description="Number of lines to show before and after each match (requires output_mode: 'content').",
        alias="-C",
    )
    n: Optional[bool] = Field(
        None,
        description="Show line numbers in output (requires output_mode: 'content').",
        alias="-n",
    )
    i: Optional[bool] = Field(
        None, description="Case insensitive search", alias="-i"
    )
    type: Optional[str] = Field(
        None,
        description="File type to search (e.g., js, py, rust, go, java).",
    )
    head_limit: Optional[int] = Field(
        None,
        description="Limit output to first N lines/entries.",
    )
    multiline: Optional[bool] = Field(
        False,
        description="Enable multiline mode where . matches newlines.",
    )

    def execute(self) -> str:
        try:
            # Check if ripgrep is available
            try:
                subprocess.run(["rg", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return "Error: ripgrep (rg) is not installed. Please install ripgrep first."

            # Build ripgrep command
            cmd = ["rg", "--color=never"]

            # Add case insensitive flag
            if getattr(self, "i", None):
                cmd.append("-i")

            # Add multiline flag
            if self.multiline:
                cmd.extend(["-U", "--multiline-dotall"])

            # Add file type filter
            if self.type:
                cmd.extend(["--type", self.type])

            # Add glob filter
            if self.glob:
                cmd.extend(["--glob", self.glob])

            # Handle output mode
            if self.output_mode == "files_with_matches":
                cmd.append("-l")
            elif self.output_mode == "count":
                cmd.append("-c")
            elif self.output_mode == "content":
                # Add line numbers if requested
                if getattr(self, "n", None):
                    cmd.append("-n")

                # Add context lines
                if getattr(self, "C", None):
                    cmd.extend(["-C", str(getattr(self, "C"))])
                elif getattr(self, "A", None) or getattr(self, "B", None):
                    if getattr(self, "A", None):
                        cmd.extend(["-A", str(getattr(self, "A"))])
                    if getattr(self, "B", None):
                        cmd.extend(["-B", str(getattr(self, "B"))])

            # Add pattern
            cmd.append(self.pattern)

            # Add search path; respect .gitignore by default via ripgrep
            if self.path:
                cmd.append(self.path)
            else:
                cmd.append(".")

            # Execute ripgrep
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    cwd=os.getcwd(),
                )

                stdout = (result.stdout or "").rstrip()
                stderr = (result.stderr or "").rstrip()

                # Exit code handling: 1 means no matches, other non-zero means error
                if result.returncode == 1 and not stdout:
                    return f"Exit code: 1\nNo matches found for pattern: {self.pattern}"

                if result.returncode not in (0, 1):
                    sections = [f"Exit code: {result.returncode}"]
                    if stdout:
                        sections.append("--- STDOUT ---")
                        sections.append(stdout)
                    if stderr:
                        sections.append("--- STDERR ---")
                        sections.append(stderr)
                    return "\n".join(sections).strip()

                output = stdout

                # Apply head_limit if specified
                if self.head_limit and output:
                    lines = output.split("\n")
                    if len(lines) > self.head_limit:
                        output = "\n".join(lines[: self.head_limit])
                        output += (
                            f"\n... (output limited to first {self.head_limit} lines)"
                        )

                # Truncate very large outputs to 30000 characters
                truncated = False
                if len(output) > 30000:
                    output = output[:30000]
                    truncated = True

                sections = [f"Exit code: {result.returncode}"]
                if output:
                    sections.append("--- STDOUT ---")
                    sections.append(output)
                if stderr:
                    sections.append("--- STDERR ---")
                    sections.append(stderr)
                if truncated:
                    sections.append("... (output truncated to 30000 characters)")

                return "\n".join(sections).strip()

            except subprocess.TimeoutExpired:
                return "Error: Search timed out after 30 seconds"

        except Exception as e:
            return f"Error during grep search: {str(e)}"
