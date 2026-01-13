"""
Template System for Agent Generation

This module provides template rendering and agent scaffolding utilities.
"""

from .renderer import render_instructions
from .scaffolder import scaffold_agent, to_snake_case, to_class_name

__all__ = [
    "render_instructions",
    "scaffold_agent",
    "to_snake_case",
    "to_class_name",
]
