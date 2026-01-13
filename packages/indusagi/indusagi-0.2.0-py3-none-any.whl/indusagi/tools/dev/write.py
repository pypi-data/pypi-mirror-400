"""
Write Tool - Create new files or overwrite existing files.
"""
import os
from typing import ClassVar
from pydantic import Field
from indusagi.tools.base import BaseTool, get_tool_context


class Write(BaseTool):
    """
    Writes a file to the local filesystem.

    Usage:
    - This tool will overwrite the existing file if there is one at the provided path.
    - If this is an existing file, you MUST use the Read tool first to read the file's contents.
    - ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.
    - NEVER proactively create documentation files (*.md) or README files.
    - Only use emojis if the user explicitly requests it.
    """

    name: ClassVar[str] = "write"
    description: ClassVar[str] = """Write content to a file.

Creates new files or overwrites existing ones.
IMPORTANT: You must Read existing files before overwriting them.
Prefer Edit for modifying existing files."""

    file_path: str = Field(..., description="Path to the file to write (absolute or relative to current working directory)")
    content: str = Field(..., description="The content to write to the file")

    def execute(self) -> str:
        # Convert to absolute path if needed
        if not os.path.isabs(self.file_path):
            self.file_path = os.path.abspath(self.file_path)

        # Check if file already exists
        file_exists = os.path.exists(self.file_path)

        if file_exists:
            # For existing files, check if the file has been read first
            abs_file_path = os.path.abspath(self.file_path)
            file_has_been_read = get_tool_context().was_file_read(abs_file_path)

            if not file_has_been_read:
                return "Error: You must use Read tool at least once before overwriting this existing file."

            # Verify it's a file and not a directory
            if not os.path.isfile(self.file_path):
                return f"Error: Path exists but is not a file: {self.file_path}"

            operation = "overwritten"
        else:
            # Create directory if it doesn't exist
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    return f"Error creating directory {directory}: {str(e)}"
            operation = "created"

        # Write the content to the file
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(self.content)

            # Get file stats
            file_size = os.path.getsize(self.file_path)
            line_count = self.content.count("\n") + (
                1 if self.content and not self.content.endswith("\n") else 0
            )

            # Mark file as read in context for future Write/Edit operations
            abs_path = os.path.abspath(self.file_path)
            get_tool_context().mark_file_read(abs_path)

            return f"Successfully {operation} file: {self.file_path}\nSize: {file_size} bytes, Lines: {line_count}"

        except PermissionError:
            return f"Error: Permission denied writing to file: {self.file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
