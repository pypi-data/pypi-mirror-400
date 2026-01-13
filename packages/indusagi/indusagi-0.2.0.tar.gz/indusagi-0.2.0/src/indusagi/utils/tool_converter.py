"""
Tool schema conversion utilities.

Converts tool/function schemas between OpenAI and Anthropic formats.
"""

from typing import List, Dict, Any


def convert_openai_tools_to_anthropic(openai_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert OpenAI tool schema format to Anthropic tool schema format.

    OpenAI format:
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate mathematical expressions",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    }

    Anthropic format:
    {
        "name": "calculator",
        "description": "Calculate mathematical expressions",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"]
        }
    }

    Args:
        openai_tools: List of tools in OpenAI format

    Returns:
        List of tools in Anthropic format
    """
    anthropic_tools = []

    for tool in openai_tools:
        if tool.get("type") == "function":
            func = tool["function"]
            anthropic_tools.append({
                "name": func["name"],
                "description": func.get("description", ""),
                "input_schema": func.get("parameters", {})
            })

    return anthropic_tools


def convert_anthropic_tools_to_openai(anthropic_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert Anthropic tool schema format to OpenAI tool schema format.

    Args:
        anthropic_tools: List of tools in Anthropic format

    Returns:
        List of tools in OpenAI format
    """
    openai_tools = []

    for tool in anthropic_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {})
            }
        })

    return openai_tools
