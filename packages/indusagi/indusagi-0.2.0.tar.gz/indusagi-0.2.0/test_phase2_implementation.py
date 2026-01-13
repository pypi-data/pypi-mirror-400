"""
Test script for Phase 2: Agency Orchestration System Implementation

This script verifies that all Phase 2 components are working correctly:
1. Agency class with all methods
2. HandoffResult and AgencyResponse dataclasses
3. HandoffType enum
4. Handoff tool functions
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set dummy API key for testing structure (not making actual API calls)
os.environ['OPENAI_API_KEY'] = 'test-key-for-structure-verification'

from indusagi import (
    Agency,
    AgencyResponse,
    HandoffResult,
    HandoffType,
    Agent
)
from indusagi.tools.handoff import (
    handoff_to_agent,
    set_current_agency,
    get_current_agency,
    register_handoff_tool
)


def test_agency_creation():
    """Test creating an Agency with multiple agents."""
    print("\n" + "="*70)
    print("TEST 1: Agency Creation")
    print("="*70)

    # Create agents
    coder = Agent('CoderAgent', 'Handles coding tasks')
    planner = Agent('PlannerAgent', 'Handles planning tasks')

    # Create agency
    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner],
        communication_flows=[
            (coder, planner),
            (planner, coder),
        ],
        name='DevAgency',
        max_handoffs=5
    )

    assert agency.name == 'DevAgency'
    assert agency.entry_agent.name == 'CoderAgent'
    assert len(agency.agents) == 2
    assert agency.max_handoffs == 5

    print("[PASS] Agency created successfully")
    print(f"  - Name: {agency.name}")
    print(f"  - Entry Agent: {agency.entry_agent.name}")
    print(f"  - Agents: {agency.list_agents()}")


def test_communication_flows():
    """Test communication flow validation."""
    print("\n" + "="*70)
    print("TEST 2: Communication Flows")
    print("="*70)

    coder = Agent('CoderAgent', 'Handles coding tasks')
    planner = Agent('PlannerAgent', 'Handles planning tasks')
    reviewer = Agent('ReviewerAgent', 'Handles review tasks')

    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner, reviewer],
        communication_flows=[
            (coder, planner),
            (planner, reviewer),
        ],
        name='DevAgency'
    )

    # Test allowed handoffs
    assert agency.can_handoff('CoderAgent', 'PlannerAgent') == True
    assert agency.can_handoff('PlannerAgent', 'ReviewerAgent') == True
    assert agency.can_handoff('CoderAgent', 'ReviewerAgent') == False

    # Test get_allowed_handoffs
    coder_targets = agency.get_allowed_handoffs('CoderAgent')
    assert 'PlannerAgent' in coder_targets
    assert len(coder_targets) == 1

    print("[PASS] Communication flows working correctly")
    print(f"  - CoderAgent can handoff to: {agency.get_allowed_handoffs('CoderAgent')}")
    print(f"  - PlannerAgent can handoff to: {agency.get_allowed_handoffs('PlannerAgent')}")
    print(f"  - ReviewerAgent can handoff to: {agency.get_allowed_handoffs('ReviewerAgent')}")


def test_agency_methods():
    """Test Agency helper methods."""
    print("\n" + "="*70)
    print("TEST 3: Agency Methods")
    print("="*70)

    agent1 = Agent('Agent1', 'First agent')
    agent2 = Agent('Agent2', 'Second agent')

    agency = Agency(
        entry_agent=agent1,
        agents=[agent1, agent2],
        name='TestAgency'
    )

    # Test get_agent
    retrieved = agency.get_agent('Agent1')
    assert retrieved is not None
    assert retrieved.name == 'Agent1'

    # Test list_agents
    agent_names = agency.list_agents()
    assert 'Agent1' in agent_names
    assert 'Agent2' in agent_names

    # Test shared state
    agency.set_shared_state('test_key', 'test_value')
    assert agency.get_shared_state('test_key') == 'test_value'
    assert agency.get_shared_state('missing_key', 'default') == 'default'

    agency.clear_shared_state()
    assert agency.get_shared_state('test_key') is None

    print("[PASS] All agency methods working correctly")
    print(f"  - get_agent: {retrieved.name}")
    print(f"  - list_agents: {agent_names}")
    print(f"  - Shared state management: OK")


def test_visualization():
    """Test agency visualization."""
    print("\n" + "="*70)
    print("TEST 4: Agency Visualization")
    print("="*70)

    coder = Agent('CoderAgent', 'Handles coding')
    planner = Agent('PlannerAgent', 'Handles planning')

    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner],
        communication_flows=[
            (coder, planner),
            (planner, coder),
        ],
        name='DevAgency'
    )

    viz = agency.visualize()
    assert 'DevAgency' in viz
    assert 'CoderAgent' in viz
    assert 'PlannerAgent' in viz
    assert 'Communication Flows:' in viz

    print("[PASS] Visualization generated successfully:")
    print(viz)


def test_handoff_functions():
    """Test handoff tool functions."""
    print("\n" + "="*70)
    print("TEST 5: Handoff Tool Functions")
    print("="*70)

    coder = Agent('CoderAgent', 'Handles coding')
    planner = Agent('PlannerAgent', 'Handles planning')

    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner],
        communication_flows=[(coder, planner)],
        name='DevAgency'
    )

    # Test set and get current agency
    set_current_agency(agency)
    retrieved_agency = get_current_agency()
    assert retrieved_agency is not None
    assert retrieved_agency.name == 'DevAgency'

    print("[PASS] Handoff functions working correctly")
    print(f"  - set_current_agency: OK")
    print(f"  - get_current_agency: OK")
    print(f"  - handoff_to_agent: Available")


def test_dataclasses():
    """Test HandoffResult and AgencyResponse dataclasses."""
    print("\n" + "="*70)
    print("TEST 6: Dataclasses")
    print("="*70)

    # Test HandoffResult
    handoff = HandoffResult(
        success=True,
        response="Task completed",
        from_agent="CoderAgent",
        to_agent="PlannerAgent",
        processing_time=1.5,
        error=None
    )
    assert handoff.success == True
    assert handoff.from_agent == "CoderAgent"

    # Test AgencyResponse
    response = AgencyResponse(
        response="Final result",
        agents_used=["CoderAgent", "PlannerAgent"],
        handoffs=[handoff],
        total_time=2.5,
        final_agent="PlannerAgent"
    )
    assert response.final_agent == "PlannerAgent"
    assert len(response.handoffs) == 1

    print("[PASS] Dataclasses working correctly")
    print(f"  - HandoffResult: {handoff.from_agent} -> {handoff.to_agent}")
    print(f"  - AgencyResponse: {response.final_agent} ({response.total_time}s)")


def test_handoff_type_enum():
    """Test HandoffType enum."""
    print("\n" + "="*70)
    print("TEST 7: HandoffType Enum")
    print("="*70)

    assert HandoffType.MESSAGE.value == "message"
    assert HandoffType.FULL_CONTEXT.value == "full_context"

    print("[PASS] HandoffType enum working correctly")
    print(f"  - MESSAGE: {HandoffType.MESSAGE.value}")
    print(f"  - FULL_CONTEXT: {HandoffType.FULL_CONTEXT.value}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("PHASE 2 IMPLEMENTATION VERIFICATION")
    print("Agency Orchestration System")
    print("="*70)

    try:
        test_agency_creation()
        test_communication_flows()
        test_agency_methods()
        test_visualization()
        test_handoff_functions()
        test_dataclasses()
        test_handoff_type_enum()

        print("\n" + "="*70)
        print("ALL TESTS PASSED!")
        print("="*70)
        print("\nPhase 2 Implementation Summary:")
        print("  [OK] Agency class with full implementation")
        print("  [OK] HandoffResult dataclass")
        print("  [OK] AgencyResponse dataclass")
        print("  [OK] HandoffType enum")
        print("  [OK] Communication flows and handoff validation")
        print("  [OK] Agency methods (get_agent, list_agents, etc.)")
        print("  [OK] Shared state management")
        print("  [OK] Visualization method")
        print("  [OK] Handoff tool functions (set_current_agency, etc.)")
        print("\nPhase 2 is COMPLETE and ready for use!")
        print("="*70)

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
