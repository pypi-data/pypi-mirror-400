"""Chucky SDK client implementation.

Matches the official Claude Agent SDK V2 interface.
"""

import asyncio
import json
from typing import Any, AsyncIterator, Dict, List, Optional, Union
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


def get_assistant_text(message: Dict[str, Any]) -> str:
    """Extract text from an assistant message."""
    content = message.get("message", {}).get("content", [])
    return "".join(
        block.get("text", "")
        for block in content
        if block.get("type") == "text"
    )


def get_result_text(message: Dict[str, Any]) -> Optional[str]:
    """Extract result text from a result message."""
    if message.get("subtype") == "success":
        return message.get("result")
    return None


class Session:
    """
    Session class - matches official V2 SDK interface.

    Usage:
        ```python
        session = client.create_session(model='claude-sonnet-4-5-20250929')

        await session.send('What is 5 + 3?')
        async for msg in session.stream():
            if msg.get('type') == 'result':
                print(msg.get('result'))

        await session.send('Multiply that by 2')
        async for msg in session.stream():
            if msg.get('type') == 'result':
                print(msg.get('result'))

        session.close()
        ```
    """

    def __init__(
        self,
        options: ChuckyOptions,
        session_options: Optional[PromptOptions] = None,
        debug: bool = False,
    ):
        self.options = options
        self.session_options = session_options or PromptOptions()
        self.debug = debug

        self._session_id: str = ""
        self._connected = False
        self._connect_lock = asyncio.Lock()
        self._ws: Optional[WebSocketClientProtocol] = None
        self._message_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._receive_task: Optional[asyncio.Task] = None

        # Build tool handlers map
        self._tool_handlers: Dict[str, ToolHandler] = {}
        if options.mcp_servers:
            for server in options.mcp_servers.values():
                for tool in server.tools:
                    self._tool_handlers[tool.name] = tool.handler
        if session_options and session_options.tools:
            for tool in session_options.tools:
                self._tool_handlers[tool.name] = tool.handler

    @property
    def session_id(self) -> str:
        return self._session_id

    async def _ensure_connected(self) -> None:
        """Connect if not already connected."""
        if self._connected:
            return

        async with self._connect_lock:
            if self._connected:
                return
            await self._connect()

    async def _connect(self) -> None:
        """Create WebSocket connection and initialize session."""
        # Build URL with token
        parsed = urlparse(self.options.url)
        query_params = {"token": self.options.token, "type": "prompt"}
        query_string = urlencode(query_params)

        if parsed.query:
            new_query = f"{parsed.query}&{query_string}"
        else:
            new_query = query_string

        url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))

        self._ws = await asyncio.wait_for(
            websockets.connect(url),
            timeout=self.options.timeout,
        )

        # Wait for ready signal
        await self._wait_for_ready()

        # Send init with config
        init_payload = self._build_init_payload()
        await self._ws.send(json.dumps({"type": "init", "payload": init_payload}))

        self._connected = True

        # Start background message receiver
        self._receive_task = asyncio.create_task(self._receive_messages())

    async def _wait_for_ready(self) -> None:
        """Wait for the 'ready' control message from server."""
        if not self._ws:
            raise RuntimeError("Not connected")

        async def wait_for_ready_inner():
            async for raw_message in self._ws:  # type: ignore
                data = json.loads(raw_message)
                if self.debug:
                    print(f"[DEBUG] Received: {json.dumps(data)[:200]}")
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

    async def _receive_messages(self) -> None:
        """Background task to receive messages and put them in queue."""
        if not self._ws:
            return

        try:
            async for raw_message in self._ws:
                try:
                    envelope = json.loads(raw_message)
                except json.JSONDecodeError:
                    continue

                if self.debug:
                    print(f"[DEBUG] Received: {json.dumps(envelope)[:200]}")

                msg_type = envelope.get("type")
                payload = envelope.get("payload", {})

                if msg_type == "sdk_message":
                    await self._message_queue.put(payload)

                elif msg_type in ("user", "assistant", "result", "system"):
                    # Direct SDK message (not wrapped in sdk_message)
                    await self._message_queue.put(envelope)

                elif msg_type == "tool_call":
                    # Execute tool locally and send result back
                    call_id = payload.get("callId")
                    tool_name = payload.get("toolName")
                    tool_input = payload.get("input", {})

                    result = await self._execute_tool(tool_name, tool_input)
                    await self._ws.send(json.dumps({
                        "type": "tool_result",
                        "payload": {
                            "callId": call_id,
                            "result": {
                                "content": result.content,
                                "isError": result.is_error,
                            },
                        },
                    }))

                elif msg_type == "error":
                    await self._message_queue.put({"type": "error", "error": payload})

                elif msg_type == "control":
                    if payload.get("action") == "close":
                        break

        except websockets.exceptions.ConnectionClosed:
            pass

    async def _execute_tool(self, name: str, input_data: Dict[str, Any]) -> ToolResult:
        """Execute a tool handler."""
        handler = self._tool_handlers.get(name)

        if not handler:
            return ToolResult(
                content=[{"type": "text", "text": f"Unknown tool: {name}"}],
                is_error=True,
            )

        try:
            result = handler(input_data)
            if asyncio.iscoroutine(result):
                result = await result
            return result  # type: ignore
        except Exception as e:
            return ToolResult(
                content=[{"type": "text", "text": f"Error: {str(e)}"}],
                is_error=True,
            )

    def _build_init_payload(self) -> Dict[str, Any]:
        """Build init payload for WebSocket."""
        mcp_servers: List[Dict[str, Any]] = []

        if self.options.mcp_servers:
            for server in self.options.mcp_servers.values():
                mcp_servers.append({
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
                })

        if self.session_options.tools:
            mcp_servers.append({
                "name": "inline-tools",
                "version": "1.0.0",
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.input_schema,
                        "executeIn": "browser",
                    }
                    for t in self.session_options.tools
                ],
            })

        payload: Dict[str, Any] = {
            "model": self.session_options.model or self.options.model,
        }

        system_prompt = self.session_options.system_prompt or self.options.system_prompt
        if system_prompt:
            payload["systemPrompt"] = system_prompt
        max_turns = self.session_options.max_turns or self.options.max_turns
        if max_turns:
            payload["maxTurns"] = max_turns
        if self.options.allowed_tools:
            payload["allowedTools"] = self.options.allowed_tools
        if self.options.disallowed_tools:
            payload["disallowedTools"] = self.options.disallowed_tools
        if mcp_servers:
            payload["mcpServers"] = mcp_servers

        return payload

    async def send(self, message: str) -> None:
        """
        Send a message to the session.

        Matches V2 SDK: send() returns None.
        Use stream() to get the response.

        Example:
            ```python
            await session.send('Hello!')
            async for msg in session.stream():
                # Handle messages
            ```
        """
        await self._ensure_connected()

        if not self._ws:
            raise RuntimeError("Not connected")

        # Clear any previous messages
        while not self._message_queue.empty():
            try:
                self._message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        prompt_options: Dict[str, Any] = {
            "model": self.session_options.model or self.options.model,
        }
        system_prompt = self.session_options.system_prompt or self.options.system_prompt
        if system_prompt:
            prompt_options["systemPrompt"] = system_prompt
        max_turns = self.session_options.max_turns or self.options.max_turns
        if max_turns:
            prompt_options["maxTurns"] = max_turns

        prompt_payload = {
            "message": message,
            "options": prompt_options,
        }
        await self._ws.send(json.dumps({"type": "prompt", "payload": prompt_payload}))

    async def stream(self) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream the response after sending a message.

        Matches V2 SDK: Returns AsyncIterator of SDK messages.

        Example:
            ```python
            await session.send('Hello!')
            async for msg in session.stream():
                if msg.get('type') == 'assistant':
                    text = get_assistant_text(msg)
                    print(text)
                if msg.get('type') == 'result':
                    print('Done:', msg.get('result'))
            ```
        """
        while True:
            try:
                msg = await asyncio.wait_for(
                    self._message_queue.get(),
                    timeout=300.0,  # 5 minute timeout
                )
                yield msg

                # Stop on result or error
                if msg.get("type") in ("result", "error"):
                    break

            except asyncio.TimeoutError:
                break

    async def receive(self) -> AsyncIterator[Dict[str, Any]]:
        """Receive messages (alias for stream for V2 compatibility)."""
        async for msg in self.stream():
            yield msg

    async def close(self) -> None:
        """Close the session."""
        if self._receive_task:
            self._receive_task.cancel()
            self._receive_task = None

        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        self._connected = False


class Chucky:
    """
    Chucky SDK Client - matches official V2 SDK interface.

    Example:
        ```python
        from chucky import Chucky

        client = Chucky(
            url='wss://conjure.chucky.cloud/ws',
            token='your-jwt-token',
        )

        # V2 style: create session, send, stream
        session = client.create_session(model='claude-sonnet-4-5-20250929')

        await session.send('Hello!')
        async for msg in session.stream():
            if msg.get('type') == 'assistant':
                print(get_assistant_text(msg))
            if msg.get('type') == 'result':
                print('Done:', msg.get('result'))

        session.close()

        # Or use one-shot prompt
        result = await client.prompt('What is 2 + 2?')
        print(result.get('result'))
        ```
    """

    def __init__(
        self,
        url: str = "wss://conjure.chucky.cloud/ws",
        token: str = "",
        *,
        model: str = "claude-sonnet-4-5-20250929",
        system_prompt: Optional[str] = None,
        max_turns: Optional[int] = None,
        allowed_tools: Optional[List[str]] = None,
        disallowed_tools: Optional[List[str]] = None,
        mcp_servers: Optional[Dict[str, McpServer]] = None,
        timeout: float = 30.0,
        keepalive_interval: float = 60.0,
        debug: bool = False,
    ):
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
        self.debug = debug
        self._active_sessions: List[Session] = []

    def create_session(
        self,
        *,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_turns: Optional[int] = None,
        tools: Optional[List[Tool]] = None,
    ) -> Session:
        """
        Create a new session.

        Matches V2 SDK: create_session() returns Session immediately.
        Connection happens automatically on first send().

        Example:
            ```python
            session = client.create_session(
                model='claude-sonnet-4-5-20250929',
                system_prompt='You are helpful.',
            )

            await session.send('Hello!')
            async for msg in session.stream():
                # Handle messages
            ```
        """
        session_options = PromptOptions(
            model=model,
            system_prompt=system_prompt,
            max_turns=max_turns,
            tools=tools,
        )

        session = Session(
            options=self.options,
            session_options=session_options,
            debug=self.debug,
        )
        self._active_sessions.append(session)
        return session

    async def prompt(
        self,
        message: str,
        *,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_turns: Optional[int] = None,
        tools: Optional[List[Tool]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a one-shot prompt.

        Matches V2 SDK: prompt(message, options) returns result message.

        Example:
            ```python
            result = await client.prompt(
                'Explain quantum computing',
                model='claude-sonnet-4-5-20250929'
            )
            if result.get('subtype') == 'success':
                print(result.get('result'))
            ```
        """
        session = self.create_session(
            model=model,
            system_prompt=system_prompt,
            max_turns=max_turns,
            tools=tools,
        )

        try:
            await session.send(message)

            result = None
            async for msg in session.stream():
                if msg.get("type") == "result":
                    result = msg
                    break

            if not result:
                raise RuntimeError("No result message received")

            return result
        finally:
            await session.close()

    async def close(self) -> None:
        """Close all active sessions."""
        for session in self._active_sessions:
            await session.close()
        self._active_sessions.clear()

    # Legacy API compatibility
    async def stream(
        self,
        message: str,
        *,
        options: Optional[PromptOptions] = None,
        debug: bool = False,
    ) -> AsyncIterator[StreamEvent]:
        """
        Legacy streaming API for backwards compatibility.

        Prefer using create_session() + send() + stream() for V2 style.
        """
        session = self.create_session(
            model=options.model if options else None,
            system_prompt=options.system_prompt if options else None,
            max_turns=options.max_turns if options else None,
            tools=options.tools if options else None,
        )

        try:
            await session.send(message)

            async for msg in session.stream():
                msg_type = msg.get("type")

                if msg_type == "result":
                    yield StreamEvent(type="result", data=msg)
                    yield StreamEvent(
                        type="done",
                        data={"sessionId": msg.get("session_id", "")},
                    )
                    return
                elif msg_type == "error":
                    yield StreamEvent(type="error", data=msg)
                    return
                else:
                    yield StreamEvent(type="message", data=msg)
        finally:
            await session.close()
