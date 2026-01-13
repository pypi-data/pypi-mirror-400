"""
IndusAGI - Modern Agent Framework with Multi-Agent Orchestration

A production-ready agent framework featuring:
- OpenAI GPT-4o integration with tool calling
- Multi-agent orchestration with intelligent routing
- Conversation memory management
- Beautiful CLI interface
- 9 built-in tools
- Comprehensive testing (92% coverage)

Quick Start:
    >>> from indusagi import Agent, create_orchestrator
    >>>
    >>> # Single agent
    >>> agent = Agent("Helper", "Helpful assistant")
    >>> response = agent.process("What is 2+2?")
    >>>
    >>> # Multi-agent orchestrator (recommended)
    >>> orchestrator = create_orchestrator()
    >>> response = orchestrator.process("Calculate 25 * 4")
    >>> print(response.response)

Installation:
    pip install -e .

CLI Usage:
    indusagi run "What is 25 * 48?"
    indusagi interactive
    indusagi list-tools

For more information, see README.md
"""

__version__ = "0.2.0"
__author__ = "IndusAGI Team"
__email__ = "contact@example.com"
__license__ = "MIT"

# Core imports from working implementation files
from indusagi.agent import Agent, AgentConfig
from indusagi.tools import registry, ToolRegistry
from indusagi.orchestrator import MultiAgentOrchestrator, OrchestratorResponse, create_orchestrator
from indusagi.memory import ConversationMemory, Message

# Import Agency after other imports to avoid circular dependencies
from indusagi.agency import Agency, AgencyResponse, HandoffResult, HandoffType

# Import tool usage logger
from indusagi.tool_usage_logger import tool_logger, ToolUsageLogger

# Expose public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",

    # Core classes
    "Agent",
    "AgentConfig",

    # Tool system
    "ToolRegistry",
    "registry",

    # Orchestrator
    "MultiAgentOrchestrator",
    "OrchestratorResponse",
    "create_orchestrator",

    # Memory
    "ConversationMemory",
    "Message",

    # Agency
    "Agency",
    "AgencyResponse",
    "HandoffResult",
    "HandoffType",

    # Tool Usage Logging
    "tool_logger",
    "ToolUsageLogger",

    # Templates (imported on demand)
    # "templates",
]

# Convenience function
def get_version() -> str:
    """Get the current version of the framework."""
    return __version__
