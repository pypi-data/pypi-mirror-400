"""Tool definition helpers for Chucky SDK."""

import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional, Type, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from .types import InputSchema, InputSchemaProperty, McpServer, Tool, ToolHandler, ToolResult


def text_result(text: str) -> ToolResult:
    """Create a simple text result."""
    return ToolResult(content=[{"type": "text", "text": text}])


def error_result(message: str) -> ToolResult:
    """Create an error result."""
    return ToolResult(content=[{"type": "text", "text": message}], is_error=True)


def _python_type_to_json_schema(py_type: Any) -> InputSchemaProperty:
    """Convert a Python type hint to JSON Schema property."""
    origin = get_origin(py_type)
    args = get_args(py_type)

    # Handle Optional[T] (Union[T, None])
    if origin is Union:
        non_none_args = [a for a in args if a is not type(None)]
        if len(non_none_args) == 1:
            # It's Optional[T]
            return _python_type_to_json_schema(non_none_args[0])
        # Complex union - default to string
        return {"type": "string"}

    # Handle Literal['a', 'b', 'c'] -> enum
    if origin is Literal:
        return {"type": "string", "enum": list(args)}

    # Handle List[T]
    if origin is list:
        return {"type": "array"}

    # Handle Dict
    if origin is dict:
        return {"type": "object"}

    # Handle basic types
    if py_type is str:
        return {"type": "string"}
    elif py_type is int:
        return {"type": "integer"}
    elif py_type is float:
        return {"type": "number"}
    elif py_type is bool:
        return {"type": "boolean"}
    else:
        # Default to string
        return {"type": "string"}


def _get_param_description(func: Callable, param_name: str) -> Optional[str]:
    """Extract parameter description from docstring."""
    docstring = func.__doc__
    if not docstring:
        return None

    # Simple parsing for Google/NumPy style docstrings
    lines = docstring.split("\n")
    in_args_section = False

    for line in lines:
        stripped = line.strip()
        if stripped.lower() in ("args:", "arguments:", "parameters:"):
            in_args_section = True
            continue
        if in_args_section:
            if stripped and not stripped.startswith(param_name):
                if ":" in stripped and not stripped.startswith(" "):
                    # New section or new param
                    if stripped.split(":")[0].strip() == param_name:
                        # Found it
                        return stripped.split(":", 1)[1].strip()
                    elif not stripped[0].isspace():
                        # New section, stop looking
                        break
            elif stripped.startswith(param_name):
                parts = stripped.split(":", 1)
                if len(parts) > 1:
                    return parts[1].strip()

    return None


def _extract_schema_from_function(func: Callable) -> InputSchema:
    """Extract JSON Schema from function signature and type hints."""
    sig = inspect.signature(func)
    hints = get_type_hints(func)

    properties: Dict[str, InputSchemaProperty] = {}
    required: List[str] = []

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        # Get type hint
        py_type = hints.get(param_name, str)
        prop = _python_type_to_json_schema(py_type)

        # Get description from docstring
        description = _get_param_description(func, param_name)
        if description:
            prop["description"] = description

        # Check if optional (has default)
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
        elif param.default is not None:
            prop["default"] = param.default

        properties[param_name] = prop

    schema: InputSchema = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required

    return schema


def _extract_schema_from_pydantic(model: Type[BaseModel]) -> InputSchema:
    """Extract JSON Schema from Pydantic model."""
    schema = model.model_json_schema()

    properties: Dict[str, InputSchemaProperty] = {}
    required: List[str] = schema.get("required", [])

    for name, prop in schema.get("properties", {}).items():
        json_prop: InputSchemaProperty = {"type": prop.get("type", "string")}
        if "description" in prop:
            json_prop["description"] = prop["description"]
        if "enum" in prop:
            json_prop["enum"] = prop["enum"]
        if "default" in prop:
            json_prop["default"] = prop["default"]
        properties[name] = json_prop

    return {
        "type": "object",
        "properties": properties,
        "required": required if required else None,
    }


def tool(
    name: str,
    description: str,
    *,
    schema: Optional[Union[Type[BaseModel], InputSchema]] = None,
) -> Callable[[ToolHandler], Tool]:
    """
    Decorator to create a tool from a function.

    The input schema can be:
    1. Automatically inferred from function signature and type hints
    2. Provided as a Pydantic model class
    3. Provided as a raw JSON Schema dict

    Examples:
        ```python
        from chucky import tool, text_result

        # Auto-infer from signature
        @tool("greet", "Greet someone by name")
        async def greet(name: str) -> ToolResult:
            return text_result(f"Hello, {name}!")

        # With Pydantic model
        class GreetInput(BaseModel):
            name: str
            style: Literal["formal", "casual"] = "casual"

        @tool("greet", "Greet someone by name", schema=GreetInput)
        async def greet(args: dict) -> ToolResult:
            return text_result(f"Hello, {args['name']}!")

        # With raw schema
        @tool("greet", "Greet someone", schema={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]
        })
        async def greet(args: dict) -> ToolResult:
            return text_result(f"Hello, {args['name']}!")
        ```
    """

    def decorator(func: ToolHandler) -> Tool:
        # Determine input schema
        if schema is None:
            # Auto-infer from function signature
            input_schema = _extract_schema_from_function(func)
        elif isinstance(schema, dict):
            # Raw JSON Schema
            input_schema = schema  # type: ignore
        elif inspect.isclass(schema) and issubclass(schema, BaseModel):
            # Pydantic model
            input_schema = _extract_schema_from_pydantic(schema)
        else:
            raise ValueError(f"Invalid schema type: {type(schema)}")

        # Wrap handler to accept dict and unpack to function args if needed
        @wraps(func)
        async def wrapper(args: Dict[str, Any]) -> ToolResult:
            # Check if function expects individual args or a dict
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            if len(params) == 1 and params[0] in ("args", "input", "data", "kwargs"):
                # Function expects a dict
                result = func(args)
            else:
                # Function expects individual args
                result = func(**args)

            # Handle both sync and async
            if inspect.iscoroutine(result):
                return await result
            return result  # type: ignore

        return Tool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=wrapper,
            execute_in="client",
        )

    return decorator


def create_mcp_server(
    name: str,
    tools: List[Tool],
    version: str = "1.0.0",
) -> McpServer:
    """
    Create an MCP server with tools.

    Example:
        ```python
        from chucky import create_mcp_server, tool, text_result

        @tool("greet", "Greet someone")
        async def greet(name: str) -> ToolResult:
            return text_result(f"Hello, {name}!")

        server = create_mcp_server("my-tools", [greet])

        client = Chucky(
            url='wss://...',
            token='...',
            mcp_servers={'my-tools': server}
        )
        ```
    """
    return McpServer(name=name, tools=tools, version=version)
