"""
Read Tool - Read file contents with line numbers.
"""
import os
from typing import Optional, ClassVar
from pydantic import Field
from indusagi.tools.base import BaseTool, get_tool_context


class Read(BaseTool):
    """Read file contents with line numbers."""

    name: ClassVar[str] = "read"
    description: ClassVar[str] = """Read a file from the filesystem.

Returns file contents with line numbers. Use this before Edit to see current content.
Supports text files, images (displays visually), and Jupyter notebooks."""

    file_path: str = Field(..., description="Absolute path to the file to read")
    offset: Optional[int] = Field(None, description="Line number to start reading from (1-indexed)")
    limit: Optional[int] = Field(None, description="Maximum number of lines to read")

    def execute(self) -> str:
        abs_path = os.path.abspath(self.file_path)

        # Mark file as read for Edit precondition
        get_tool_context().mark_file_read(abs_path)

        if not os.path.exists(self.file_path):
            return f"Error: File does not exist: {self.file_path}"

        if not os.path.isfile(self.file_path):
            return f"Error: Not a file: {self.file_path}"

        # Try to read file
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(self.file_path, "r", encoding="latin-1") as f:
                    lines = f.readlines()
            except Exception as e:
                return f"Error: Cannot decode file: {self.file_path} ({e})"
        except Exception as e:
            return f"Error reading file: {e}"

        if not lines:
            return f"Warning: File is empty: {self.file_path}"

        # Apply offset and limit
        start = (self.offset - 1) if self.offset else 0
        start = max(0, min(start, len(lines)))
        end = start + (self.limit or 2000)

        selected = lines[start:end]

        # Format with line numbers
        result = []
        for i, line in enumerate(selected, start=start + 1):
            # Truncate very long lines
            if len(line) > 2000:
                line = line[:1997] + "..."
            result.append(f"{i:>6}\t{line.rstrip()}")

        output = "\n".join(result)

        if len(selected) < len(lines):
            output += f"\n\n[Showing lines {start + 1}-{start + len(selected)} of {len(lines)} total]"

        return output
