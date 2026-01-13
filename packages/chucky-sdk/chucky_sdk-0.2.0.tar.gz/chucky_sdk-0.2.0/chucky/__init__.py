"""
Chucky SDK - Python client for Claude Agent as a Service.

Types and API match the official Claude Agent SDK.
See: https://platform.claude.com/docs/en/agent-sdk/python

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

from .client import Chucky, Session, get_assistant_text, get_result_text
from .tools import create_mcp_server, create_sdk_mcp_server, error_result, text_result, tool
from .types import (
    # Message types (official SDK format)
    AssistantMessage,
    Budget,
    BudgetToken,
    ChuckyOptions,
    ContentBlock,
    InputSchema,
    McpServer,
    McpSdkServerConfig,
    Message,
    PromptOptions,
    PromptResult,
    ResultMessage,
    SDKMessage,
    SdkMcpTool,
    StreamEvent,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    Tool,
    ToolResult,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
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

__version__ = "0.2.0"

__all__ = [
    # Client
    "Chucky",
    "Session",
    "get_assistant_text",
    "get_result_text",
    # Tool helpers
    "tool",
    "create_mcp_server",
    "create_sdk_mcp_server",
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
    # Message types (official SDK format)
    "Message",
    "UserMessage",
    "AssistantMessage",
    "SystemMessage",
    "ResultMessage",
    # Content block types
    "ContentBlock",
    "TextBlock",
    "ThinkingBlock",
    "ToolUseBlock",
    "ToolResultBlock",
    # Tool types
    "SdkMcpTool",
    "Tool",
    "ToolResult",
    "McpServer",
    "McpSdkServerConfig",
    "InputSchema",
    # Client types
    "ChuckyOptions",
    "PromptOptions",
    "PromptResult",
    "StreamEvent",
    # Token types
    "Budget",
    "BudgetToken",
    # Legacy
    "SDKMessage",
]
