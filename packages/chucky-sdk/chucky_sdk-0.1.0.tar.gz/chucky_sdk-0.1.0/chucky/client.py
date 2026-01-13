"""Chucky SDK client implementation."""

import asyncio
import json
from typing import Any, AsyncIterator, Dict, List, Optional
from urllib.parse import urlencode, urlparse, urlunparse

import websockets
from websockets.client import WebSocketClientProtocol

from .types import (
    ChuckyOptions,
    McpServer,
    PromptOptions,
    PromptResult,
    SDKMessage,
    StreamEvent,
    Tool,
    ToolHandler,
    ToolResult,
)


class Chucky:
    """
    Chucky SDK Client.

    Connects to a Chucky server via WebSocket and provides methods for
    sending prompts and receiving streaming responses.

    Example:
        ```python
        from chucky import Chucky

        client = Chucky(
            url='wss://chuckybox.example.com/ws',
            token='your-jwt-token',
        )

        # One-shot prompt
        result = await client.prompt('What is 2 + 2?')
        print(result.result)

        # Streaming
        async for event in client.stream('Tell me a story'):
            if event.type == 'message':
                print(event.data)
        ```
    """

    def __init__(
        self,
        url: str,
        token: str,
        *,
        model: str = "claude-sonnet-4-5-20250929",
        system_prompt: Optional[str] = None,
        max_turns: Optional[int] = None,
        allowed_tools: Optional[List[str]] = None,
        disallowed_tools: Optional[List[str]] = None,
        mcp_servers: Optional[Dict[str, McpServer]] = None,
        timeout: float = 30.0,
        keepalive_interval: float = 60.0,
    ):
        """
        Initialize the Chucky client.

        Args:
            url: Chucky server WebSocket URL
            token: Billing token (JWT)
            model: Claude model to use
            system_prompt: Default system prompt
            max_turns: Maximum conversation turns
            allowed_tools: List of allowed tool names
            disallowed_tools: List of disallowed tool names
            mcp_servers: MCP servers with client-side tools
            timeout: Connection timeout in seconds
            keepalive_interval: Keep-alive interval in seconds
        """
        self.options = ChuckyOptions(
            url=url,
            token=token,
            model=model,
            system_prompt=system_prompt,
            max_turns=max_turns,
            allowed_tools=allowed_tools,
            disallowed_tools=disallowed_tools,
            mcp_servers=mcp_servers,
            timeout=timeout,
            keepalive_interval=keepalive_interval,
        )

        # Build tool handlers map from mcp_servers
        self._tool_handlers: Dict[str, ToolHandler] = {}
        if mcp_servers:
            for server in mcp_servers.values():
                for tool in server.tools:
                    self._tool_handlers[tool.name] = tool.handler

    async def prompt(
        self,
        message: str,
        *,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_turns: Optional[int] = None,
        tools: Optional[List[Tool]] = None,
    ) -> PromptResult:
        """
        Send a one-shot prompt and wait for the complete result.

        Args:
            message: The prompt message
            model: Override model for this prompt
            system_prompt: Override system prompt for this prompt
            max_turns: Maximum turns for this prompt
            tools: Additional tools for this prompt

        Returns:
            PromptResult with the final result and all messages
        """
        options = PromptOptions(
            model=model,
            system_prompt=system_prompt,
            max_turns=max_turns,
            tools=tools,
        )

        messages: List[SDKMessage] = []
        final_result: Optional[PromptResult] = None

        async for event in self.stream(message, options=options):
            if event.type == "message":
                messages.append(event.data)  # type: ignore
            elif event.type == "result":
                result_data = event.data
                final_result = PromptResult(
                    result=result_data.get("result", ""),  # type: ignore
                    messages=messages,
                    session_id=result_data.get("session_id", ""),  # type: ignore
                    total_cost_usd=result_data.get("total_cost_usd"),  # type: ignore
                    duration_ms=result_data.get("duration_ms"),  # type: ignore
                )

        if not final_result:
            raise RuntimeError("No result received from server")

        return final_result

    async def stream(
        self,
        message: str,
        *,
        options: Optional[PromptOptions] = None,
        debug: bool = False,
    ) -> AsyncIterator[StreamEvent]:
        """
        Send a prompt and stream events as they arrive.

        Args:
            message: The prompt message
            options: Prompt options

        Yields:
            StreamEvent objects as they arrive
        """
        options = options or PromptOptions()

        # Add tools from options to handlers
        if options.tools:
            for tool in options.tools:
                self._tool_handlers[tool.name] = tool.handler

        async with await self._connect() as ws:
            # Wait for ready signal
            await self._wait_for_ready(ws)

            # Send init with config
            init_payload = self._build_init_payload(options)
            await ws.send(json.dumps({"type": "init", "payload": init_payload}))

            # Send prompt
            prompt_options: Dict[str, Any] = {
                "model": options.model or self.options.model,
            }
            # Only include optional fields if they have values
            system_prompt = options.system_prompt or self.options.system_prompt
            if system_prompt:
                prompt_options["systemPrompt"] = system_prompt
            max_turns = options.max_turns or self.options.max_turns
            if max_turns:
                prompt_options["maxTurns"] = max_turns

            prompt_payload = {
                "message": message,
                "options": prompt_options,
            }
            await ws.send(json.dumps({"type": "prompt", "payload": prompt_payload}))

            # Process messages
            async for event in self._process_messages(ws, debug=debug):
                yield event

    async def _connect(self) -> WebSocketClientProtocol:
        """Create a WebSocket connection with token."""
        # Parse URL and add query params
        parsed = urlparse(self.options.url)
        query_params = {"token": self.options.token, "type": "prompt"}
        query_string = urlencode(query_params)

        # Reconstruct URL with query params
        if parsed.query:
            new_query = f"{parsed.query}&{query_string}"
        else:
            new_query = query_string

        url = urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment,
            )
        )

        return await asyncio.wait_for(
            websockets.connect(url),
            timeout=self.options.timeout,
        )

    async def _wait_for_ready(self, ws: WebSocketClientProtocol) -> None:
        """Wait for the 'ready' control message from server."""
        async def wait_for_ready_inner():
            async for raw_message in ws:
                data = json.loads(raw_message)
                if data.get("type") == "control":
                    payload = data.get("payload", {})
                    if payload.get("action") == "ready":
                        return
                elif data.get("type") == "error":
                    raise RuntimeError(data.get("payload", {}).get("message", "Unknown error"))

        try:
            await asyncio.wait_for(wait_for_ready_inner(), timeout=self.options.timeout)
        except asyncio.TimeoutError:
            raise RuntimeError("Timeout waiting for ready signal")

    async def _process_messages(
        self, ws: WebSocketClientProtocol,
        debug: bool = False,
    ) -> AsyncIterator[StreamEvent]:
        """Process incoming messages and yield events."""
        async for raw_message in ws:
            try:
                envelope = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            if debug:
                print(f"[DEBUG] Received: {json.dumps(envelope)[:200]}")

            msg_type = envelope.get("type")
            payload = envelope.get("payload", {})

            if msg_type == "sdk_message":
                sdk_message = payload

                if sdk_message.get("type") == "result":
                    yield StreamEvent(type="result", data=sdk_message)
                    yield StreamEvent(
                        type="done",
                        data={"sessionId": sdk_message.get("session_id", "")},
                    )
                    return
                else:
                    yield StreamEvent(type="message", data=sdk_message)

            elif msg_type == "tool_call":
                # Execute tool locally and send result back
                call_id = payload.get("callId")
                tool_name = payload.get("toolName")
                tool_input = payload.get("input", {})

                result = await self._execute_tool(tool_name, tool_input)
                await ws.send(
                    json.dumps(
                        {
                            "type": "tool_result",
                            "payload": {
                                "callId": call_id,
                                "result": {
                                    "content": result.content,
                                    "isError": result.is_error,
                                },
                            },
                        }
                    )
                )

            elif msg_type == "error":
                yield StreamEvent(type="error", data=payload)
                return

            elif msg_type == "control":
                if payload.get("action") == "close":
                    return

    async def _execute_tool(
        self, name: str, input_data: Dict[str, Any]
    ) -> ToolResult:
        """Execute a tool handler."""
        handler = self._tool_handlers.get(name)

        if not handler:
            return ToolResult(
                content=[{"type": "text", "text": f"Unknown tool: {name}"}],
                is_error=True,
            )

        try:
            result = handler(input_data)
            # Handle both sync and async handlers
            if asyncio.iscoroutine(result):
                result = await result
            return result  # type: ignore
        except Exception as e:
            return ToolResult(
                content=[{"type": "text", "text": f"Error: {str(e)}"}],
                is_error=True,
            )

    def _build_init_payload(self, options: PromptOptions) -> Dict[str, Any]:
        """Build init payload for WebSocket."""
        mcp_servers: List[Dict[str, Any]] = []

        # Convert mcp_servers to wire format
        if self.options.mcp_servers:
            for server in self.options.mcp_servers.values():
                mcp_servers.append(
                    {
                        "name": server.name,
                        "version": server.version,
                        "tools": [
                            {
                                "name": t.name,
                                "description": t.description,
                                "inputSchema": t.input_schema,
                                "executeIn": "browser",
                            }
                            for t in server.tools
                        ],
                    }
                )

        # Add any tools from options
        if options.tools:
            mcp_servers.append(
                {
                    "name": "inline-tools",
                    "version": "1.0.0",
                    "tools": [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.input_schema,
                            "executeIn": "browser",
                        }
                        for t in options.tools
                    ],
                }
            )

        payload: Dict[str, Any] = {
            "model": options.model or self.options.model,
        }

        if options.system_prompt or self.options.system_prompt:
            payload["systemPrompt"] = options.system_prompt or self.options.system_prompt
        if options.max_turns or self.options.max_turns:
            payload["maxTurns"] = options.max_turns or self.options.max_turns
        if self.options.allowed_tools:
            payload["allowedTools"] = self.options.allowed_tools
        if self.options.disallowed_tools:
            payload["disallowedTools"] = self.options.disallowed_tools
        if mcp_servers:
            payload["mcpServers"] = mcp_servers

        return payload
