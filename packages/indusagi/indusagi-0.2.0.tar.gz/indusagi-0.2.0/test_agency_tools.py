"""
Test script to verify that the agency uses tools correctly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from example_agency import create_development_agency

def main():
    print("="*70)
    print(" Testing Agency with Tools")
    print("="*70)
    print()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not set in environment")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        return

    # Create the agency
    print("Creating development agency...")
    agency = create_development_agency()
    print(f"[SUCCESS] Agency created: {agency.name}")
    print(f"[SUCCESS] Tools registered: {len(agency.tools)}")
    print(f"   Tool names: {[t['function']['name'] for t in agency.tools]}")
    print()

    # Test with a simple task
    print("Testing with a simple task: Create a hello.txt file")
    print("-"*70)

    try:
        result = agency.process(
            "Create a file named hello.txt with the content 'Hello, World from AI Agent!'",
            use_tools=True,
            tools=agency.tools,
            tool_executor=agency.tool_executor
        )

        print(f"\n[SUCCESS] Task completed!")
        print(f"Response: {result.response}")
        print(f"Time taken: {result.total_time:.2f}s")

        # Check if file was created
        if os.path.exists("hello.txt"):
            print("\n[SUCCESS] File 'hello.txt' was created successfully!")
            with open("hello.txt", "r") as f:
                content = f.read()
            print(f"   Content: {content}")
        else:
            print("\n[WARNING] File 'hello.txt' was not created")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
