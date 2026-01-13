"""
Test script for Phase 3 Development Tools implementation.
"""
import sys
import os
import tempfile

sys.path.insert(0, 'src')

from indusagi.tools import (
    BaseTool, ToolContext, get_tool_context,
    Bash, Read, Edit, Write, Glob, Grep
)

def test_base_tool():
    """Test BaseTool and ToolContext."""
    print("Testing BaseTool and ToolContext...")

    # Test context
    ctx = get_tool_context()
    assert isinstance(ctx, ToolContext)

    # Test context operations
    ctx.set("test_key", "test_value")
    assert ctx.get("test_key") == "test_value"

    # Test file tracking
    ctx.mark_file_read("/tmp/test.txt")
    assert ctx.was_file_read("/tmp/test.txt")
    assert not ctx.was_file_read("/tmp/other.txt")

    print("  [OK] BaseTool and ToolContext work correctly")

def test_read_tool():
    """Test Read tool."""
    print("\nTesting Read tool...")

    # Create a temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        temp_file = f.name

    try:
        # Test reading entire file
        tool = Read(file_path=temp_file)
        result = tool.execute()
        assert "Line 1" in result
        assert "Line 5" in result

        # Verify file was marked as read
        ctx = get_tool_context()
        assert ctx.was_file_read(os.path.abspath(temp_file))

        # Test offset and limit
        tool2 = Read(file_path=temp_file, offset=2, limit=2)
        result2 = tool2.execute()
        assert "Line 2" in result2
        assert "Line 3" in result2
        assert "Line 1" not in result2

        print("  [OK] Read tool works correctly")
    finally:
        os.unlink(temp_file)

def test_write_tool():
    """Test Write tool."""
    print("\nTesting Write tool...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test creating new file
        new_file = os.path.join(tmpdir, "new_file.txt")
        tool = Write(file_path=new_file, content="Hello World\nLine 2")
        result = tool.execute()
        assert "created" in result.lower()
        assert os.path.exists(new_file)

        with open(new_file, 'r') as f:
            content = f.read()
        assert content == "Hello World\nLine 2"

        # Test overwriting (should fail without reading first)
        ctx = get_tool_context()
        # Clear the read files to test the precondition
        ctx._read_files.discard(os.path.abspath(new_file))

        tool2 = Write(file_path=new_file, content="New content")
        result2 = tool2.execute()
        assert "Error" in result2
        assert "Read" in result2

        # Mark as read and try again
        ctx.mark_file_read(os.path.abspath(new_file))
        tool3 = Write(file_path=new_file, content="New content")
        result3 = tool3.execute()
        assert "overwritten" in result3.lower()

        print("  [OK] Write tool works correctly")

def test_edit_tool():
    """Test Edit tool."""
    print("\nTesting Edit tool...")

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Hello World\nThis is a test\nHello again")
        temp_file = f.name

    try:
        # First read the file
        read_tool = Read(file_path=temp_file)
        read_tool.execute()

        # Test editing
        edit_tool = Edit(
            file_path=temp_file,
            old_string="This is a test",
            new_string="This was edited"
        )
        result = edit_tool.execute()
        assert "Successfully replaced" in result

        # Verify the edit
        with open(temp_file, 'r') as f:
            content = f.read()
        assert "This was edited" in content
        assert "This is a test" not in content

        # Test replace_all
        read_tool.execute()  # Read again
        edit_tool2 = Edit(
            file_path=temp_file,
            old_string="Hello",
            new_string="Hi",
            replace_all=True
        )
        result2 = edit_tool2.execute()
        assert "2 occurrence" in result2

        print("  [OK] Edit tool works correctly")
    finally:
        os.unlink(temp_file)

def test_glob_tool():
    """Test Glob tool."""
    print("\nTesting Glob tool...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        os.makedirs(os.path.join(tmpdir, "subdir"))
        open(os.path.join(tmpdir, "file1.py"), 'w').close()
        open(os.path.join(tmpdir, "file2.py"), 'w').close()
        open(os.path.join(tmpdir, "file3.txt"), 'w').close()
        open(os.path.join(tmpdir, "subdir", "file4.py"), 'w').close()

        # Test simple pattern
        tool = Glob(pattern="*.py", path=tmpdir)
        result = tool.execute()
        assert "file1.py" in result
        assert "file2.py" in result
        assert "file3.txt" not in result
        assert "file4.py" not in result  # Not in subdir

        # Test recursive pattern
        tool2 = Glob(pattern="**/*.py", path=tmpdir)
        result2 = tool2.execute()
        assert "file1.py" in result2
        assert "file4.py" in result2

        print("  [OK] Glob tool works correctly")

def test_tool_schemas():
    """Test tool schema generation."""
    print("\nTesting tool schema generation...")

    schema = Read.get_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "read"
    assert "file_path" in schema["function"]["parameters"]["properties"]

    schema2 = Edit.get_schema()
    assert schema2["function"]["name"] == "edit"
    assert "old_string" in schema2["function"]["parameters"]["properties"]
    assert "new_string" in schema2["function"]["parameters"]["properties"]

    print("  [OK] Tool schemas generate correctly")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 3 Development Tools - Test Suite")
    print("=" * 60)

    try:
        test_base_tool()
        test_read_tool()
        test_write_tool()
        test_edit_tool()
        test_glob_tool()
        test_tool_schemas()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
