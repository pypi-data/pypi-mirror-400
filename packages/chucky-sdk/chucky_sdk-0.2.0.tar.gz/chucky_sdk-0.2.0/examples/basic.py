"""
Basic example of using the Chucky SDK.

Run with: PYTHONPATH=. python examples/basic.py

Environment variables:
  CHUCKY_URL        - WebSocket URL (default: wss://conjure.chucky.cloud/ws)
  CHUCKY_PROJECT_ID - Your project ID from the portal (app.chucky.cloud)
  CHUCKY_SECRET     - Your HMAC secret from the portal
"""

import asyncio
import os
from datetime import datetime
from typing import Literal

from chucky import (
    Chucky,
    PromptOptions,
    ToolResult,
    create_budget,
    create_token,
    text_result,
    tool,
)


# ============================================================================
# Define Tools
# ============================================================================


@tool("get_current_time", "Get the current date and time")
async def get_current_time() -> ToolResult:
    return text_result(datetime.now().isoformat())


@tool("greet", "Greet someone by name")
async def greet(
    name: str,
    style: Literal["formal", "casual"] = "casual",
) -> ToolResult:
    """
    Greet someone.

    Args:
        name: The name of the person to greet
        style: The greeting style (formal or casual)
    """
    if style == "formal":
        greeting = f"Good day, {name}. How may I assist you?"
    else:
        greeting = f"Hey {name}! What's up?"
    return text_result(greeting)


@tool("calculate", "Perform a mathematical calculation")
async def calculate(expression: str) -> ToolResult:
    """
    Evaluate a math expression.

    Args:
        expression: Math expression to evaluate (e.g., "2 + 2")
    """
    try:
        # Simple safe eval for basic math
        result = eval(expression, {"__builtins__": {}}, {})
        return text_result(f"{expression} = {result}")
    except Exception as e:
        return ToolResult(
            content=[{"type": "text", "text": f"Error: {str(e)}"}],
            is_error=True,
        )


# ============================================================================
# Main
# ============================================================================


async def main():
    # Configuration - get these from your Chucky portal (app.chucky.cloud)
    url = os.environ.get("CHUCKY_URL", "wss://conjure.chucky.cloud/ws")
    project_id = os.environ.get("CHUCKY_PROJECT_ID")
    secret = os.environ.get("CHUCKY_SECRET")
    user_id = "user_123"

    if not project_id or not secret:
        print("Error: Please set CHUCKY_PROJECT_ID and CHUCKY_SECRET environment variables")
        print("Get these from your project settings at app.chucky.cloud")
        return

    print(f"Project ID: {project_id}")

    # Generate token using SDK utilities
    token = create_token(
        user_id=user_id,
        project_id=project_id,
        secret=secret,
        budget=create_budget(
            ai_dollars=10.00,  # $10 budget
            compute_hours=1,   # 1 hour compute
            window="day",
        ),
    )
    print(f"Generated token for user: {user_id}")

    # Create client
    client = Chucky(
        url=url,
        token=token,
        model="claude-sonnet-4-5-20250929",
    )

    print("\n--- Example 1: Simple prompt ---\n")

    try:
        result = await client.prompt("What is 2 + 2? Answer briefly.")
        print(f"Result: {result.result}")
        print(f"Cost: ${result.total_cost_usd:.4f}" if result.total_cost_usd else "Cost: N/A")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Example 2: Streaming ---\n")

    try:
        async for event in client.stream("Tell me a very short joke (one sentence)."):
            if event.type == "message":
                msg = event.data
                if msg.get("type") == "assistant":
                    content = msg.get("message", {}).get("content", [])
                    for block in content:
                        if block.get("type") == "text" and block.get("text"):
                            print(block["text"], end="", flush=True)
            elif event.type == "done":
                print("\n[Done]")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Example 3: With tools ---\n")

    try:
        result = await client.prompt(
            'Please greet "Alice" casually, then tell me the current time.',
            tools=[greet, get_current_time],
        )
        print(f"Result: {result.result}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
