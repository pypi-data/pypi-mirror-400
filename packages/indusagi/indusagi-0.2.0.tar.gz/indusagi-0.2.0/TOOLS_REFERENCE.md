# Tools Reference - Indus Agents Framework

This document provides a comprehensive reference for all available tools in the agency framework.

## Available Tools

### 1. **Bash** - Execute Shell Commands
**Tool Name:** `bash`

**Description:** Execute bash/shell commands in the current working directory.

**Parameters:**
- `command` (required): The shell command to execute
- `command_description` (optional): Description of what the command does
- `timeout` (optional): Timeout in milliseconds (default: 120000)
- `run_in_background` (optional): Run command in background

**Use Cases:**
- Running tests: `pytest tests/`
- Installing packages: `npm install`, `pip install requests`
- Git operations: `git status`, `git add .`, `git commit -m "message"`
- Building projects: `npm run build`, `python setup.py install`
- File system operations: `mkdir folder`, `ls`, `pwd`

**Examples:**
```python
# Run tests
{"command": "pytest tests/test_api.py", "command_description": "Run API tests"}

# Install dependencies
{"command": "npm install express", "command_description": "Install Express.js"}

# Check git status
{"command": "git status", "command_description": "Check repository status"}
```

**Important Notes:**
- Do NOT use for reading files (use Read tool instead)
- Do NOT use for editing files (use Edit tool instead)
- Do NOT use for searching (use Grep/Glob instead)

---

### 2. **Read** - Read File Contents
**Tool Name:** `read`

**Description:** Read file contents with line numbers.

**Parameters:**
- `file_path` (required): Path to the file (absolute or relative)
- `offset` (optional): Line number to start reading from (1-indexed)
- `limit` (optional): Maximum number of lines to read

**Use Cases:**
- View file contents before editing
- Inspect configuration files
- Read code to understand implementation
- View logs and documentation

**Examples:**
```python
# Read entire file
{"file_path": "src/app.py"}

# Read first 50 lines
{"file_path": "README.md", "limit": 50}

# Read from line 100 to 150
{"file_path": "logs/app.log", "offset": 100, "limit": 50}

# Read from project folder
{"file_path": "todo_app/index.html"}
```

**Important Notes:**
- Automatically marks file as read (required for Edit/Write precondition)
- Supports text files, images, PDFs, and Jupyter notebooks
- Returns content with line numbers for easy reference

---

### 3. **Edit** - Modify Existing Files
**Tool Name:** `edit`

**Description:** Replace text in a file using exact string matching.

**Parameters:**
- `file_path` (required): Path to the file to modify
- `old_string` (required): Exact text to replace (must match exactly including whitespace)
- `new_string` (required): New text to replace with
- `replace_all` (optional): Replace all occurrences (default: false)

**Use Cases:**
- Update configuration values
- Fix bugs in code
- Modify function implementations
- Update documentation

**Examples:**
```python
# Change a variable value
{
    "file_path": "config.py",
    "old_string": "DEBUG = False",
    "new_string": "DEBUG = True"
}

# Update a function
{
    "file_path": "src/utils.py",
    "old_string": "def calculate(x):\n    return x * 2",
    "new_string": "def calculate(x):\n    return x * 3"
}

# Replace all occurrences
{
    "file_path": "app.js",
    "old_string": "console.log",
    "new_string": "logger.debug",
    "replace_all": true
}
```

**Important Notes:**
- MUST Read the file first (safety precondition)
- `old_string` must match EXACTLY (including indentation, line breaks)
- If `old_string` appears multiple times, use `replace_all: true` or provide more context
- Preserves file encoding and formatting

---

### 4. **Write** - Create New Files
**Tool Name:** `write`

**Description:** Create new files or overwrite existing ones.

**Parameters:**
- `file_path` (required): Path to the file (absolute or relative)
- `content` (required): Content to write to the file

**Use Cases:**
- Create new source files
- Create HTML/CSS/JS files
- Generate configuration files
- Create documentation

**Examples:**
```python
# Create HTML file in project folder
{
    "file_path": "todo_app/index.html",
    "content": "<!DOCTYPE html>\\n<html>\\n<head>...</head>\\n</html>"
}

# Create Python file
{
    "file_path": "src/models/user.py",
    "content": "class User:\\n    def __init__(self, name):\\n        self.name = name"
}

# Create config file
{
    "file_path": "config.json",
    "content": "{\\n  \\"debug\\": true,\\n  \\"port\\": 3000\\n}"
}
```

**Important Notes:**
- Automatically creates parent directories if they don't exist
- For existing files, MUST Read first (safety precondition)
- Prefer Edit for modifying existing files
- Overwrites existing files completely

---

### 5. **Glob** - Find Files by Pattern
**Tool Name:** `glob`

**Description:** Find files matching a glob pattern.

**Parameters:**
- `pattern` (required): Glob pattern to match
- `path` (optional): Directory to search in (default: current directory)

**Pattern Syntax:**
- `*.py` - All Python files in current directory
- `**/*.js` - All JavaScript files recursively
- `src/**/*.test.js` - All test files in src/ recursively
- `*.{html,css}` - All HTML and CSS files
- `[!.]*.py` - All Python files not starting with dot

**Use Cases:**
- Find all files of a certain type
- Locate test files
- Find configuration files
- Search for specific file patterns

**Examples:**
```python
# Find all Python files recursively
{"pattern": "**/*.py"}

# Find all HTML files in a specific folder
{"pattern": "*.html", "path": "todo_app"}

# Find all JavaScript test files
{"pattern": "**/*.test.js"}

# Find all config files
{"pattern": "**/{config,settings}.{json,yaml,yml}"}
```

**Important Notes:**
- Returns absolute file paths
- Sorted by modification time (newest first)
- Respects .gitignore patterns
- Fast pattern matching

---

### 6. **Grep** - Search File Contents
**Tool Name:** `grep`

**Description:** Search for patterns in files using ripgrep.

**Parameters:**
- `pattern` (required): Regex pattern to search for
- `path` (optional): Directory or file to search in
- `output_mode` (optional): "files_with_matches" (default), "content", or "count"
- `glob` (optional): Filter files by glob pattern
- `type` (optional): File type filter (js, py, rust, go, etc.)
- `case_insensitive` (optional): Case-insensitive search
- `multiline` (optional): Enable multiline pattern matching

**Output Modes:**
- `files_with_matches` - List files containing the pattern
- `content` - Show matching lines with context
- `count` - Count matches per file

**Use Cases:**
- Find function/class definitions
- Search for TODO comments
- Find API endpoints
- Search for error messages
- Locate configuration values

**Examples:**
```python
# Find all TODO comments
{
    "pattern": "TODO:",
    "output_mode": "content"
}

# Find function definitions in Python files
{
    "pattern": "def \\w+\\(",
    "type": "py",
    "output_mode": "content"
}

# Find all files importing React
{
    "pattern": "import.*React",
    "glob": "**/*.{js,jsx,tsx}"
}

# Case-insensitive search for error
{
    "pattern": "error",
    "case_insensitive": true,
    "output_mode": "content"
}

# Find API routes
{
    "pattern": "app\\.(get|post|put|delete)",
    "glob": "**/*.js"
}
```

**Important Notes:**
- Uses ripgrep for fast searching
- Supports full regex syntax
- Respects .gitignore by default
- Can search across multiple files simultaneously

---

### 7. **Handoff to Agent** - Transfer Tasks
**Tool Name:** `handoff_to_agent`

**Description:** Hand off the current task to another agent in the agency.

**Parameters:**
- `agent_name` (required): Name of target agent ("Planner" or "Coder")
- `message` (required): Task description for the target agent
- `context` (optional): Additional context or information

**Use Cases:**
- Coder needs planning help → handoff to Planner
- Planner finished planning → handoff to Coder
- Need different expertise or perspective
- Task requires coordination

**Examples:**
```python
# Coder asks Planner for help
{
    "agent_name": "Planner",
    "message": "I need help planning how to implement user authentication. What's the best approach?",
    "context": "Current tech stack: Flask, SQLite"
}

# Planner sends implementation task to Coder
{
    "agent_name": "Coder",
    "message": "Please implement the login endpoint according to this plan: 1. Create /api/login route 2. Validate credentials 3. Return JWT token",
    "context": "Use bcrypt for password hashing"
}
```

**Important Notes:**
- Can only handoff to agents in allowed communication flows
- Available handoffs: Coder ↔ Planner
- Preserves conversation context
- Limited by max_handoffs setting (default: 10)

---

## Tool Execution Flow

```
User Request
    ↓
Entry Agent (Coder)
    ↓
Agent decides which tool to use
    ↓
Tool Registry executes the tool
    ↓
Tool returns result
    ↓
Agent uses result to continue or finish
    ↓
Final Response to User
```

## Tool Safety Features

1. **Read-before-Edit/Write**: Cannot edit or overwrite existing files without reading them first
2. **File Tracking**: ToolContext tracks which files have been read
3. **Automatic Path Resolution**: Converts relative paths to absolute paths
4. **Directory Creation**: Write tool automatically creates parent directories
5. **Error Handling**: All tools return descriptive error messages
6. **Validation**: Pydantic validates all tool parameters

## Best Practices

### For File Operations:
1. Always **Read** before **Edit** or **Write** (for existing files)
2. Use **Edit** for modifying existing files, **Write** for new files
3. Create files in organized folders (e.g., `project_name/file.html`)
4. Use descriptive folder names

### For Searching:
1. Use **Glob** to find files by name/pattern
2. Use **Grep** to search file contents
3. Combine them: Glob to find files, then Read specific ones

### For Commands:
1. Use **Bash** for system operations (git, npm, testing)
2. Provide clear `command_description` for better logging
3. Check command output for errors

### For Coordination:
1. Use **handoff_to_agent** when you need different expertise
2. Provide clear context in handoff messages
3. Let Planner plan, let Coder implement

## Tool Registry

All tools are registered in the global `registry`:

```python
from indusagi.tools import registry, Bash, Read, Edit, Write, Glob, Grep

# Register tools
registry.register(Bash)
registry.register(Read)
# ... etc

# Get all tool schemas
schemas = registry.schemas

# Execute a tool
result = registry.execute("read", file_path="config.py")
```

## Adding Custom Tools

To add your own tools, inherit from `BaseTool`:

```python
from indusagi.tools.base import BaseTool
from typing import ClassVar
from pydantic import Field

class MyCustomTool(BaseTool):
    name: ClassVar[str] = "my_tool"
    description: ClassVar[str] = "Does something useful"

    param1: str = Field(..., description="First parameter")
    param2: int = Field(10, description="Second parameter")

    def execute(self) -> str:
        # Your implementation
        return f"Result: {self.param1}, {self.param2}"

# Register it
from indusagi.tools import registry
registry.register(MyCustomTool)
```

## Summary

You have **7 powerful tools** available:

| Tool | Purpose | Key Use Case |
|------|---------|-------------|
| **Bash** | Execute commands | Testing, building, git operations |
| **Read** | Read files | View code before editing |
| **Edit** | Modify files | Update existing code |
| **Write** | Create files | Create new files/projects |
| **Glob** | Find files | Locate files by pattern |
| **Grep** | Search content | Find code patterns |
| **Handoff** | Delegate tasks | Coordinate between agents |

All tools work together to enable the agents to build complete projects autonomously! 🚀
