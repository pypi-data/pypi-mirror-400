"""Benchmarks for MCP tool dispatch performance.

Target: <100ms for 1000 calls (from current ~200ms baseline)
Goal: 2x improvement through pre-compiled dispatch and caching

    - PERF-MCP-001: Tool dispatch optimization
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl._mcp.models import MCPToolParameter
from spreadsheet_dl._mcp.registry import MCPToolRegistry

if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

pytestmark = [pytest.mark.benchmark, pytest.mark.mcp]


class TestMCPDispatchBenchmarks:
    """Benchmark tests for MCP tool dispatch performance."""

    def test_tool_registration_overhead(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark tool registration overhead.

        Measures decorator registration time for 100 tools.
        """

        def register_tools() -> MCPToolRegistry:
            registry = MCPToolRegistry()

            # Register 100 tools
            for i in range(100):

                @registry.tool(  # type: ignore[arg-type]
                    name=f"test_tool_{i}",
                    description=f"Test tool {i}",
                    category="test",
                    parameters=[
                        MCPToolParameter(
                            name="param1",
                            type="string",
                            description="First parameter",
                            required=True,
                        ),
                        MCPToolParameter(
                            name="param2",
                            type="number",
                            description="Second parameter",
                            required=False,
                        ),
                    ],
                )
                def tool_func(param1: str, param2: int = 0) -> dict[str, str]:
                    return {"result": f"{param1}_{param2}"}

            return registry

        registry = benchmark(register_tools)
        assert registry.get_tool_count() == 100

    def test_tool_lookup_performance(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark tool lookup performance.

        Target: <100ms for 1000 lookups
        Current baseline: ~200ms

        Implements: PERF-MCP-001
        """
        # Setup: Create registry with tools
        registry = MCPToolRegistry()

        for i in range(100):

            @registry.tool(  # type: ignore[arg-type]
                name=f"tool_{i}",
                description=f"Tool {i}",
            )
            def tool_func() -> dict[str, str]:
                return {"result": "ok"}

        # Benchmark: Look up tools 1000 times
        def lookup_tools() -> int:
            count = 0
            for _ in range(1000):
                tool = registry.get_tool("tool_50")
                if tool:
                    count += 1
            return count

        result = benchmark(lookup_tools)
        assert result == 1000

    def test_tool_execution_dispatch(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark tool execution dispatch.

        Measures end-to-end dispatch time including handler invocation.
        """
        registry = MCPToolRegistry()

        @registry.tool(  # type: ignore[arg-type]
            name="add",
            description="Add two numbers",
            parameters=[
                MCPToolParameter(
                    name="a", type="number", description="First number", required=True
                ),
                MCPToolParameter(
                    name="b", type="number", description="Second number", required=True
                ),
            ],
        )
        def add_tool(a: int, b: int) -> dict[str, int]:
            return {"result": a + b}

        # Benchmark: Execute tool 1000 times
        def execute_tool() -> int:
            total = 0
            for i in range(1000):
                tool = registry.get_tool("add")
                if tool and tool.handler:
                    result = tool.handler(a=i, b=1)
                    total += result["result"]
            return total

        result = benchmark(execute_tool)
        assert result > 0

    def test_category_lookup_performance(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark category-based tool lookup.

        Tests performance of filtering tools by category.
        """
        registry = MCPToolRegistry()

        # Create tools across 10 categories
        categories = [
            "cell",
            "style",
            "format",
            "sheet",
            "chart",
            "data",
            "import",
            "export",
            "query",
            "admin",
        ]

        for category in categories:
            for i in range(10):

                @registry.tool(  # type: ignore[arg-type]
                    name=f"{category}_tool_{i}",
                    description=f"{category} tool {i}",
                    category=category,
                )
                def tool_func() -> dict[str, str]:
                    return {"result": "ok"}

        # Benchmark: Get tools by category
        def get_by_category() -> int:
            total = 0
            for _ in range(100):
                for category in categories:
                    tools = registry.get_tools_by_category(category)
                    total += len(tools)
            return total

        result = benchmark(get_by_category)
        assert result == 10000  # 100 iterations * 10 categories * 10 tools per category

    def test_list_all_tools_performance(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark listing all tools with metadata.

        Tests schema generation performance.
        """
        registry = MCPToolRegistry()

        # Register 50 tools with full metadata
        for i in range(50):

            @registry.tool(  # type: ignore[arg-type]
                name=f"tool_{i}",
                description=f"Tool {i} with parameters",
                category=f"category_{i % 5}",
                parameters=[
                    MCPToolParameter(
                        name="param1",
                        type="string",
                        description="Parameter 1",
                        required=True,
                    ),
                    MCPToolParameter(
                        name="param2",
                        type="number",
                        description="Parameter 2",
                        required=False,
                    ),
                ],
            )
            def tool_func(param1: str, param2: int = 0) -> dict[str, str]:
                return {"result": "ok"}

        # Benchmark: List all tools
        def list_tools() -> int:
            total = 0
            for _ in range(100):
                schemas = registry.list_tools()
                total += len(schemas)
            return total

        result = benchmark(list_tools)
        assert result == 5000  # 100 iterations * 50 tools

    def test_bulk_tool_registration(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark programmatic bulk tool registration.

        Tests non-decorator registration path.
        """

        def bulk_register() -> MCPToolRegistry:
            registry = MCPToolRegistry()

            def generic_handler(x: int) -> dict[str, int]:
                return {"result": x * 2}

            # Register 100 tools programmatically
            for i in range(100):
                registry.register(
                    name=f"bulk_tool_{i}",
                    description=f"Bulk tool {i}",
                    handler=generic_handler,  # type: ignore[arg-type]
                    parameters=[
                        MCPToolParameter(
                            name="x",
                            type="number",
                            description="Input value",
                            required=True,
                        )
                    ],
                    category="bulk",
                )

            return registry

        registry = benchmark(bulk_register)
        assert registry.get_tool_count() == 100
