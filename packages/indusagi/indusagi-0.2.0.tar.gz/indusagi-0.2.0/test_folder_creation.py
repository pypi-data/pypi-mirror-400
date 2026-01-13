"""
Test that the agency creates files in organized folders.
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

from example_agency import create_development_agency

def main():
    print("="*70)
    print(" Testing Folder Organization")
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
    print()

    # Test with a calculator app
    print("Task: Create a simple calculator web app")
    print("-"*70)

    try:
        result = agency.process(
            "Create a simple calculator web app with HTML, CSS, and JavaScript. "
            "It should have buttons for numbers 0-9, +, -, *, /, =, and Clear.",
            use_tools=True,
            tools=agency.tools,
            tool_executor=agency.tool_executor
        )

        print(f"\n[SUCCESS] Task completed!")
        print(f"Response: {result.response}")
        print(f"Time taken: {result.total_time:.2f}s")
        print()

        # Check for created folders
        print("Checking for created files and folders...")

        # Look for common folder names
        possible_folders = ['calculator_app', 'calculator', 'calculator_project', 'simple_calculator']
        found_folder = None

        for folder in possible_folders:
            if os.path.exists(folder):
                found_folder = folder
                break

        if found_folder:
            print(f"[SUCCESS] Found project folder: {found_folder}/")

            # List all files in the folder
            for root, dirs, files in os.walk(found_folder):
                level = root.replace(found_folder, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        else:
            # Check current directory
            print("[INFO] No dedicated folder found. Checking current directory...")
            html_files = [f for f in os.listdir('.') if f.endswith('.html')]
            css_files = [f for f in os.listdir('.') if f.endswith('.css')]
            js_files = [f for f in os.listdir('.') if f.endswith('.js')]

            if html_files or css_files or js_files:
                print(f"   HTML files: {html_files}")
                print(f"   CSS files: {css_files}")
                print(f"   JS files: {js_files}")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
