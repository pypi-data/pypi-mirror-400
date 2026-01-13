"""
Edit Tool - Edit files using string replacement.
"""
import os
from typing import ClassVar
from pydantic import Field
from indusagi.tools.base import BaseTool, get_tool_context


class Edit(BaseTool):
    """Edit files using exact string replacement."""

    name: ClassVar[str] = "edit"
    description: ClassVar[str] = """Replace text in a file using exact string matching.

IMPORTANT: You must Read the file first before editing.
The old_string must match exactly (including indentation).
If old_string appears multiple times, use replace_all or provide more context."""

    file_path: str = Field(..., description="Absolute path to the file to edit")
    old_string: str = Field(..., description="The exact text to replace")
    new_string: str = Field(..., description="The replacement text")
    replace_all: bool = Field(False, description="Replace all occurrences (default: False)")

    def execute(self) -> str:
        abs_path = os.path.abspath(self.file_path)

        # Precondition: file must have been read first
        if not get_tool_context().was_file_read(abs_path):
            return "Error: You must Read the file before editing it. Use the Read tool first."

        if self.old_string == self.new_string:
            return "Error: old_string and new_string must be different"

        if not os.path.exists(self.file_path):
            return f"Error: File does not exist: {self.file_path}"

        # Read current content
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file: {e}"

        # Check if old_string exists
        if self.old_string not in content:
            return "Error: old_string not found in file. Check for exact match including whitespace."

        # Check uniqueness
        count = content.count(self.old_string)
        if count > 1 and not self.replace_all:
            return f"Error: old_string appears {count} times. Set replace_all=True or provide more context to make it unique."

        # Perform replacement
        if self.replace_all:
            new_content = content.replace(self.old_string, self.new_string)
            replaced = count
        else:
            new_content = content.replace(self.old_string, self.new_string, 1)
            replaced = 1

        # Write back
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"Successfully replaced {replaced} occurrence(s) in {self.file_path}"
        except Exception as e:
            return f"Error writing file: {e}"
