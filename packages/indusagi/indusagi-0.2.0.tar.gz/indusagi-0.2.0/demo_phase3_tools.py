"""
Demo script showing Phase 3 Development Tools in action.
"""
import sys
import os
import tempfile
import json

sys.path.insert(0, 'src')

from indusagi.tools import (
    BaseTool, ToolContext, get_tool_context,
    Bash, Read, Edit, Write, Glob, Grep
)

def demo_header(title):
    """Print a demo section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def demo_tool_schemas():
    """Demonstrate tool schema generation for OpenAI function calling."""
    demo_header("Tool Schema Generation (OpenAI Function Calling)")

    print("\nRead Tool Schema:")
    read_schema = Read.get_schema()
    print(json.dumps(read_schema, indent=2))

    print("\nEdit Tool Schema:")
    edit_schema = Edit.get_schema()
    print(json.dumps(edit_schema, indent=2))

def demo_file_operations():
    """Demonstrate file operations workflow."""
    demo_header("File Operations Workflow")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Create a Python file
        print("\n1. Creating a new Python file with Write tool...")
        py_file = os.path.join(tmpdir, "example.py")
        write_tool = Write(
            file_path=py_file,
            content='''def calculate(x, y):
    """Calculate sum of two numbers."""
    return x + y

def main():
    result = calculate(10, 20)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
'''
        )
        result = write_tool.execute()
        print(f"   {result}")

        # 2. Read the file
        print("\n2. Reading the file with Read tool...")
        read_tool = Read(file_path=py_file)
        result = read_tool.execute()
        print(f"   File contents:\n{result}")

        # 3. Edit the file
        print("\n3. Editing the file with Edit tool...")
        edit_tool = Edit(
            file_path=py_file,
            old_string='    return x + y',
            new_string='    result = x + y\n    print(f"Computing {x} + {y} = {result}")\n    return result'
        )
        result = edit_tool.execute()
        print(f"   {result}")

        # 4. Read again to verify
        print("\n4. Reading edited file...")
        result = read_tool.execute()
        print(f"   File contents:\n{result}")

def demo_glob_search():
    """Demonstrate glob file pattern matching."""
    demo_header("Glob Pattern Matching")

    print("\n1. Finding all Python files in src/indusagi/tools/...")
    glob_tool = Glob(
        pattern="**/*.py",
        path="src/indusagi/tools"
    )
    result = glob_tool.execute()
    print(result)

    print("\n2. Finding only tool files (not __init__.py)...")
    glob_tool2 = Glob(
        pattern="**/[!_]*.py",
        path="src/indusagi/tools/dev"
    )
    result2 = glob_tool2.execute()
    print(result2)

def demo_context_tracking():
    """Demonstrate shared context and file tracking."""
    demo_header("Shared Context & File Tracking")

    ctx = get_tool_context()

    print("\n1. Context can store shared data:")
    ctx.set("api_key", "secret-key-123")
    ctx.set("current_task", "demo")
    print(f"   api_key: {ctx.get('api_key')}")
    print(f"   current_task: {ctx.get('current_task')}")

    print("\n2. Context tracks which files have been read:")
    print(f"   Files read so far: {len(ctx._read_files)}")
    for file in list(ctx._read_files)[:3]:
        print(f"   - {file}")

    print("\n3. This enables safety checks:")
    print("   - Edit tool requires file to be Read first")
    print("   - Write tool requires existing files to be Read first")
    print("   - Prevents accidental overwrites!")

def demo_base_tool_features():
    """Demonstrate BaseTool features."""
    demo_header("BaseTool Features")

    print("\n1. All tools inherit from BaseTool")
    print(f"   Read is BaseTool subclass: {issubclass(Read, BaseTool)}")
    print(f"   Edit is BaseTool subclass: {issubclass(Edit, BaseTool)}")

    print("\n2. Tools use Pydantic for validation")
    try:
        # This will fail validation
        bad_bash = Bash(command="ls", timeout=999999999)
        bad_bash.execute()
    except Exception as e:
        print(f"   Validation caught invalid timeout: {type(e).__name__}")

    print("\n3. Tools provide both execute() and run() methods")
    print("   - execute(): Direct execution")
    print("   - run(): Agency Swarm compatibility")

    print("\n4. Tools have .name and .description class variables")
    print(f"   Read.name: {Read.name}")
    print(f"   Edit.name: {Edit.name}")
    print(f"   Bash.name: {Bash.name}")

def main():
    """Run all demos."""
    print("\n")
    print("#" * 60)
    print("#  Phase 3 Development Tools - Interactive Demo")
    print("#" * 60)

    demo_tool_schemas()
    demo_file_operations()
    demo_glob_search()
    demo_context_tracking()
    demo_base_tool_features()

    print("\n" + "#" * 60)
    print("#  Demo Complete!")
    print("#" * 60)
    print("\nKey Features Demonstrated:")
    print("  - BaseTool abstract base class with Pydantic validation")
    print("  - ToolContext for shared state and file tracking")
    print("  - Read, Write, Edit tools with safety preconditions")
    print("  - Glob for file pattern matching")
    print("  - Grep for content search (ripgrep-based)")
    print("  - Bash for command execution with timeout")
    print("  - OpenAI function calling schema generation")
    print()

if __name__ == "__main__":
    main()
