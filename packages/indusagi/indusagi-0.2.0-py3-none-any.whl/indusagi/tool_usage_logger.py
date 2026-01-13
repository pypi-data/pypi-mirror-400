"""
Tool Usage Logger - Track and analyze tool usage patterns.
"""
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field
from collections import Counter


@dataclass
class ToolCall:
    """Record of a single tool call."""
    tool_name: str
    timestamp: float
    agent_name: str
    arguments: Dict[str, Any]
    result: str
    success: bool
    execution_time: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "agent_name": self.agent_name,
            "arguments": self.arguments,
            "result": self.result[:200] + "..." if len(self.result) > 200 else self.result,
            "success": self.success,
            "execution_time": self.execution_time,
            "error": self.error
        }


class ToolUsageLogger:
    """
    Logger for tracking tool usage across agents.

    Tracks all tool calls, provides statistics, and can export logs.
    """

    def __init__(self):
        self.calls: List[ToolCall] = []
        self.session_start = time.time()

    def log_call(
        self,
        tool_name: str,
        agent_name: str,
        arguments: Dict[str, Any],
        result: str,
        success: bool = True,
        execution_time: float = 0.0,
        error: Optional[str] = None
    ) -> None:
        """
        Log a tool call.

        Args:
            tool_name: Name of the tool
            agent_name: Name of the agent that called the tool
            arguments: Arguments passed to the tool
            result: Result returned by the tool
            success: Whether the call was successful
            execution_time: Time taken to execute (seconds)
            error: Error message if failed
        """
        call = ToolCall(
            tool_name=tool_name,
            timestamp=time.time(),
            agent_name=agent_name,
            arguments=arguments.copy(),
            result=result,
            success=success,
            execution_time=execution_time,
            error=error
        )
        self.calls.append(call)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get usage statistics.

        Returns:
            Dictionary with statistics about tool usage
        """
        if not self.calls:
            return {
                "total_calls": 0,
                "session_duration": time.time() - self.session_start,
                "tools_used": [],
                "agents_active": []
            }

        # Count tool usage
        tool_counts = Counter(call.tool_name for call in self.calls)
        agent_counts = Counter(call.agent_name for call in self.calls)

        # Calculate success rates
        total_calls = len(self.calls)
        successful_calls = sum(1 for call in self.calls if call.success)
        failed_calls = total_calls - successful_calls

        # Calculate execution times
        total_execution_time = sum(call.execution_time for call in self.calls)
        avg_execution_time = total_execution_time / total_calls if total_calls > 0 else 0

        # Tool-specific stats
        tool_stats = {}
        for tool_name in tool_counts:
            tool_calls = [c for c in self.calls if c.tool_name == tool_name]
            tool_stats[tool_name] = {
                "count": len(tool_calls),
                "success_rate": sum(1 for c in tool_calls if c.success) / len(tool_calls) * 100,
                "avg_execution_time": sum(c.execution_time for c in tool_calls) / len(tool_calls)
            }

        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0,
            "session_duration": time.time() - self.session_start,
            "total_execution_time": total_execution_time,
            "avg_execution_time": avg_execution_time,
            "tools_used": dict(tool_counts),
            "agents_active": dict(agent_counts),
            "tool_statistics": tool_stats
        }

    def get_recent_calls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent tool calls.

        Args:
            limit: Maximum number of calls to return

        Returns:
            List of recent tool calls as dictionaries
        """
        recent = self.calls[-limit:] if len(self.calls) > limit else self.calls
        return [call.to_dict() for call in reversed(recent)]

    def get_calls_by_tool(self, tool_name: str) -> List[Dict[str, Any]]:
        """
        Get all calls for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List of calls for that tool
        """
        return [
            call.to_dict()
            for call in self.calls
            if call.tool_name == tool_name
        ]

    def get_calls_by_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        Get all calls made by a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            List of calls by that agent
        """
        return [
            call.to_dict()
            for call in self.calls
            if call.agent_name == agent_name
        ]

    def get_failed_calls(self) -> List[Dict[str, Any]]:
        """
        Get all failed tool calls.

        Returns:
            List of failed calls
        """
        return [
            call.to_dict()
            for call in self.calls
            if not call.success
        ]

    def print_statistics(self) -> None:
        """Print usage statistics in a readable format."""
        stats = self.get_statistics()

        print("\n" + "="*70)
        print("📊 TOOL USAGE STATISTICS")
        print("="*70)

        # Overall stats
        print(f"\n📈 Overall:")
        print(f"  Total Calls:     {stats['total_calls']}")
        print(f"  Successful:      {stats['successful_calls']} ({stats['success_rate']:.1f}%)")
        print(f"  Failed:          {stats['failed_calls']}")
        print(f"  Session Time:    {stats['session_duration']:.1f}s")
        print(f"  Total Exec Time: {stats['total_execution_time']:.2f}s")
        print(f"  Avg Exec Time:   {stats['avg_execution_time']:.3f}s")

        # Tools used
        print(f"\n🔧 Tools Used:")
        for tool, count in sorted(stats['tools_used'].items(), key=lambda x: x[1], reverse=True):
            tool_stat = stats['tool_statistics'][tool]
            print(f"  {tool:20s} {count:3d} calls  ({tool_stat['success_rate']:.0f}% success, {tool_stat['avg_execution_time']:.3f}s avg)")

        # Agents active
        print(f"\n🤖 Agents Active:")
        for agent, count in sorted(stats['agents_active'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {agent:20s} {count:3d} calls")

        print("="*70 + "\n")

    def print_recent_calls(self, limit: int = 5) -> None:
        """
        Print recent tool calls.

        Args:
            limit: Number of recent calls to show
        """
        recent = self.get_recent_calls(limit)

        print("\n" + "="*70)
        print(f"📝 RECENT TOOL CALLS (Last {limit})")
        print("="*70)

        for i, call in enumerate(recent, 1):
            status = "✅" if call['success'] else "❌"
            print(f"\n{i}. {status} [{call['agent_name']}] {call['tool_name']}")
            print(f"   Time: {call['datetime']}")

            # Show key arguments
            if call['arguments']:
                args_str = ", ".join(f"{k}={v}" for k, v in list(call['arguments'].items())[:2])
                if len(call['arguments']) > 2:
                    args_str += ", ..."
                print(f"   Args: {args_str}")

            # Show result snippet
            result = call['result']
            if len(result) > 80:
                result = result[:77] + "..."
            print(f"   Result: {result}")

            if call['error']:
                print(f"   Error: {call['error']}")

        print("="*70 + "\n")

    def export_to_json(self, filepath: str) -> None:
        """
        Export all logs to JSON file.

        Args:
            filepath: Path to save the JSON file
        """
        data = {
            "session_start": datetime.fromtimestamp(self.session_start).isoformat(),
            "statistics": self.get_statistics(),
            "calls": [call.to_dict() for call in self.calls]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Logs exported to {filepath}")

    def clear(self) -> None:
        """Clear all logged calls."""
        self.calls = []
        self.session_start = time.time()


# Global logger instance
tool_logger = ToolUsageLogger()


__all__ = [
    "ToolCall",
    "ToolUsageLogger",
    "tool_logger"
]
