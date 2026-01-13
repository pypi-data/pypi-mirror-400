"""
DataAnalyst Agent Factory

This module provides the factory function for creating DataAnalyst instances.
"""
import os
from typing import Optional

from indusagi import Agent, AgentConfig
from indusagi.templates import render_instructions
from indusagi.tools.dev import Read, Write, Bash

current_dir = os.path.dirname(os.path.abspath(__file__))


def create_data_analyst_agent(
    model: str = "gpt-4o",
    config: Optional[AgentConfig] = None,
    reasoning_effort: str = "medium"
) -> Agent:
    """
    Factory that returns a fresh DataAnalyst instance.

    Args:
        model: The LLM model to use
        config: Optional agent configuration
        reasoning_effort: Reasoning effort level (low, medium, high)

    Returns:
        Configured Agent instance
    """
    instructions = render_instructions(
        os.path.join(current_dir, "instructions.md"),
        model=model
    )

    agent_config = config or AgentConfig.from_env()
    agent_config.model = model

    return Agent(
        name="DataAnalyst",
        role="Analyzes data and generates reports",
        config=agent_config,
        system_prompt=instructions,
        tools=[Read, Write, Bash],
    )
