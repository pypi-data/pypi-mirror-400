"""MCP data models.

Part of the modular MCP server implementation.
Defines tool parameters, tool definitions, and tool results.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class MCPToolParameter:
    """Definition of a tool parameter."""

    name: str
    type: str
    description: str
    required: bool = True
    enum: list[str] | None = None
    default: Any = None

    def to_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema format."""
        schema: dict[str, Any] = {
            "type": self.type,
            "description": self.description,
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass
class MCPTool:
    """Definition of an MCP tool."""

    name: str
    description: str
    parameters: list[MCPToolParameter] = field(default_factory=list)
    handler: Callable[..., Any] | None = None

    def to_schema(self) -> dict[str, Any]:
        """Convert to MCP tool schema format."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }


@dataclass
class MCPToolResult:
    """Result of a tool execution."""

    content: list[dict[str, Any]]
    is_error: bool = False

    @classmethod
    def text(cls, text: str) -> MCPToolResult:
        """Create a text result."""
        return cls(content=[{"type": "text", "text": text}])

    @classmethod
    def json(cls, data: Any) -> MCPToolResult:
        """Create a JSON result."""
        return cls(
            content=[
                {
                    "type": "text",
                    "text": json.dumps(data, indent=2, default=str),
                }
            ]
        )

    @classmethod
    def error(cls, message: str) -> MCPToolResult:
        """Create an error result."""
        return cls(
            content=[{"type": "text", "text": f"Error: {message}"}],
            is_error=True,
        )
