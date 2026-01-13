"""
Example Agency using Anthropic Provider (GLM-4.7 via Z.AI)

This demonstrates a multi-agent system using the Anthropic provider with Z.AI's GLM-4.7 model.
Shows how to build a business consulting agency with multiple specialized agents.

Architecture:
- CEO Agent: Coordinates the team and delegates tasks
- Market Research Agent: Analyzes market trends and competition
- Financial Analyst: Handles financial planning and projections
- Strategy Agent: Develops business strategies and recommendations

All agents use GLM-4.7 via Z.AI's Anthropic-compatible API.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from indusagi import Agent, AgentConfig, Agency
from indusagi.tools import handoff_to_agent, set_current_agency, registry
from indusagi.tools.base import BaseTool
from pydantic import Field
from typing import ClassVar

# Load environment variables
load_dotenv()


# ============================================================================
# Business Consulting Tools
# ============================================================================

class MarketAnalysis(BaseTool):
    """Analyze market conditions for a specific industry."""

    name: ClassVar[str] = "market_analysis"
    description: ClassVar[str] = "Analyze market conditions for a specific industry"

    industry: str = Field(..., description="Industry to analyze (e.g., 'technology', 'retail', 'healthcare')")
    region: str = Field("global", description="Geographic region")

    def execute(self) -> str:
        analyses = {
            "technology": f"Technology sector in {self.region}: High growth, increased AI adoption, strong competition.",
            "retail": f"Retail sector in {self.region}: Digital transformation, omnichannel focus, supply chain challenges.",
            "healthcare": f"Healthcare sector in {self.region}: Innovation-driven, regulatory complexity, aging demographics.",
            "fintech": f"Fintech sector in {self.region}: Rapid innovation, regulatory evolution, customer-centric solutions.",
        }
        return analyses.get(self.industry.lower(), f"Limited data available for {self.industry} in {self.region}")


class FinancialProjection(BaseTool):
    """Calculate financial projections."""

    name: ClassVar[str] = "financial_projection"
    description: ClassVar[str] = "Calculate financial projections"

    revenue: float = Field(..., description="Current annual revenue")
    growth_rate: float = Field(..., description="Expected annual growth rate (as decimal, e.g., 0.15 for 15%)")
    years: int = Field(3, description="Number of years to project")

    def execute(self) -> str:
        projections = []
        current = self.revenue
        for year in range(1, self.years + 1):
            current = current * (1 + self.growth_rate)
            projections.append(f"Year {year}: ${current:,.2f}")

        return "Financial Projections:\n" + "\n".join(projections)


class CompetitorAnalysis(BaseTool):
    """Analyze competitive landscape."""

    name: ClassVar[str] = "competitor_analysis"
    description: ClassVar[str] = "Analyze competitive landscape"

    company_name: str = Field(..., description="Name of the company")
    competitors: str = Field(..., description="Comma-separated list of competitors")

    def execute(self) -> str:
        comp_list = [c.strip() for c in self.competitors.split(",")]
        return f"Competitive Analysis for {self.company_name}:\n" + \
               f"Main competitors: {', '.join(comp_list)}\n" + \
               f"Market position: Competing in a {len(comp_list)}-player market\n" + \
               f"Differentiation opportunity: Focus on unique value proposition"


class SwotAnalysis(BaseTool):
    """Generate SWOT analysis."""

    name: ClassVar[str] = "swot_analysis"
    description: ClassVar[str] = "Generate SWOT analysis"

    strengths: str = Field(..., description="Company strengths")
    weaknesses: str = Field(..., description="Company weaknesses")
    opportunities: str = Field(..., description="Market opportunities")
    threats: str = Field(..., description="External threats")

    def execute(self) -> str:
        return f"""
SWOT Analysis:
--------------
STRENGTHS:
{self.strengths}

WEAKNESSES:
{self.weaknesses}

OPPORTUNITIES:
{self.opportunities}

THREATS:
{self.threats}
"""


def create_anthropic_config(agent_name: str) -> AgentConfig:
    """Create Anthropic provider configuration for an agent."""
    return AgentConfig(
        model="glm-4.7",  # Using GLM-4.7 via Z.AI
        provider="anthropic",
        max_tokens=2048,
        temperature=0.7
    )


def setup_business_consulting_agency():
    """
    Set up a business consulting agency using Anthropic provider.

    Returns:
        Agency: Configured agency with multiple specialized agents
    """

    print("\n" + "=" * 70)
    print("Setting up Business Consulting Agency")
    print("Provider: Anthropic (GLM-4.7 via Z.AI)")
    print("=" * 70 + "\n")

    # Register business tools
    registry.register(MarketAnalysis)
    registry.register(FinancialProjection)
    registry.register(CompetitorAnalysis)
    registry.register(SwotAnalysis)

    # Create CEO Agent (coordinates the team)
    ceo_agent = Agent(
        name="CEO",
        role="Chief Executive - Business Consulting Agency",
        config=create_anthropic_config("CEO"),
        system_prompt="""You are the CEO of a business consulting agency.

Your responsibilities:
- Understand client needs and business challenges
- Delegate tasks to specialized agents (Market Research, Financial Analyst, Strategy)
- Coordinate team efforts for comprehensive solutions
- Synthesize insights from all agents into actionable recommendations

When a client presents a business question:
1. Analyze what expertise is needed
2. Delegate to appropriate agents using handoff_to_agent tool
3. Compile final recommendations

Available team:
- MarketResearch: Market analysis, industry trends, competitive landscape
- FinancialAnalyst: Financial projections, budgeting, ROI analysis
- Strategy: Business strategy, growth planning, SWOT analysis

Be professional, strategic, and results-oriented."""
    )

    # Create Market Research Agent
    market_research_agent = Agent(
        name="MarketResearch",
        role="Market Research Specialist",
        config=create_anthropic_config("MarketResearch"),
        system_prompt="""You are a Market Research Specialist.

Your expertise:
- Industry analysis and market trends
- Competitive landscape assessment
- Market size and growth potential
- Customer segmentation

Tools available:
- market_analysis: Analyze market conditions for industries
- competitor_analysis: Assess competitive landscape

Provide data-driven insights and actionable market intelligence.
When done, hand back to CEO with your findings."""
    )

    # Create Financial Analyst Agent
    financial_analyst_agent = Agent(
        name="FinancialAnalyst",
        role="Financial Analysis Expert",
        config=create_anthropic_config("FinancialAnalyst"),
        system_prompt="""You are a Financial Analyst.

Your expertise:
- Financial projections and forecasting
- Revenue modeling
- Cost analysis and optimization
- Investment ROI calculations

Tools available:
- financial_projection: Calculate growth projections

Provide clear, numbers-backed financial insights.
When done, hand back to CEO with your analysis."""
    )

    # Create Strategy Agent
    strategy_agent = Agent(
        name="Strategy",
        role="Business Strategy Consultant",
        config=create_anthropic_config("Strategy"),
        system_prompt="""You are a Business Strategy Consultant.

Your expertise:
- Strategic planning and roadmaps
- Business model innovation
- Growth strategies
- SWOT analysis and strategic frameworks

Tools available:
- swot_analysis: Generate SWOT analysis

Provide strategic recommendations with clear action plans.
When done, hand back to CEO with your strategy recommendations."""
    )

    # Set up communication flows (who can hand off to whom)
    communication_flows = [
        (ceo_agent, market_research_agent),  # CEO can delegate to Market Research
        (ceo_agent, financial_analyst_agent),  # CEO can delegate to Financial Analyst
        (ceo_agent, strategy_agent),  # CEO can delegate to Strategy
        (market_research_agent, ceo_agent),  # Market Research reports back to CEO
        (financial_analyst_agent, ceo_agent),  # Financial Analyst reports back to CEO
        (strategy_agent, ceo_agent),  # Strategy reports back to CEO
    ]

    # Create the Agency
    agency = Agency(
        name="BusinessConsultingAgency",
        entry_agent=ceo_agent,
        agents=[ceo_agent, market_research_agent, financial_analyst_agent, strategy_agent],
        communication_flows=communication_flows,
        tools=registry.schemas,
        tool_executor=registry,
        max_handoffs=100
    )

    # Set the current agency for handoff tools
    set_current_agency(agency)

    print("[OK] Agency created successfully")
    print(f"[OK] Entry Agent: {ceo_agent.name}")
    print(f"[OK] Team Size: {len(agency.agents)} agents")
    print(f"[OK] Tools Registered: {len(registry.get_tool_names())} tools")
    print(f"[OK] Provider: {ceo_agent.provider.get_provider_name()}")
    print(f"[OK] Model: {ceo_agent.config.model}\n")

    return agency


def run_business_consulting_scenarios(agency: Agency):
    """Run example business consulting scenarios."""

    scenarios = [
        {
            "title": "Startup Market Entry Strategy",
            "query": """We're a fintech startup planning to enter the digital payments market.
We have $500,000 in initial funding and expect 20% monthly growth.
Our main competitors are PayPal, Stripe, and Square.

Can you help us with:
1. Market analysis for the fintech industry
2. Financial projections for 3 years
3. Competitive analysis
4. Strategic recommendations for market entry"""
        },
        {
            "title": "Retail Business Expansion",
            "query": """We operate a regional retail chain with $5M annual revenue.
We're considering expanding to new markets and expect 15% annual growth.

We need:
1. Market analysis for retail industry
2. Financial projections for expansion (3 years, 15% growth)
3. SWOT analysis for expansion decision"""
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print("\n" + "=" * 70)
        print(f"SCENARIO {i}: {scenario['title']}")
        print("=" * 70 + "\n")

        print(f"Client Request:\n{scenario['query']}\n")
        print("-" * 70)
        print("Processing request through agency...\n")

        try:
            response = agency.process(scenario["query"])
            result = response.response  # Extract response text from AgencyResponse

            print("\n" + "=" * 70)
            print("FINAL RECOMMENDATIONS")
            print("=" * 70)
            print(result)
            print("=" * 70 + "\n")

            # Pause between scenarios
            if i < len(scenarios):
                input("Press Enter to continue to next scenario...")

        except Exception as e:
            print(f"\nError processing scenario: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Main execution function."""

    print("\n" + "=" * 70)
    print("BUSINESS CONSULTING AGENCY - ANTHROPIC PROVIDER DEMO")
    print("Using GLM-4.7 via Z.AI's Anthropic-Compatible API")
    print("=" * 70)

    # Verify environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n[ERROR] ANTHROPIC_API_KEY not set in environment")
        print("Please set it in your .env file")
        return

    provider = os.getenv("LLM_PROVIDER", "not set")
    print(f"\nEnvironment Configuration:")
    print(f"  LLM_PROVIDER: {provider}")
    print(f"  ANTHROPIC_MODEL: {os.getenv('ANTHROPIC_MODEL', 'not set')}")
    print(f"  ANTHROPIC_BASE_URL: {os.getenv('ANTHROPIC_BASE_URL', 'not set')}")

    try:
        # Set up agency
        agency = setup_business_consulting_agency()

        # Run scenarios
        run_business_consulting_scenarios(agency)

        print("\n" + "=" * 70)
        print("Demo completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
