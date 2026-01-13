"""
Chucky SDK - Python client for Claude Agent as a Service.

Example:
    ```python
    from chucky import Chucky, tool, text_result, create_token, create_budget

    # Create token (server-side)
    # Get project_id and secret from app.chucky.cloud
    token = create_token(
        user_id='user-123',
        project_id='your-project-id',  # From portal
        secret='your-hmac-secret',      # From portal
        budget=create_budget(ai_dollars=1.00, compute_hours=1, window='day'),
    )

    # Define a tool that executes locally
    @tool("greet", "Greet someone by name")
    async def greet(name: str) -> ToolResult:
        return text_result(f"Hello, {name}!")

    # Create client
    client = Chucky(
        url='wss://conjure.chucky.cloud/ws',
        token=token,
    )

    # One-shot prompt
    result = await client.prompt('What is 2 + 2?')
    print(result.result)

    # Streaming with tools
    async for event in client.stream('Greet the world!', options=PromptOptions(tools=[greet])):
        if event.type == 'message':
            print(event.data)
    ```
"""

from .client import Chucky
from .tools import create_mcp_server, error_result, text_result, tool
from .types import (
    Budget,
    BudgetToken,
    ChuckyOptions,
    InputSchema,
    McpServer,
    PromptOptions,
    PromptResult,
    SDKMessage,
    StreamEvent,
    Tool,
    ToolResult,
)
from .utils import (
    TokenBudget,
    create_budget,
    create_token,
    decode_token,
    extract_project_id,
    is_token_expired,
    verify_token,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "Chucky",
    # Tool helpers
    "tool",
    "create_mcp_server",
    "text_result",
    "error_result",
    # Token utilities
    "create_token",
    "create_budget",
    "decode_token",
    "verify_token",
    "is_token_expired",
    "extract_project_id",
    "TokenBudget",
    # Types
    "ChuckyOptions",
    "PromptOptions",
    "PromptResult",
    "StreamEvent",
    "SDKMessage",
    "Tool",
    "ToolResult",
    "McpServer",
    "InputSchema",
    "Budget",
    "BudgetToken",
]
