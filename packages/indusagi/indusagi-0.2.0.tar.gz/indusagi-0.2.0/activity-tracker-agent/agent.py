"""
Activity Tracker Agent - Python Implementation
Uses indus-agents framework with Anthropic Provider (GLM-4.7 via Z.AI)

Tracks member activity patterns and calculates engagement scores using Supabase data.
Supports batch processing for 1-20 members with weighted activity scoring.

Based on prompt.md specifications.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import framework
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from indusagi import Agent, AgentConfig
from indusagi.tools import Bash, Read, Edit, Write, Glob, Grep, TodoWrite
from indusagi.tools import registry

# Load environment variables
load_dotenv()


def create_activity_tracker_agent(
    model: str = "glm-4.7",
    max_tokens: int = 16000
) -> Agent:
    """
    Create Activity Tracker Agent using Anthropic provider.

    This agent analyzes member activity patterns and calculates engagement scores
    following the specifications in prompt.md.

    Args:
        model: Model to use (default: glm-4.7)
        max_tokens: Maximum tokens for responses

    Returns:
        Configured Agent instance
    """
    # Read the prompt.md file for system instructions
    prompt_file = Path(__file__).parent / "prompt.md"

    if not prompt_file.exists():
        raise FileNotFoundError(
            f"prompt.md not found at {prompt_file}. "
            "Please ensure prompt.md is in the same directory as agent.py"
        )

    with open(prompt_file, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    # Create agent configuration with Anthropic provider
    config = AgentConfig(
        model=model,
        provider="anthropic",
        temperature=0.7,
        max_tokens=max_tokens,
    )

    # Create the agent
    agent = Agent(
        name="ActivityTrackerAgent",
        role="Member engagement analysis and pastoral care recommendations specialist",
        config=config,
        system_prompt=system_prompt
    )

    # Set context for shared tool state
    agent.context = registry.context

    return agent


def run_activity_tracker(
    member_id: str = None,
    member_ids: list = None,
    interactive: bool = False
):
    """
    Run the Activity Tracker Agent.

    Args:
        member_id: Single member UUID to analyze
        member_ids: List of member UUIDs for batch processing
        interactive: If True, start interactive mode
    """
    # Register tools
    for tool_class in [Bash, Read, Edit, Write, Glob, Grep, TodoWrite]:
        registry.register(tool_class)

    print("=" * 70)
    print("  ACTIVITY TRACKER AGENT - Member Engagement Analysis")
    print("  Provider: Anthropic (GLM-4.7 via Z.AI)")
    print("=" * 70)
    print()

    # Verify environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY not set in environment")
        print("Please set it in your .env file")
        return

    # Create the agent
    print("Creating Activity Tracker Agent...")
    agent = create_activity_tracker_agent()

    print(f"Agent: {agent.name}")
    print(f"Provider: {agent.provider.get_provider_name()}")
    print(f"Model: {agent.config.model}")
    print(f"Max Tokens: {agent.config.max_tokens}")
    print()

    # Determine mode
    if interactive:
        print("=" * 70)
        print("INTERACTIVE MODE")
        print("=" * 70)
        print()
        print("You can now interact with the Activity Tracker Agent.")
        print("Type your request or use these commands:")
        print()
        print("Examples:")
        print('  "Analyze member <UUID>"')
        print('  "Batch analyze members <UUID1>,<UUID2>,<UUID3>"')
        print('  "quit" to exit')
        print()
        print("=" * 70)
        print()

        # Interactive loop
        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nExiting interactive mode...")
                    break

                if not user_input:
                    continue

                print()
                # Process with tools
                response = agent.process_with_tools(
                    user_input=user_input,
                    tools=registry.schemas,
                    tool_executor=registry,
                    max_turns=100
                )

                print(f"\nAgent: {response}\n")
                print("=" * 70)
                print()

            except KeyboardInterrupt:
                print("\n\nInterrupted. Exiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()

    else:
        # Automated mode with member ID(s)
        if member_ids:
            # Batch mode
            member_ids_str = ','.join(member_ids)
            task = f"""Analyze member activity patterns for the following members in batch mode:
Member IDs: {member_ids_str}

Follow the complete workflow from prompt.md:
1. Use TodoWrite to create task list
2. Run data fetcher for all members
3. Analyze activity patterns and calculate engagement scores
4. Generate comprehensive analysis reports for each member
5. Run storage script to save to Supabase
6. Clean up data files

Execute all steps systematically."""

        elif member_id:
            # Single member mode
            task = f"""Analyze member activity patterns for member ID: {member_id}

Follow the complete workflow from prompt.md:
1. Use TodoWrite to create task list
2. Run data fetcher for this member
3. Analyze activity patterns and calculate engagement scores
4. Generate comprehensive analysis report
5. Run storage script to save to Supabase
6. Clean up data files

Execute all steps systematically."""

        else:
            print("[ERROR] No member ID(s) provided. Use --member_id or --member_ids")
            print()
            print("Usage:")
            print("  python agent.py --member_id <UUID>")
            print("  python agent.py --member_ids <UUID1>,<UUID2>,<UUID3>")
            print("  python agent.py --interactive")
            return

        print("=" * 70)
        print("TASK")
        print("=" * 70)
        print(task)
        print()
        print("=" * 70)
        print("PROCESSING")
        print("=" * 70)
        print()

        # Process the task
        try:
            response = agent.process_with_tools(
                user_input=task,
                tools=registry.schemas,
                tool_executor=registry,
                max_turns=100
            )

            print()
            print("=" * 70)
            print("FINAL RESULT")
            print("=" * 70)
            print(response)
            print("=" * 70)
            print()

        except Exception as e:
            print(f"\nError processing task: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point with argument parsing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Activity Tracker Agent - Member Engagement Analysis"
    )
    parser.add_argument(
        '--member_id',
        type=str,
        help='Single member UUID to analyze'
    )
    parser.add_argument(
        '--member_ids',
        type=str,
        help='Comma-separated list of member UUIDs for batch analysis'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='glm-4.7',
        help='Model to use (default: glm-4.7)'
    )

    args = parser.parse_args()

    # Parse member_ids if provided
    member_ids_list = None
    if args.member_ids:
        member_ids_list = [mid.strip() for mid in args.member_ids.split(',')]

    # Run the agent
    run_activity_tracker(
        member_id=args.member_id,
        member_ids=member_ids_list,
        interactive=args.interactive
    )


if __name__ == "__main__":
    main()
