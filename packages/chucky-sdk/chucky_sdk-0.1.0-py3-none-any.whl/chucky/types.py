"""Type definitions for Chucky SDK."""

from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
)


# ============================================================================
# Token & Budget Types
# ============================================================================


class Budget(TypedDict):
    """Budget configuration in the billing token."""

    ai: int  # AI budget in microdollars (1 USD = 1,000,000)
    compute: int  # Compute budget in seconds
    window: Literal["hour", "day", "week", "month"]
    windowStart: str  # ISO 8601 date string


class BudgetToken(TypedDict, total=False):
    """Billing token payload (JWT claims)."""

    sub: str  # User ID
    iss: str  # Issuer/Project ID (UUID)
    exp: int  # Token expiry timestamp (Unix seconds)
    iat: int  # Issued at timestamp (Unix seconds)
    budget: Budget


# ============================================================================
# SDK Message Types
# ============================================================================


class ContentBlock(TypedDict, total=False):
    """Content block in SDK messages."""

    type: Literal["text", "tool_use", "tool_result"]
    text: str
    id: str
    name: str
    input: Dict[str, Any]
    tool_use_id: str
    content: str


class MessageContent(TypedDict):
    """Message content structure."""

    role: str
    content: List[ContentBlock]


class SDKMessage(TypedDict, total=False):
    """SDK message from the server."""

    type: Literal["user", "assistant", "result", "system"]
    message: MessageContent
    session_id: str
    result: str
    total_cost_usd: float
    duration_ms: int


# ============================================================================
# Tool Types
# ============================================================================


class ToolResultContent(TypedDict):
    """Tool result content block."""

    type: Literal["text"]
    text: str


@dataclass
class ToolResult:
    """Result from a tool execution."""

    content: List[ToolResultContent]
    is_error: bool = False


# Tool handler type
ToolHandler = Callable[[Dict[str, Any]], Union[ToolResult, Awaitable[ToolResult]]]


class InputSchemaProperty(TypedDict, total=False):
    """JSON Schema property definition."""

    type: str
    description: str
    enum: List[str]
    default: Any


class InputSchema(TypedDict, total=False):
    """JSON Schema for tool input."""

    type: Literal["object"]
    properties: Dict[str, InputSchemaProperty]
    required: List[str]


@dataclass
class Tool:
    """Tool definition."""

    name: str
    description: str
    input_schema: InputSchema
    handler: ToolHandler
    execute_in: Literal["client"] = "client"


@dataclass
class McpServer:
    """MCP server with tools."""

    name: str
    tools: List[Tool]
    version: str = "1.0.0"


# ============================================================================
# Client Types
# ============================================================================


@dataclass
class ChuckyOptions:
    """Options for creating a Chucky client."""

    url: str  # Chucky server URL (WebSocket)
    token: str  # Billing token (JWT)
    model: str = "claude-sonnet-4-5-20250929"
    system_prompt: Optional[str] = None
    max_turns: Optional[int] = None
    allowed_tools: Optional[List[str]] = None
    disallowed_tools: Optional[List[str]] = None
    mcp_servers: Optional[Dict[str, McpServer]] = None
    timeout: float = 30.0  # Connection timeout in seconds
    keepalive_interval: float = 60.0  # Keep-alive interval in seconds


@dataclass
class PromptOptions:
    """Options for a single prompt."""

    model: Optional[str] = None
    system_prompt: Optional[str] = None
    max_turns: Optional[int] = None
    tools: Optional[List[Tool]] = None


@dataclass
class PromptResult:
    """Result from a prompt."""

    result: str
    messages: List[SDKMessage]
    session_id: str
    total_cost_usd: Optional[float] = None
    duration_ms: Optional[int] = None


@dataclass
class StreamEvent:
    """Event from streaming."""

    type: Literal["message", "result", "error", "done"]
    data: Union[SDKMessage, Dict[str, Any]]
