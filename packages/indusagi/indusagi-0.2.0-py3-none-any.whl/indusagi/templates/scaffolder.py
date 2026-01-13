import os
import re
from typing import Optional
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_class_name(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return ''.join(word.capitalize() for word in name.split('_'))


def scaffold_agent(
    name: str,
    output_dir: str = ".",
    description: str = "A specialized agent",
    tools: Optional[list] = None
) -> str:
    """
    Scaffold a new agent directory with all necessary files.

    Args:
        name: Agent name (e.g., 'qa_tester' or 'QATester')
        output_dir: Where to create the agent directory
        description: Agent description for instructions
        tools: List of tool names to include

    Returns:
        Path to created agent directory
    """
    snake_name = to_snake_case(name)
    class_name = to_class_name(snake_name)

    # Create agent directory
    agent_dir = Path(output_dir) / f"{snake_name}_agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_content = f'''"""
{class_name} Agent - {description}
"""
from .{snake_name}_agent import create_{snake_name}_agent

__all__ = ["create_{snake_name}_agent"]
'''
    (agent_dir / "__init__.py").write_text(init_content)

    # Create agent factory file
    tools_list = tools or ["Read", "Write", "Bash"]
    tools_import = ", ".join(tools_list)

    agent_content = f'''"""
{class_name} Agent Factory

This module provides the factory function for creating {class_name} instances.
"""
import os
from typing import Optional

from indusagi import Agent, AgentConfig
from indusagi.templates import render_instructions
from indusagi.tools.dev import {tools_import}

current_dir = os.path.dirname(os.path.abspath(__file__))


def create_{snake_name}_agent(
    model: str = "gpt-4o",
    config: Optional[AgentConfig] = None,
    reasoning_effort: str = "medium"
) -> Agent:
    """
    Factory that returns a fresh {class_name} instance.

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
        name="{class_name}",
        role="{description}",
        config=agent_config,
        system_prompt=instructions,
        tools=[{tools_import}],
    )
'''
    (agent_dir / f"{snake_name}_agent.py").write_text(agent_content)

    # Create instructions.md
    instructions_content = f'''# {class_name} Agent

You are a {class_name} - {description}.

## Role and Objective

[Describe the agent's primary function and mission]

## Instructions

1. Be concise and direct in your responses
2. Use available tools appropriately
3. Follow existing code patterns and conventions
4. Do not create unnecessary files

## Communication Guidelines

- Use GitHub-flavored markdown for formatting
- Provide clear, actionable information
- Ask clarifying questions when requirements are ambiguous

## Handoff Guidelines

When you need assistance from another agent:
- Provide comprehensive context
- Explain what you've tried
- Specify what help you need

## Environment

<env>
Working directory: {{cwd}}
Is directory a git repo: {{is_git_repo}}
Platform: {{platform}}
OS Version: {{os_version}}
Today's date: {{today}}
Model Name: {{model}}
</env>
'''
    (agent_dir / "instructions.md").write_text(instructions_content)

    return str(agent_dir)
