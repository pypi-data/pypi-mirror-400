"""
Test Script for Agency Swarm Implementation

Tests all 4 phases of the Agency Swarm implementation:
- Phase 1: Agent Generation System
- Phase 2: Agency Orchestration
- Phase 3: Development Tools
- Phase 4: Hook System
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from indusagi import Agent, AgentConfig, Agency
from indusagi.tools import Bash, Read, Edit, Write, Glob, Grep
from indusagi.tools import get_tool_context, set_current_agency
from indusagi.templates import scaffold_agent
from indusagi.hooks import SystemReminderHook, RunContext

# ============================================================================
# Test Utilities
# ============================================================================

class TestRunner:
    """Simple test runner for displaying results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name: str, func):
        """Run a test function and record results."""
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print('='*70)
        try:
            func()
            print("[PASSED]")
            self.passed += 1
            self.tests.append((name, True, None))
        except AssertionError as e:
            print(f"[FAILED]: {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
        except Exception as e:
            print(f"[ERROR]: {e}")
            self.failed += 1
            self.tests.append((name, False, f"Error: {e}"))

    def summary(self):
        """Print test summary."""
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print('='*70)
        print(f"Total: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print()

        if self.failed > 0:
            print("Failed tests:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  - {name}: {error}")

        return self.failed == 0


runner = TestRunner()


# ============================================================================
# Phase 1: Agent Generation Tests
# ============================================================================

def test_phase1_template_rendering():
    """Test template rendering with placeholders."""
    from indusagi.templates.renderer import render_instructions

    # Create a test template
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Current directory: {cwd}\n")
        f.write("Platform: {platform}\n")
        f.write("Model: {model}\n")
        template_path = f.name

    try:
        # Render template
        result = render_instructions(template_path, model="gpt-4o")

        # Verify placeholders were replaced
        assert "{cwd}" not in result, "CWD placeholder not replaced"
        assert "{platform}" not in result, "Platform placeholder not replaced"
        assert "{model}" not in result, "Model placeholder not replaced"
        assert "gpt-4o" in result, "Model value not inserted"

        print(f"Template rendered successfully")
        print(f"Output length: {len(result)} characters")
    finally:
        os.unlink(template_path)


def test_phase1_agent_scaffolding():
    """Test agent scaffolding with templates."""
    from indusagi.templates.scaffolder import to_snake_case, to_class_name

    # Test string conversions
    assert to_snake_case("QATester") == "qa_tester", "Snake case conversion failed"
    assert to_class_name("qa_tester") == "QaTester", "Class name conversion failed"
    assert to_snake_case("CodeHelper") == "code_helper", "Snake case conversion failed"
    assert to_class_name("code_helper") == "CodeHelper", "Class name conversion failed"

    # Test scaffolding (we won't actually create files in the test)
    print("String conversions working correctly")
    print(f"  QATester -> qa_tester -> QaTester")
    print(f"  CodeHelper -> code_helper -> CodeHelper")


# ============================================================================
# Phase 2: Agency Orchestration Tests
# ============================================================================

def test_phase2_agency_creation():
    """Test Agency creation and configuration."""
    # Set dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key-for-unit-testing"

    # Create simple agents
    agent1 = Agent("Agent1", "Test agent 1")
    agent2 = Agent("Agent2", "Test agent 2")

    # Create agency
    agency = Agency(
        entry_agent=agent1,
        agents=[agent1, agent2],
        communication_flows=[
            (agent1, agent2),
        ],
        name="TestAgency"
    )

    assert agency.name == "TestAgency", "Agency name not set"
    assert len(agency.agents) == 2, "Wrong number of agents"
    assert agency.entry_agent.name == "Agent1", "Entry agent not set correctly"

    print(f"Agency created: {agency.name}")
    print(f"Agents: {[a.name for a in agency.agents]}")
    print(f"Entry point: {agency.entry_agent.name}")


def test_phase2_communication_flows():
    """Test communication flow validation."""
    # Set dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key-for-unit-testing"

    agent1 = Agent("Agent1", "Test agent 1")
    agent2 = Agent("Agent2", "Test agent 2")
    agent3 = Agent("Agent3", "Test agent 3")

    agency = Agency(
        entry_agent=agent1,
        agents=[agent1, agent2, agent3],
        communication_flows=[
            (agent1, agent2),
            (agent2, agent3),
        ],
        name="FlowTest"
    )

    # Verify flows
    assert "Agent2" in agency._flows.get("Agent1", []), "Flow 1->2 not registered"
    assert "Agent3" in agency._flows.get("Agent2", []), "Flow 2->3 not registered"
    assert "Agent1" not in agency._flows.get("Agent3", []), "Invalid flow exists"

    print(f"Communication flows validated")
    print(f"Agent1 can handoff to: {agency._flows.get('Agent1', [])}")
    print(f"Agent2 can handoff to: {agency._flows.get('Agent2', [])}")


# ============================================================================
# Phase 3: Development Tools Tests
# ============================================================================

def test_phase3_read_tool():
    """Test Read tool with file operations."""
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\n")
        test_file = f.name

    try:
        # Test read
        read_tool = Read(file_path=test_file)
        result = read_tool.execute()

        assert "Line 1" in result, "Content not read correctly"
        assert "Line 2" in result, "Content not read correctly"

        # Verify file was marked as read
        assert get_tool_context().was_file_read(os.path.abspath(test_file)), \
            "File not marked as read in context"

        print(f"Read tool working correctly")
        print(f"File tracked in context: {os.path.abspath(test_file)}")
    finally:
        os.unlink(test_file)


def test_phase3_edit_tool():
    """Test Edit tool with safety preconditions."""
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World\nThis is a test\n")
        test_file = f.name

    try:
        # First, try to edit without reading (should fail)
        edit_tool = Edit(
            file_path=test_file,
            old_string="Hello World",
            new_string="Hello Universe"
        )
        result = edit_tool.execute()
        assert "must Read the file before editing" in result, \
            "Edit should fail without prior Read"

        print("Safety precondition enforced: Read required before Edit")

        # Now read the file first
        read_tool = Read(file_path=test_file)
        read_tool.execute()

        # Now edit should work
        result = edit_tool.execute()
        assert "Error" not in result, f"Edit failed: {result}"

        # Verify the edit
        with open(test_file, 'r') as f:
            content = f.read()
            assert "Hello Universe" in content, "Edit not applied"

        print("Edit tool working correctly after Read")
    finally:
        os.unlink(test_file)


def test_phase3_glob_tool():
    """Test Glob tool for file pattern matching."""
    # Create test directory with files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        Path(tmpdir, "test1.py").write_text("print('test1')")
        Path(tmpdir, "test2.py").write_text("print('test2')")
        Path(tmpdir, "readme.md").write_text("# Readme")

        # Test glob
        glob_tool = Glob(pattern="*.py", path=tmpdir)
        result = glob_tool.execute()

        assert "test1.py" in result, "test1.py not found"
        assert "test2.py" in result, "test2.py not found"
        assert "readme.md" not in result, "Wrong file matched"

        print(f"Glob tool found Python files correctly")


def test_phase3_grep_tool():
    """Test Grep tool for content search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files with content
        test_file = Path(tmpdir, "test.py")
        test_file.write_text("def hello():\n    print('Hello World')\n\ndef goodbye():\n    print('Goodbye')\n")

        # Test grep
        grep_tool = Grep(
            pattern="def.*:",
            path=tmpdir,
            output_mode="content"
        )
        result = grep_tool.execute()

        assert "def hello" in result, "hello function not found"
        assert "def goodbye" in result, "goodbye function not found"

        print(f"Grep tool found pattern matches correctly")


# ============================================================================
# Phase 4: Hook System Tests
# ============================================================================

def test_phase4_run_context():
    """Test RunContext for hook system."""
    context = RunContext(agent_name="TestAgent")

    assert context.agent_name == "TestAgent", "Agent name not set"
    assert context.tool_calls == 0, "Tool calls should start at 0"
    assert len(context.messages) == 0, "Messages should start empty"

    # Test shared state
    context.shared_state["test_key"] = "test_value"
    assert context.shared_state["test_key"] == "test_value", "Shared state not working"

    print(f"RunContext working correctly")
    print(f"  Agent: {context.agent_name}")
    print(f"  Tool calls: {context.tool_calls}")


def test_phase4_system_reminder_hook():
    """Test SystemReminderHook functionality."""
    hook = SystemReminderHook(tool_call_interval=3)

    context = RunContext(agent_name="TestAgent")

    # Simulate tool calls
    for i in range(5):
        context.tool_calls = i
        # In real usage, this would be called during tool execution

    assert hook.tool_call_interval == 3, "Interval not set correctly"

    print(f"SystemReminderHook configured correctly")
    print(f"  Reminder interval: {hook.tool_call_interval} tool calls")


# ============================================================================
# Integration Test
# ============================================================================

def test_integration_full_agency():
    """Test full agency integration with all components."""
    # Set dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key-for-unit-testing"

    # Create agents
    planner = Agent("Planner", "Plans tasks")
    coder = Agent("Coder", "Implements code")

    # Create agency
    agency = Agency(
        entry_agent=coder,
        agents=[planner, coder],
        communication_flows=[
            (coder, planner),
            (planner, coder),
        ],
        name="IntegrationTest"
    )

    # Set as current agency
    set_current_agency(agency)

    assert agency.name == "IntegrationTest", "Agency not created"
    assert len(agency.agents) == 2, "Wrong number of agents"

    # Verify visualization doesn't crash
    try:
        agency.visualize()
        print("Agency visualization works")
    except Exception as e:
        raise AssertionError(f"Visualization failed: {e}")

    print(f"Full integration test passed")
    print(f"  Agency: {agency.name}")
    print(f"  Agents: {[a.name for a in agency.agents]}")


# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("AGENCY SWARM IMPLEMENTATION TEST SUITE")
    print("="*70)

    # Phase 1 Tests
    runner.test("Phase 1: Template Rendering", test_phase1_template_rendering)
    runner.test("Phase 1: Agent Scaffolding", test_phase1_agent_scaffolding)

    # Phase 2 Tests
    runner.test("Phase 2: Agency Creation", test_phase2_agency_creation)
    runner.test("Phase 2: Communication Flows", test_phase2_communication_flows)

    # Phase 3 Tests
    runner.test("Phase 3: Read Tool", test_phase3_read_tool)
    runner.test("Phase 3: Edit Tool Safety", test_phase3_edit_tool)
    runner.test("Phase 3: Glob Tool", test_phase3_glob_tool)
    runner.test("Phase 3: Grep Tool", test_phase3_grep_tool)

    # Phase 4 Tests
    runner.test("Phase 4: RunContext", test_phase4_run_context)
    runner.test("Phase 4: SystemReminderHook", test_phase4_system_reminder_hook)

    # Integration Tests
    runner.test("Integration: Full Agency", test_integration_full_agency)

    # Print summary
    success = runner.summary()

    if success:
        print("\n[SUCCESS] All tests passed! Agency Swarm implementation is working correctly.")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Please review the failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
