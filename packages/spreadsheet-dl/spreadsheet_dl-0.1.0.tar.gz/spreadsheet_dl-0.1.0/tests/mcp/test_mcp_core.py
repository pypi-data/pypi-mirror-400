"""
Tests for MCP server core classes.

Tests IR-MCP-002: Native MCP Server - Core Classes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spreadsheet_dl.mcp_server import (
    MCPCapabilities,
    MCPConfig,
    MCPSecurityError,
    MCPServer,
    MCPTool,
    MCPToolParameter,
    MCPToolRegistry,
    MCPToolResult,
    MCPVersion,
)

pytestmark = [pytest.mark.unit, pytest.mark.mcp]


class TestMCPVersion:
    """Tests for MCPVersion enum."""

    def test_mcp_version_v1(self) -> None:
        """Test MCP Version V1 value."""
        assert MCPVersion.V1.value == "2024-11-05"


class TestMCPCapabilities:
    """Tests for MCPCapabilities."""

    def test_default_capabilities(self) -> None:
        """Test default capabilities values."""
        caps = MCPCapabilities()
        assert caps.tools is True
        assert caps.resources is False
        assert caps.prompts is False
        assert caps.logging is True

    def test_custom_capabilities(self) -> None:
        """Test custom capabilities."""
        caps = MCPCapabilities(tools=False, resources=True, prompts=True, logging=False)
        assert caps.tools is False
        assert caps.resources is True
        assert caps.prompts is True
        assert caps.logging is False


class TestMCPConfig:
    """Tests for MCPConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = MCPConfig()

        assert config.name == "spreadsheet-dl"
        assert config.version == "1.0.0"
        assert config.rate_limit_per_minute == 60
        assert config.enable_audit_log is True
        assert config.audit_log_path is None

    def test_default_allowed_paths(self) -> None:
        """Test default allowed paths."""
        config = MCPConfig()

        # Should have some default paths
        assert len(config.allowed_paths) > 0
        assert Path.cwd() in config.allowed_paths

    def test_custom_allowed_paths(self) -> None:
        """Test custom allowed paths."""
        custom_paths = [Path("/tmp/test")]
        config = MCPConfig(allowed_paths=custom_paths)

        assert config.allowed_paths == custom_paths

    def test_custom_name(self) -> None:
        """Test custom server name."""
        config = MCPConfig(name="my-server")
        assert config.name == "my-server"

    def test_custom_version(self) -> None:
        """Test custom server version."""
        config = MCPConfig(version="2.0.0")
        assert config.version == "2.0.0"

    def test_custom_rate_limit(self) -> None:
        """Test custom rate limit."""
        config = MCPConfig(rate_limit_per_minute=100)
        assert config.rate_limit_per_minute == 100

    def test_audit_log_disabled(self) -> None:
        """Test audit logging disabled."""
        config = MCPConfig(enable_audit_log=False)
        assert config.enable_audit_log is False

    def test_audit_log_path(self) -> None:
        """Test custom audit log path."""
        log_path = Path("/var/log/mcp.log")
        config = MCPConfig(audit_log_path=log_path)
        assert config.audit_log_path == log_path


class TestMCPToolParameter:
    """Tests for MCPToolParameter."""

    def test_to_schema_basic(self) -> None:
        """Test basic schema generation."""
        param = MCPToolParameter(
            name="file_path",
            type="string",
            description="Path to file",
            required=True,
        )

        schema = param.to_schema()

        assert schema["type"] == "string"
        assert schema["description"] == "Path to file"

    def test_to_schema_with_enum(self) -> None:
        """Test schema with enum values."""
        param = MCPToolParameter(
            name="format",
            type="string",
            description="Output format",
            enum=["json", "text", "markdown"],
        )

        schema = param.to_schema()

        assert schema["enum"] == ["json", "text", "markdown"]

    def test_to_schema_with_default(self) -> None:
        """Test schema with default value."""
        param = MCPToolParameter(
            name="count",
            type="number",
            description="Number of items",
            required=False,
            default=10,
        )

        schema = param.to_schema()

        assert schema["default"] == 10

    def test_to_schema_no_enum_or_default(self) -> None:
        """Test schema without enum or default."""
        param = MCPToolParameter(
            name="value",
            type="string",
            description="A value",
            required=True,
        )

        schema = param.to_schema()

        assert "enum" not in schema
        assert "default" not in schema

    def test_default_required_true(self) -> None:
        """Test that required defaults to True."""
        param = MCPToolParameter(
            name="test",
            type="string",
            description="Test",
        )
        assert param.required is True

    def test_default_enum_none(self) -> None:
        """Test that enum defaults to None."""
        param = MCPToolParameter(
            name="test",
            type="string",
            description="Test",
        )
        assert param.enum is None

    def test_default_value_none(self) -> None:
        """Test that default value defaults to None."""
        param = MCPToolParameter(
            name="test",
            type="string",
            description="Test",
        )
        assert param.default is None


class TestMCPTool:
    """Tests for MCPTool."""

    def test_to_schema(self) -> None:
        """Test tool schema generation."""
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            parameters=[
                MCPToolParameter(
                    name="required_param",
                    type="string",
                    description="Required parameter",
                    required=True,
                ),
                MCPToolParameter(
                    name="optional_param",
                    type="number",
                    description="Optional parameter",
                    required=False,
                ),
            ],
        )

        schema = tool.to_schema()

        assert schema["name"] == "test_tool"
        assert schema["description"] == "A test tool"
        assert "required_param" in schema["inputSchema"]["properties"]
        assert "optional_param" in schema["inputSchema"]["properties"]
        assert "required_param" in schema["inputSchema"]["required"]
        assert "optional_param" not in schema["inputSchema"]["required"]

    def test_to_schema_no_parameters(self) -> None:
        """Test schema for tool with no parameters."""
        tool = MCPTool(
            name="simple_tool",
            description="A simple tool",
        )

        schema = tool.to_schema()

        assert schema["name"] == "simple_tool"
        assert schema["inputSchema"]["properties"] == {}
        assert schema["inputSchema"]["required"] == []

    def test_tool_with_handler(self) -> None:
        """Test tool with handler function."""

        def my_handler() -> MCPToolResult:
            return MCPToolResult.text("Hello")

        tool = MCPTool(
            name="handler_tool",
            description="Tool with handler",
            handler=my_handler,
        )

        assert tool.handler is not None
        result = tool.handler()
        assert result.content[0]["text"] == "Hello"


class TestMCPToolResult:
    """Tests for MCPToolResult."""

    def test_text_result(self) -> None:
        """Test text result creation."""
        result = MCPToolResult.text("Hello, world!")

        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert result.content[0]["text"] == "Hello, world!"
        assert result.is_error is False

    def test_json_result(self) -> None:
        """Test JSON result creation."""
        data = {"key": "value", "number": 42}
        result = MCPToolResult.json(data)

        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert '"key": "value"' in result.content[0]["text"]
        assert result.is_error is False

    def test_json_result_with_non_serializable(self) -> None:
        """Test JSON result with non-serializable types."""
        from datetime import date

        data = {"date": date(2025, 1, 15), "value": 100}
        result = MCPToolResult.json(data)

        # Should not raise, uses default=str
        assert "2025-01-15" in result.content[0]["text"]

    def test_error_result(self) -> None:
        """Test error result creation."""
        result = MCPToolResult.error("Something went wrong")

        assert len(result.content) == 1
        assert "Error:" in result.content[0]["text"]
        assert "Something went wrong" in result.content[0]["text"]
        assert result.is_error is True

    def test_direct_creation(self) -> None:
        """Test direct result creation."""
        result = MCPToolResult(
            content=[{"type": "text", "text": "Direct"}],
            is_error=False,
        )
        assert result.content[0]["text"] == "Direct"


class TestMCPToolRegistry:
    """Tests for MCPToolRegistry."""

    def test_registry_creation(self) -> None:
        """Test registry initialization."""
        registry = MCPToolRegistry()
        assert registry.get_tool_count() == 0

    def test_register_tool(self) -> None:
        """Test programmatic tool registration."""
        registry = MCPToolRegistry()

        def handler() -> MCPToolResult:
            return MCPToolResult.text("Test")

        registry.register(
            name="test_tool",
            description="A test tool",
            handler=handler,
            category="test",
        )

        assert registry.get_tool_count() == 1
        tool = registry.get_tool("test_tool")
        assert tool is not None
        assert tool.name == "test_tool"

    def test_register_with_decorator(self) -> None:
        """Test decorator-based tool registration."""
        registry = MCPToolRegistry()

        @registry.tool("decorated_tool", "A decorated tool", category="test")
        def my_tool() -> MCPToolResult:
            return MCPToolResult.text("Hello")

        assert registry.get_tool_count() == 1
        tool = registry.get_tool("decorated_tool")
        assert tool is not None
        assert tool.description == "A decorated tool"

    def test_get_all_tools(self) -> None:
        """Test getting all tools."""
        registry = MCPToolRegistry()

        def h1() -> MCPToolResult:
            return MCPToolResult.text("1")

        def h2() -> MCPToolResult:
            return MCPToolResult.text("2")

        registry.register("tool1", "Tool 1", h1)
        registry.register("tool2", "Tool 2", h2)

        tools = registry.get_all_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    def test_get_tools_by_category(self) -> None:
        """Test getting tools by category."""
        registry = MCPToolRegistry()

        def h() -> MCPToolResult:
            return MCPToolResult.text("x")

        registry.register("tool1", "Tool 1", h, category="cat_a")
        registry.register("tool2", "Tool 2", h, category="cat_a")
        registry.register("tool3", "Tool 3", h, category="cat_b")

        cat_a_tools = registry.get_tools_by_category("cat_a")
        assert len(cat_a_tools) == 2

        cat_b_tools = registry.get_tools_by_category("cat_b")
        assert len(cat_b_tools) == 1

    def test_get_tools_by_unknown_category(self) -> None:
        """Test getting tools by unknown category."""
        registry = MCPToolRegistry()
        tools = registry.get_tools_by_category("nonexistent")
        assert tools == []

    def test_get_categories(self) -> None:
        """Test getting all categories."""
        registry = MCPToolRegistry()

        def h() -> MCPToolResult:
            return MCPToolResult.text("x")

        registry.register("tool1", "Tool 1", h, category="cat_a")
        registry.register("tool2", "Tool 2", h, category="cat_b")

        categories = registry.get_categories()
        assert "cat_a" in categories
        assert "cat_b" in categories

    def test_list_tools(self) -> None:
        """Test listing all tools as schemas."""
        registry = MCPToolRegistry()

        def h() -> MCPToolResult:
            return MCPToolResult.text("x")

        registry.register("tool1", "Tool 1", h)
        registry.register("tool2", "Tool 2", h)

        schemas = registry.list_tools()
        assert len(schemas) == 2
        assert all("name" in s for s in schemas)
        assert all("description" in s for s in schemas)

    def test_get_nonexistent_tool(self) -> None:
        """Test getting non-existent tool returns None."""
        registry = MCPToolRegistry()
        assert registry.get_tool("nonexistent") is None

    def test_decorator_with_parameters(self) -> None:
        """Test decorator with parameters."""
        registry = MCPToolRegistry()

        @registry.tool(
            "param_tool",
            "Tool with params",
            parameters=[
                MCPToolParameter("input", "string", "Input value"),
            ],
        )
        def param_tool() -> MCPToolResult:
            return MCPToolResult.text("x")

        tool = registry.get_tool("param_tool")
        assert tool is not None
        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "input"


class TestMCPServer:
    """Tests for MCPServer."""

    @pytest.fixture
    def server(self, tmp_path: Path) -> MCPServer:
        """Create a test server."""
        config = MCPConfig(
            allowed_paths=[tmp_path, Path.cwd()],
        )
        return MCPServer(config)

    def test_registered_tools(self, server: MCPServer) -> None:
        """Test that standard tools are registered."""
        expected_tools = [
            "cell_get",
            "cell_set",
            "cell_clear",
            "style_apply",
            "row_insert",
            "column_insert",
            "sheet_create",
            "theme_list",
        ]

        for tool_name in expected_tools:
            assert tool_name in server._tools, f"Tool {tool_name} not registered"

    def test_handle_initialize(self, server: MCPServer) -> None:
        """Test initialize message handling."""
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
            },
        }

        response = server.handle_message(message)
        assert response is not None

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert "serverInfo" in response["result"]
        assert response["result"]["serverInfo"]["name"] == "spreadsheet-dl"

    def test_handle_initialized(self, server: MCPServer) -> None:
        """Test initialized notification handling."""
        message = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        # Should not raise, should return None (no response for notifications)
        response = server.handle_message(message)
        # Notifications don't require response
        assert response is None or "result" in response

    def test_handle_tools_list(self, server: MCPServer) -> None:
        """Test tools/list message handling."""
        message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        response = server.handle_message(message)
        assert response is not None

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) >= 8

        # Check tool schema format
        tool = response["result"]["tools"][0]
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool

    def test_handle_unknown_method(self, server: MCPServer) -> None:
        """Test unknown method handling."""
        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "unknown/method",
            "params": {},
        }

        response = server.handle_message(message)
        assert response is not None

        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "not found" in response["error"]["message"].lower()

    def test_handle_unknown_tool(self, server: MCPServer) -> None:
        """Test calling unknown tool."""
        message = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {},
            },
        }

        response = server.handle_message(message)
        assert response is not None

        assert "error" in response or response["result"]["isError"] is True

    def test_path_validation_allowed(self, server: MCPServer, tmp_path: Path) -> None:
        """Test path validation for allowed paths."""
        test_file = tmp_path / "test.ods"
        test_file.write_text("test")

        # Should not raise
        validated = server._validate_path(str(test_file))
        assert validated == test_file

    def test_path_validation_disallowed(self, server: MCPServer) -> None:
        """Test path validation for disallowed paths."""
        with pytest.raises(MCPSecurityError):
            server._validate_path("/etc/passwd")

    def test_rate_limiting(self, server: MCPServer) -> None:
        """Test rate limit checking."""
        # First request should pass
        assert server._check_rate_limit() is True

        # Simulate many requests
        server._request_count = server.config.rate_limit_per_minute

        # Next should fail
        assert server._check_rate_limit() is False

    def test_rate_limit_reset(self, server: MCPServer) -> None:
        """Test rate limit reset after time period."""
        from datetime import datetime, timedelta

        # Set high request count
        server._request_count = server.config.rate_limit_per_minute

        # Simulate time passing
        server._last_reset = datetime.now() - timedelta(minutes=2)

        # Should reset and pass
        assert server._check_rate_limit() is True
        assert server._request_count == 1
