"""
Test TodoWrite tool integration with the agency.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from example_agency import create_development_agency

def main():
    print("="*70)
    print(" Testing TodoWrite Tool Integration")
    print("="*70)
    print()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not set in environment")
        return

    # Create the agency
    print("Creating development agency...")
    agency = create_development_agency()
    print(f"[SUCCESS] Agency created: {agency.name}")
    print(f"[SUCCESS] Tools registered: {len(agency.tools)}")

    # Check if todo_write is in the tools
    tool_names = [t['function']['name'] for t in agency.tools]
    print(f"   Tool names: {tool_names}")

    if 'todo_write' in tool_names:
        print("[SUCCESS] todo_write tool is registered!")
    else:
        print("[ERROR] todo_write tool is NOT registered!")
        return

    print()

    # Test with a task that should trigger TodoWrite
    print("Testing with a multi-step task: Create a portfolio website")
    print("-"*70)

    try:
        result = agency.process(
            "Create a simple portfolio website with Home, About, and Contact pages. "
            "Include navigation, responsive design, and a contact form.",
            use_tools=True,
            tools=agency.tools,
            tool_executor=agency.tool_executor
        )

        print(f"\n[SUCCESS] Task completed!")
        print(f"Response: {result.response[:500]}...")  # Show first 500 chars
        print(f"Time taken: {result.total_time:.2f}s")

        # Check if files were created
        print("\nChecking for created files...")
        if os.path.exists("portfolio_website") or os.path.exists("portfolio"):
            folder = "portfolio_website" if os.path.exists("portfolio_website") else "portfolio"
            print(f"[SUCCESS] Found project folder: {folder}/")

            # List files
            for root, dirs, files in os.walk(folder):
                level = root.replace(folder, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        else:
            print("[INFO] No dedicated folder found")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
