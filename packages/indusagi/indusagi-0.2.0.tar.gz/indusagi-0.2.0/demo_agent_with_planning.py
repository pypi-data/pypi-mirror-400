"""
Demo: Agent with Visible Planning and Tool Execution

This script demonstrates an autonomous agent that:
1. Receives a user query
2. Creates a plan showing which tools to use
3. Executes tools in order
4. Shows all steps in console with detailed logging

The agent uses OpenAI's function calling to autonomously decide which tools to use.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("\n" + "="*70)
    print("ERROR: OPENAI_API_KEY not found!")
    print("="*70)
    print("\nPlease set your API key:")
    print("1. Copy .env.example to .env")
    print("2. Add your key: OPENAI_API_KEY=sk-proj-your-key-here")
    print("\nOr set it temporarily:")
    print("  export OPENAI_API_KEY='your-key-here'  # Linux/Mac")
    print("  $env:OPENAI_API_KEY='your-key-here'    # Windows PowerShell")
    print("\n" + "="*70)
    sys.exit(1)

from indusagi import Agent, registry

def print_banner(text, char="="):
    """Print a banner with text."""
    print("\n" + char * 70)
    print(text.center(70))
    print(char * 70)

def print_step(step_num, total_steps, description):
    """Print a step in the process."""
    print(f"\n[Step {step_num}/{total_steps}] {description}")
    print("-" * 70)

def print_tool_call(tool_name, arguments):
    """Print tool call details."""
    print(f"\n  Tool: Tool: {tool_name}")
    print(f"  Args: Arguments: {arguments}")

def print_tool_result(result):
    """Print tool result."""
    print(f"  OK: Result: {result}")

class PlanningAgent(Agent):
    """
    Enhanced Agent with visible planning and execution logging.
    """

    def __init__(self, name, role, config=None):
        super().__init__(name, role, config=config)
        self.execution_log = []

    def process_with_detailed_logging(self, user_input: str, max_turns: int = 5) -> str:
        """
        Process user input with detailed step-by-step logging.

        Shows:
        - User query
        - Agent's planning (when it decides to use tools)
        - Tool execution with arguments
        - Tool results
        - Final response
        """
        print_banner(f">>> AGENT: {self.name}", "=")
        print(f"Role: {self.role}")
        print(f"Model: {self.config.model}")

        print_step(1, 4, "RECEIVING USER QUERY")
        print(f"User Query: \"{user_input}\"")

        # Add user message
        self.messages.append({"role": "user", "content": user_input})

        print_step(2, 4, "AGENT ANALYZING QUERY & CREATING PLAN")
        print("Agent is thinking about which tools to use...")

        turn_number = 0

        for turn in range(max_turns):
            turn_number += 1

            try:
                # Call OpenAI API with tools
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    tools=registry.schemas,
                    messages=self.messages
                )

                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason

                # Check if agent wants to use tools
                if finish_reason == "tool_calls" and message.tool_calls:
                    # Agent has created a plan!
                    print_step(3, 4, f"EXECUTING PLAN (Turn {turn_number})")
                    print(f"\n>>> Agent's Plan: Use {len(message.tool_calls)} tool(s)")

                    # Show the plan
                    for i, tool_call in enumerate(message.tool_calls, 1):
                        print(f"  {i}. {tool_call.function.name}({tool_call.function.arguments})")

                    # Add assistant message with tool calls
                    self.messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    })

                    # Execute each tool
                    print(f"\n>>>  Executing Tools:")
                    for i, tool_call in enumerate(message.tool_calls, 1):
                        tool_name = tool_call.function.name

                        # Parse arguments
                        import json
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except:
                            arguments = {}

                        print(f"\n  Tool {i}/{len(message.tool_calls)}:")
                        print_tool_call(tool_name, arguments)

                        # Execute tool
                        result = registry.execute(tool_name, **arguments)
                        print_tool_result(result)

                        # Log execution
                        self.execution_log.append({
                            "turn": turn_number,
                            "tool": tool_name,
                            "arguments": arguments,
                            "result": result
                        })

                        # Add tool result to messages
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": str(result)
                        })

                    print(f"\n[OK] All tools executed successfully!")

                    # Continue to next turn to get final response
                    continue

                elif finish_reason == "stop":
                    # Agent has final answer
                    final_response = message.content

                    print_step(4, 4, "FINAL RESPONSE")
                    print(f"\nAgent: {final_response}")

                    # Add to messages
                    self.messages.append({
                        "role": "assistant",
                        "content": final_response
                    })

                    # Show execution summary
                    if self.execution_log:
                        print_banner(">>> EXECUTION SUMMARY", "-")
                        print(f"Total Turns: {turn_number}")
                        print(f"Tools Used: {len(self.execution_log)}")
                        for i, log in enumerate(self.execution_log, 1):
                            print(f"\n{i}. Turn {log['turn']}: {log['tool']}")
                            print(f"   Args: {log['arguments']}")
                            print(f"   Result: {log['result']}")

                    print_banner("OK: TASK COMPLETE", "=")
                    return final_response

                else:
                    # Unexpected finish reason
                    print(f"\nWARNING:  Unexpected finish reason: {finish_reason}")
                    return f"Unexpected finish reason: {finish_reason}"

            except Exception as e:
                print(f"\nERROR: Error: {str(e)}")
                return f"Error: {str(e)}"

        return "Maximum turns reached without completing task"


def main():
    """Run the demo with example queries."""

    print_banner(">>> AUTONOMOUS AGENT WITH PLANNING DEMO", "=")
    print("\nThis demo shows an agent that:")
    print("  1. Analyzes user queries")
    print("  2. Creates a plan (which tools to use)")
    print("  3. Executes tools step-by-step")
    print("  4. Shows all steps in the console")

    # Create planning agent
    agent = PlanningAgent(
        name="PlanningBot",
        role="Autonomous assistant that plans and executes tasks using available tools"
    )

    # Example queries to demonstrate
    example_queries = [
        "What is 144 divided by 12, and what time is it right now?",
        "Calculate 25 * 48 and then tell me the result in uppercase",
        "What's the current date and time?",
        "Reverse the text 'HELLO WORLD' and count how many words it has"
    ]

    print("\n" + "="*70)
    print("Available example queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"  {i}. {query}")
    print("="*70)

    # Let user choose or enter custom query
    print("\nOptions:")
    print("  - Enter a number (1-4) to use an example query")
    print("  - Type your own query")
    print("  - Press Enter to use example 1")

    user_choice = input("\nYour choice: ").strip()

    if user_choice == "":
        query = example_queries[0]
        print(f"Using example 1: {query}")
    elif user_choice.isdigit() and 1 <= int(user_choice) <= len(example_queries):
        query = example_queries[int(user_choice) - 1]
        print(f"Using example {user_choice}: {query}")
    else:
        query = user_choice
        print(f"Using custom query: {query}")

    # Process the query with detailed logging
    print("\n" + "="*70)
    print("STARTING AGENT EXECUTION")
    print("="*70)

    response = agent.process_with_detailed_logging(query)

    print("\n" + "="*70)
    print("Demo complete! The agent showed its planning and execution process.")
    print("="*70)


if __name__ == "__main__":
    main()
