"""Basic usage example for indus-agents."""

import asyncio

from indusagi import Agent
from indusagi.agent.base import AgentConfig
from indusagi.core.config import Config


async def main():
    """Run a basic agent example."""
    # Load configuration
    config = Config()

    # Check if API key is set
    if not config.validate_api_key():
        print("Warning: OPENAI_API_KEY not set in environment")
        print("Please set it in your .env file")
        return

    # Create agent configuration
    agent_config = AgentConfig(
        name="BasicAgent",
        model=config.default_model,
        temperature=config.default_temperature,
    )

    # Create agent
    agent = Agent(config=agent_config)

    # Run agent with a prompt
    prompt = "Hello, can you help me understand what you can do?"
    print(f"User: {prompt}")

    response = await agent.run(prompt)
    print(f"Agent: {response}")

    # Check history
    history = agent.get_history()
    print(f"\nConversation history: {len(history)} turns")


if __name__ == "__main__":
    asyncio.run(main())
