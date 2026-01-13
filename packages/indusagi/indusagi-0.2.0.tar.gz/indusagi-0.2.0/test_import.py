"""
Simple test to verify the agency framework is working
"""

print("Testing imports...")

try:
    from indusagi import Agent, AgentConfig, Agency
    print("✅ Import successful!")
    print(f"   - Agent: {Agent}")
    print(f"   - AgentConfig: {AgentConfig}")
    print(f"   - Agency: {Agency}")

    print("\nTesting agent creation...")
    agent = Agent("TestAgent", "Testing")
    print(f"✅ Agent created: {agent.name}")

    print("\nTesting agency creation...")
    agency = Agency(
        entry_agent=agent,
        agents=[agent],
        communication_flows=[],
        name="TestAgency"
    )
    print(f"✅ Agency created: {agency.name}")

    print("\n" + "="*50)
    print("🎉 All tests passed! The framework is working!")
    print("="*50)

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nDebugging info:")
    import sys
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print("\nPython path:")
    for p in sys.path:
        print(f"  - {p}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
