"""
Test improved logging output.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from example_agency import create_development_agency

def main():
    print("="*70)
    print(" Testing Improved Logging")
    print("="*70)
    print()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not set")
        return

    # Create agency
    print("Creating agency...")
    agency = create_development_agency()
    print()

    # Test with a simple multi-step task
    print("Task: Create a simple number guessing game")
    print("="*70)
    print()

    try:
        result = agency.process(
            "Create a simple number guessing game web app where the user tries to guess a random number between 1-100. "
            "Include HTML, CSS, and JavaScript.",
            use_tools=True,
            tools=agency.tools,
            tool_executor=agency.tool_executor
        )

        print()
        print("="*70)
        print(f"Task completed in {result.total_time:.1f}s")
        print("="*70)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
