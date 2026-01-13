"""
Agency Configuration - Easy model switching

Change the MODEL variable to switch between models for all agents.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from example_agency_improved import create_development_agency

# ============================================================================
# CONFIGURATION - Change these settings
# ============================================================================

# Model Selection (choose one):
# - "gpt-5-mini"      ✅ RECOMMENDED: Latest, fast, cost-efficient (Released Aug 2025)
# - "gpt-5"           🚀 Most capable GPT-5 variant
# - "gpt-5-nano"      ⚡ Smallest/fastest GPT-5
# - "gpt-4o-mini"     💼 Previous gen, still good
# - "gpt-4o"          💰 Previous gen, more expensive
# - "o1-mini"         🧠 Reasoning model (slower, for complex logic)

MODEL = "gpt-5-mini"  # ✅ Latest GPT-5 mini model (Aug 2025)

# Reasoning effort (for o1/o3 models):
# - "low", "medium", "high"
REASONING_EFFORT = "medium"

# Maximum handoffs allowed per request:
MAX_HANDOFFS = 15

# ============================================================================
# Model Comparison
# ============================================================================

"""
┌─────────────────┬─────────┬────────┬──────────────┬─────────────┐
│ Model           │ Speed   │ Cost   │ Rate Limits  │ Quality     │
├─────────────────┼─────────┼────────┼──────────────┼─────────────┤
│ gpt-5-mini ⭐   │ ⚡⚡⚡    │ 💰     │ ✅ Very High │ ⭐⭐⭐⭐     │
│ gpt-5           │ ⚡⚡     │ 💰💰   │ ✅ High      │ ⭐⭐⭐⭐⭐   │
│ gpt-5-nano      │ ⚡⚡⚡⚡  │ 💰     │ ✅ Very High │ ⭐⭐⭐       │
│ gpt-4o-mini     │ ⚡⚡⚡    │ 💰     │ ✅ High      │ ⭐⭐⭐       │
│ gpt-4o          │ ⚡⚡     │ 💰💰💰 │ ⚠️  Medium   │ ⭐⭐⭐⭐     │
└─────────────────┴─────────┴────────┴──────────────┴─────────────┘

Recommendations:
- Development/Testing: gpt-5-mini ⭐ (latest, fast, cheap)
- Production: gpt-5 (best quality)
- High volume: gpt-5-nano or gpt-5-mini (best rate limits)
"""

# ============================================================================
# Run Agency with Config
# ============================================================================

def main():
    """Run agency with configured settings."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set in .env file")
        return

    print("=" * 70)
    print(f"  INDUS-AGENTS - Multi-Agent System")
    print(f"  Model: {MODEL}")
    print(f"  Reasoning: {REASONING_EFFORT}")
    print(f"  Max Handoffs: {MAX_HANDOFFS}")
    print("=" * 70)
    print()

    # Create agency with configured settings
    agency = create_development_agency(
        model=MODEL,
        reasoning_effort=REASONING_EFFORT,
        max_handoffs=MAX_HANDOFFS
    )

    print(f"Agency: {agency.name}")
    print(f"Entry Agent: {agency.entry_agent.name}")
    print(f"Agents: {', '.join([a.name for a in agency.agents])}")
    print()

    # Show communication flows
    print("Communication Flows:")
    agency.visualize()
    print()

    # Example prompts
    print("=" * 70)
    print("EXAMPLE PROMPTS:")
    print("=" * 70)
    print()
    print("Simple tasks:")
    print('  "Create a hello world HTML page"')
    print('  "Build a simple calculator"')
    print()
    print("Planning tasks:")
    print('  "Create plan.md for a todo app, then implement it"')
    print('  "Plan and build a weather dashboard"')
    print()
    print("=" * 70)
    print()

    # Run terminal demo
    print("Starting interactive demo...")
    print("Commands: /quit, /agents, /handoffs, /logs, /stats")
    print()

    try:
        agency.terminal_demo(show_reasoning=False)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
