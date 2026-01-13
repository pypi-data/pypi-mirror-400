"""
Example usage script for Activity Tracker Agent

Run this to see the agent in action with example member IDs.
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agent import run_activity_tracker


def main():
    print("=" * 70)
    print("  ACTIVITY TRACKER AGENT - EXAMPLE RUN")
    print("=" * 70)
    print()
    print("This example demonstrates the Activity Tracker Agent.")
    print()
    print("Choose a mode:")
    print("  1. Single member analysis (example UUID)")
    print("  2. Batch analysis (3 example UUIDs)")
    print("  3. Interactive mode")
    print("  4. Exit")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        # Example single member
        example_uuid = "550e8400-e29b-41d4-a716-446655440000"
        print(f"\nRunning single member analysis for: {example_uuid}\n")
        run_activity_tracker(member_id=example_uuid)

    elif choice == "2":
        # Example batch
        example_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "6ba7b811-9dad-11d1-80b4-00c04fd430c9"
        ]
        print(f"\nRunning batch analysis for {len(example_uuids)} members\n")
        run_activity_tracker(member_ids=example_uuids)

    elif choice == "3":
        print("\nStarting interactive mode...\n")
        run_activity_tracker(interactive=True)

    elif choice == "4":
        print("\nExiting...\n")
        return

    else:
        print("\nInvalid choice. Exiting...\n")


if __name__ == "__main__":
    # Check environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n[ERROR] ANTHROPIC_API_KEY not set!")
        print("Please set it in your .env file:")
        print("  ANTHROPIC_API_KEY=your-api-key")
        print("  ANTHROPIC_MODEL=glm-4.7")
        print("  ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic")
        print("  LLM_PROVIDER=anthropic")
        print()
        sys.exit(1)

    main()
