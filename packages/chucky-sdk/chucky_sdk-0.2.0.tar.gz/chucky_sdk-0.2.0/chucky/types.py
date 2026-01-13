"""Type definitions for Chucky SDK.

These types match the official Claude Agent SDK format.
See: https://platform.claude.com/docs/en/agent-sdk/python
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    TypedDict,
    TypeVar,
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
# Content Block Types (matching official SDK)
# ============================================================================


@dataclass
class TextBlock:
    """Text content block."""

    text: str
    type: Literal["text"] = "text"


@dataclass
class ThinkingBlock:
    """Thinking content block (for models with thinking capability)."""

    thinking: str
    signature: str
    type: Literal["thinking"] = "thinking"


@dataclass
class ToolUseBlock:
    """Tool use request block."""

    id: str
    name: str
    input: Dict[str, Any]
    type: Literal["tool_use"] = "tool_use"


@dataclass
class ToolResultBlock:
    """Tool execution result block."""

    tool_use_id: str
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    is_error: Optional[bool] = None
    type: Literal["tool_result"] = "tool_result"


# Union type of all content blocks
ContentBlock = Union[TextBlock, ThinkingBlock, ToolUseBlock, ToolResultBlock]


# ============================================================================
# Message Types (matching official SDK)
# ============================================================================


@dataclass
class UserMessage:
    """User input message."""

    content: Union[str, List[ContentBlock]]
    type: Literal["user"] = "user"


@dataclass
class AssistantMessage:
    """Assistant response message with content blocks."""

    content: List[ContentBlock]
    model: str
    type: Literal["assistant"] = "assistant"


@dataclass
class SystemMessage:
    """System message with metadata."""

    subtype: str
    data: Dict[str, Any]
    type: Literal["system"] = "system"


@dataclass
class ResultMessage:
    """Final result message with cost and usage information."""

    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: Optional[float] = None
    usage: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    type: Literal["result"] = "result"


# Union type of all message types
Message = Union[UserMessage, AssistantMessage, SystemMessage, ResultMessage]


# ============================================================================
# Tool Types (matching official SDK)
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


# Type variable for tool input
T = TypeVar("T")


# Tool handler type - accepts dict and returns ToolResult or dict
ToolHandler = Callable[[Dict[str, Any]], Union[ToolResult, Dict[str, Any], Awaitable[Union[ToolResult, Dict[str, Any]]]]]


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
class SdkMcpTool(Generic[T]):
    """Definition for an SDK MCP tool created with the @tool decorator."""

    name: str
    description: str
    input_schema: Union[type, Dict[str, Any]]
    handler: Callable[[T], Awaitable[Dict[str, Any]]]


# Keep Tool as alias for backwards compatibility
@dataclass
class Tool:
    """Tool definition."""

    name: str
    description: str
    input_schema: InputSchema
    handler: ToolHandler
    execute_in: Literal["client"] = "client"


@dataclass
class McpSdkServerConfig:
    """Configuration for SDK MCP servers created with create_sdk_mcp_server()."""

    type: Literal["sdk"] = "sdk"
    name: str = ""
    instance: Any = None  # MCP Server instance


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
    messages: List[Message]
    session_id: str
    total_cost_usd: Optional[float] = None
    duration_ms: Optional[int] = None


@dataclass
class StreamEvent:
    """Event from streaming."""

    type: Literal["message", "result", "error", "done"]
    data: Union[Message, Dict[str, Any]]


# ============================================================================
# Legacy SDK Message Types (for backwards compatibility)
# ============================================================================


class LegacyContentBlock(TypedDict, total=False):
    """Content block in SDK messages (legacy format)."""

    type: Literal["text", "tool_use", "tool_result"]
    text: str
    id: str
    name: str
    input: Dict[str, Any]
    tool_use_id: str
    content: str


class MessageContent(TypedDict):
    """Message content structure (legacy format)."""

    role: str
    content: List[LegacyContentBlock]


class SDKMessage(TypedDict, total=False):
    """SDK message from the server (legacy format)."""

    type: Literal["user", "assistant", "result", "system"]
    message: MessageContent
    session_id: str
    result: str
    total_cost_usd: float
    duration_ms: int
