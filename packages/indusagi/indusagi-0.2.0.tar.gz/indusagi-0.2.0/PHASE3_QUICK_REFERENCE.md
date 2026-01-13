# Phase 3 Development Tools - Quick Reference

## Import

```python
from indusagi.tools import (
    BaseTool, ToolContext, get_tool_context,
    Bash, Read, Edit, Write, Glob, Grep
)
```

## Tool Reference

### Bash - Execute Shell Commands

```python
tool = Bash(
    command="pytest tests/ -v",
    timeout=120000,  # milliseconds (default: 120000)
    description_field="Run tests"  # optional
)
result = tool.execute()  # or tool.run()
```

**Features:**
- Timeout: 5s - 600s (5000-600000ms)
- Output truncation at 30KB
- Thread-safe execution
- Returns exit code + stdout/stderr

### Read - Read File Contents

```python
tool = Read(
    file_path="/absolute/path/to/file.py",
    offset=10,   # optional: start line (1-indexed)
    limit=20     # optional: number of lines
)
result = tool.execute()
```

**Features:**
- Returns cat -n style output (line numbers)
- Marks file as "read" in context
- UTF-8/Latin-1 encoding fallback
- Default limit: 2000 lines

### Edit - Edit File with String Replacement

```python
# Must Read file first!
read_tool = Read(file_path="/path/to/file.py")
read_tool.execute()

tool = Edit(
    file_path="/path/to/file.py",
    old_string="old_function_name",
    new_string="new_function_name",
    replace_all=False  # True to replace all occurrences
)
result = tool.execute()
```

**Features:**
- Exact string matching
- Precondition: file must be Read first
- Single or multiple replacement
- Validation for uniqueness

### Write - Create or Overwrite Files

```python
# For new files - no precondition
tool = Write(
    file_path="/absolute/path/to/new_file.py",
    content="def hello():\n    print('Hello')\n"
)
result = tool.execute()

# For existing files - must Read first
read_tool = Read(file_path="/existing/file.py")
read_tool.execute()

tool = Write(
    file_path="/existing/file.py",
    content="new content"
)
result = tool.execute()
```

**Features:**
- Auto-creates directories
- Precondition: existing files must be Read
- Reports file size and line count
- Marks file as read after writing

### Glob - File Pattern Matching

```python
# Simple pattern
tool = Glob(
    pattern="*.py",
    path="/src"  # optional, defaults to cwd
)
result = tool.execute()

# Recursive pattern
tool = Glob(
    pattern="**/*.py",
    path="/project"
)
result = tool.execute()
```

**Features:**
- Supports `**` for recursive search
- Respects .gitignore patterns
- Sorted by modification time (newest first)
- Returns absolute paths

### Grep - Content Search with Ripgrep

```python
# Find files with matches
tool = Grep(
    pattern="TODO",
    output_mode="files_with_matches"  # default
)
result = tool.execute()

# Show content with line numbers
tool = Grep(
    pattern="def .*calculate",
    output_mode="content",
    n=True,              # show line numbers
    A=2,                 # 2 lines after
    B=2,                 # 2 lines before
    i=True,              # case insensitive
    glob="*.py",         # filter files
    path="/src",         # search directory
    head_limit=10        # limit results
)
result = tool.execute()

# Count matches
tool = Grep(
    pattern="import",
    output_mode="count",
    type="py"  # file type filter
)
result = tool.execute()
```

**Features:**
- Requires ripgrep installed
- Three modes: content, files_with_matches, count
- Context lines (-A, -B, -C)
- File filtering (glob, type)
- Multiline support
- 30s timeout, 30KB output limit

## BaseTool - Create Custom Tools

```python
from indusagi.tools.base import BaseTool
from pydantic import Field
from typing import ClassVar

class MyTool(BaseTool):
    """My custom tool."""

    name: ClassVar[str] = "my_tool"
    description: ClassVar[str] = "Does something useful"

    param1: str = Field(..., description="First parameter")
    param2: int = Field(10, description="Second parameter")

    def execute(self) -> str:
        # Access shared context
        ctx = self.context
        ctx.set("last_tool", "my_tool")

        return f"Executed with {self.param1}, {self.param2}"

# Use the tool
tool = MyTool(param1="test", param2=42)
result = tool.execute()

# Get OpenAI schema
schema = MyTool.get_schema()
```

## ToolContext - Shared State

```python
from indusagi.tools import get_tool_context

# Get global context
ctx = get_tool_context()

# Store/retrieve data
ctx.set("api_key", "secret")
api_key = ctx.get("api_key")
default = ctx.get("missing_key", "default_value")

# Track file operations
ctx.mark_file_read("/path/to/file.py")
was_read = ctx.was_file_read("/path/to/file.py")  # True

# Access from any tool
class MyTool(BaseTool):
    def execute(self):
        ctx = self.context  # Same instance
        return ctx.get("api_key")
```

## OpenAI Function Calling Integration

```python
# Get schema for all tools
tools = [Bash, Read, Edit, Write, Glob, Grep]
schemas = [tool.get_schema() for tool in tools]

# Use with OpenAI
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Read file.py"}],
    functions=schemas,
    function_call="auto"
)

# Execute called function
if response.choices[0].message.get("function_call"):
    func_call = response.choices[0].message.function_call
    func_name = func_call.name
    args = json.loads(func_call.arguments)

    # Map to tool class
    tool_map = {
        "bash": Bash,
        "read": Read,
        "edit": Edit,
        "write": Write,
        "glob": Glob,
        "grep": Grep
    }

    tool_class = tool_map[func_name]
    tool = tool_class(**args)
    result = tool.execute()
```

## Common Patterns

### Safe File Editing Workflow

```python
# 1. Read file
read = Read(file_path="/path/to/file.py")
content = read.execute()

# 2. Edit file
edit = Edit(
    file_path="/path/to/file.py",
    old_string="old_code",
    new_string="new_code"
)
result = edit.execute()

# 3. Read again to verify
verify = read.execute()
```

### Find and Edit Pattern

```python
# 1. Find files
glob = Glob(pattern="**/*.py", path="/src")
files = glob.execute()

# 2. Search for pattern
grep = Grep(pattern="TODO", output_mode="files_with_matches")
todo_files = grep.execute()

# 3. Edit each file
for file_path in todo_files.split('\n'):
    if file_path and file_path.strip():
        read = Read(file_path=file_path.strip())
        read.execute()

        edit = Edit(
            file_path=file_path.strip(),
            old_string="TODO",
            new_string="DONE"
        )
        edit.execute()
```

### Code Analysis Workflow

```python
# 1. Find all Python files
glob = Glob(pattern="**/*.py", path="/project")
files = glob.execute()

# 2. Search for specific patterns
grep = Grep(
    pattern="class.*Agent",
    output_mode="content",
    n=True,
    glob="*.py"
)
classes = grep.execute()

# 3. Run analysis script
bash = Bash(
    command="pylint /project --reports=y",
    timeout=60000
)
lint_results = bash.execute()
```

## Error Handling

```python
from pydantic import ValidationError

# Tools validate input automatically
try:
    tool = Bash(command="ls", timeout=999999999)
except ValidationError as e:
    print(f"Invalid parameters: {e}")

# Check execution results
read = Read(file_path="/nonexistent/file.py")
result = read.execute()
if "Error:" in result:
    print(f"Read failed: {result}")
```

## Testing Tools

```python
import tempfile
import os

def test_my_tool():
    # Use temp files for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")

        # Create file
        write = Write(
            file_path=test_file,
            content="print('test')"
        )
        write.execute()

        # Read and verify
        read = Read(file_path=test_file)
        content = read.execute()
        assert "print('test')" in content

        # Files auto-cleaned up when tmpdir context exits
```

## Tips and Best Practices

1. **Always use absolute paths** for file operations
2. **Read before Edit/Write** on existing files
3. **Use Glob for finding**, Grep for searching content
4. **Check tool results** for "Error:" messages
5. **Use timeout** appropriately for long-running Bash commands
6. **Test with temp files** to avoid affecting real code
7. **Access context** via `self.context` in custom tools
8. **Generate schemas** with `Tool.get_schema()` for OpenAI

## File Locations

- **Base**: `src/indusagi/tools/base.py`
- **Tools**: `src/indusagi/tools/dev/*.py`
- **Tests**: `test_phase3_tools.py`
- **Demo**: `demo_phase3_tools.py`
- **Docs**: This file

## Next: Phase 4

Phase 4 will add:
- Tool Registry for dynamic discovery
- Additional tools (Git, LS, MultiEdit, TodoWrite)
- Tool versioning and validation
- Enhanced tool management
