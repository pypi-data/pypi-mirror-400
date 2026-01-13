# 04_advanced - Integration and Extension

Extend SpreadsheetDL with custom plugins and integrate with external systems.

## Prerequisites

- **Completed**: [03_charts](../03_charts/) - Data visualization
- **Skills needed**:
  - Advanced Python (classes, decorators, type hints)
  - Understanding of plugin architectures
  - Familiarity with MCP (Model Context Protocol) helpful
- **Time**: 60 minutes

## Learning Objectives

By completing these examples, you'll learn how to:

1. **Create custom plugins** - Extend SpreadsheetDL with domain-specific functionality
2. **Use plugin system** - Register and load plugins dynamically
3. **Integrate with MCP** - Connect to LLM tools and services
4. **Build MCP servers** - Create custom MCP servers for your domain
5. **Extend formulas** - Add new formula libraries
6. **Customize behavior** - Hook into SpreadsheetDL lifecycle events

## Examples in This Section

### 01_plugin_system.py

**What it does**: Demonstrates creating and using custom domain plugins

**Concepts covered**:

- Plugin interface implementation
- Domain-specific formula libraries
- Custom data models
- Plugin registration and discovery
- Namespace management
- Plugin lifecycle hooks

**Run it**:

```bash
uv run python examples/04_advanced/01_plugin_system.py
```

**Expected output**: Spreadsheet using custom plugin formulas

**Creates a custom "Real Estate" domain plugin**:

```python
from spreadsheet_dl.plugin import DomainPlugin, register_plugin

@register_plugin("real_estate")
class RealEstatePlugin(DomainPlugin):
    """Custom plugin for real estate calculations."""

    def get_formulas(self):
        return [
            MortgagePayment,
            CapitalizationRate,
            CashOnCashReturn,
            # ... more custom formulas
        ]

    def get_models(self):
        return [Property, Investment, Rental]
```

---

### 02_mcp_basics.py

**What it does**: Introduction to Model Context Protocol (MCP) integration

**Concepts covered**:

- MCP client setup
- Connecting to MCP servers
- Calling MCP tools
- Spreadsheet generation via MCP
- Error handling with MCP
- Authentication and configuration

**Run it**:

```bash
uv run python examples/04_advanced/02_mcp_basics.py
```

**Expected output**: Spreadsheet created via MCP tool calls

**MCP integration**:

```python
from spreadsheet_dl.mcp import MCPClient

# Connect to MCP server
client = MCPClient("http://localhost:3000")

# Call spreadsheet generation tool
result = client.call_tool(
    "create_budget",
    month=1,
    year=2025,
    categories=["groceries", "transportation"]
)

# Result contains ODS file path
print(f"Created: {result['output_path']}")
```

---

### 03_mcp_server_usage.py

**What it does**: Build and run a custom MCP server for SpreadsheetDL

**Concepts covered**:

- MCP server architecture
- Tool registration and handlers
- Request/response patterns
- Server configuration
- Deployment considerations
- LLM integration patterns

**Run it**:

```bash
# First, start the MCP server
uv run python examples/04_advanced/03_mcp_server_usage.py --serve

# Then, in another terminal, test it
uv run python examples/04_advanced/03_mcp_server_usage.py --test
```

**Expected output**:

- MCP server running on configured port
- Test client successfully creates spreadsheets via server

**Server structure**:

```python
from spreadsheet_dl.mcp.server import MCPServer, tool

server = MCPServer(name="budget-server")

@server.tool("create_budget")
def create_budget_tool(month: int, year: int) -> dict:
    """MCP tool for budget creation."""
    generator = OdsGenerator()
    path = generator.create_budget_spreadsheet(...)
    return {"output_path": str(path)}

# Run server
server.run(host="localhost", port=3000)
```

---

## Key Concepts

### Plugin System

Create reusable domain-specific extensions:

```python
from spreadsheet_dl.plugin import DomainPlugin, register_plugin
from spreadsheet_dl.formulas import BaseFormula

# Define custom formulas
@dataclass
class MyFormula(BaseFormula):
    """Custom formula implementation."""

    @property
    def metadata(self) -> FormulaMetadata:
        return FormulaMetadata(
            name="MY_FORMULA",
            category="Custom",
            description="Does custom calculation",
            # ... metadata
        )

    def build(self, *args, **kwargs) -> str:
        return f"of:=CUSTOM_CALC({args[0]};{args[1]})"

# Create plugin
@register_plugin("my_domain")
class MyDomainPlugin(DomainPlugin):
    def get_formulas(self):
        return [MyFormula]

    def get_models(self):
        return []  # Optional data models

# Use plugin
from spreadsheet_dl import load_plugin

plugin = load_plugin("my_domain")
formulas = plugin.get_formulas()
```

### MCP Integration

Connect to LLM-powered tools:

```python
from spreadsheet_dl.mcp import MCPClient, MCPConfig

# Configure client
config = MCPConfig(
    server_url="http://localhost:3000",
    api_key="optional-key",
    timeout=30
)

client = MCPClient(config)

# List available tools
tools = client.list_tools()
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Call a tool
result = client.call_tool(
    "create_spreadsheet",
    template="budget",
    month=1,
    year=2025
)

# Handle response
if result.success:
    print(f"Created: {result.data['path']}")
else:
    print(f"Error: {result.error}")
```

### Custom MCP Server

Build your own MCP server:

```python
from spreadsheet_dl.mcp.server import MCPServer, tool, MCPToolResult

server = MCPServer(
    name="my-spreadsheet-server",
    version="1.0.0",
    description="Custom spreadsheet generation server"
)

@server.tool(
    name="generate_report",
    description="Generate custom report spreadsheet"
)
def generate_report(
    data: list[dict],
    format: str = "ods"
) -> MCPToolResult:
    """Generate report from data."""
    try:
        # Your custom logic
        generator = OdsGenerator()
        path = generator.create_from_data(data)

        return MCPToolResult(
            success=True,
            data={"path": str(path), "format": format}
        )
    except Exception as e:
        return MCPToolResult(
            success=False,
            error=str(e)
        )

# Run server
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=3000)
```

### Plugin Discovery

Load plugins dynamically:

```python
from spreadsheet_dl.plugin import discover_plugins, load_plugin

# Auto-discover installed plugins
plugins = discover_plugins()
print(f"Found {len(plugins)} plugins")

# Load specific plugin
finance = load_plugin("finance")
formulas = finance.get_formulas()

# Use plugin formulas
from spreadsheet_dl.domains.finance.formulas import PresentValue

pv = PresentValue()
formula_str = pv.build(rate=0.05, nper=10, pmt=-100)
# -> "of:=PV(0.05;10;-100;0;0)"
```

## Advanced Patterns

### Custom Formula Registry

Extend the formula system:

```python
from spreadsheet_dl.formulas import FormulaRegistry

registry = FormulaRegistry()

# Register formula
registry.register("MY_CALC", MyCustomFormula)

# Lookup formula
formula_class = registry.get("MY_CALC")
formula = formula_class()

# List all formulas
all_formulas = registry.list_all()
```

### Plugin Configuration

Configure plugins with settings:

```python
from spreadsheet_dl.plugin import PluginConfig

config = PluginConfig(
    enabled=True,
    settings={
        "precision": 2,
        "currency": "USD",
        "date_format": "YYYY-MM-DD"
    }
)

plugin = load_plugin("finance", config=config)
```

### Event Hooks

Hook into SpreadsheetDL lifecycle:

```python
from spreadsheet_dl.hooks import on_before_generate, on_after_generate

@on_before_generate
def validate_data(context):
    """Validate data before generation."""
    if not context.expenses:
        raise ValueError("No expenses provided")

@on_after_generate
def post_process(context, result):
    """Post-process generated file."""
    print(f"Generated: {result.path}")
    # Could add: email notification, cloud upload, etc.
```

## Estimated Time

- **Quick review**: 15 minutes (read concepts)
- **Run examples**: 20 minutes
- **Build custom plugin**: 60 minutes (hands-on)

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'spreadsheet_dl.plugin'`
**Solution**: Ensure you have the latest version of SpreadsheetDL with plugin support

**Issue**: Plugin not discovered
**Solution**: Check plugin is properly decorated with `@register_plugin` and installed in Python path

**Issue**: MCP connection refused
**Solution**: Ensure MCP server is running before client connects:

```bash
# Terminal 1: Start server
uv run python examples/04_advanced/03_mcp_server_usage.py --serve

# Terminal 2: Run client
uv run python examples/04_advanced/02_mcp_basics.py
```

**Issue**: Custom formula not working
**Solution**: Verify formula inherits from `BaseFormula` and implements `metadata` property and `build()` method

**Issue**: Type errors with plugin
**Solution**: Ensure proper type hints and implement all required DomainPlugin methods

## Security Considerations

### Plugin Security

- **Validate inputs**: Always validate data in plugin methods
- **Sanitize formulas**: Prevent formula injection attacks
- **Restrict imports**: Only import trusted modules in plugins
- **Review code**: Audit third-party plugins before use

```python
def build(self, *args, **kwargs) -> str:
    # GOOD: Validate inputs
    if not all(isinstance(arg, (int, float)) for arg in args):
        raise ValueError("Invalid argument types")

    # GOOD: Sanitize
    safe_value = str(args[0]).replace(";", "")

    return f"of:=CALC({safe_value})"
```

### MCP Security

- **Use authentication**: Require API keys for production servers
- **Rate limiting**: Prevent abuse with rate limits
- **Input validation**: Validate all MCP tool parameters
- **HTTPS only**: Use encrypted connections in production

```python
from spreadsheet_dl.mcp.server import MCPServer, require_auth

server = MCPServer(name="secure-server")

@server.tool("generate_report")
@require_auth  # Require authentication
def generate_report(data: dict) -> MCPToolResult:
    # Validate inputs
    if not data:
        return MCPToolResult(success=False, error="No data provided")

    # Process securely...
```

## Best Practices

1. **Version your plugins**:

   ```python
   class MyPlugin(DomainPlugin):
       version = "1.0.0"
   ```

2. **Document formulas thoroughly**:

   ```python
   FormulaMetadata(
       description="Detailed description of what this does",
       examples=["Example 1", "Example 2"]
   )
   ```

3. **Test plugins extensively**:

   ```python
   def test_my_formula():
       formula = MyFormula()
       result = formula.build(arg1=10, arg2=20)
       assert "CALC(10;20)" in result
   ```

4. **Handle errors gracefully**:

   ```python
   try:
       result = plugin.process(data)
   except PluginError as e:
       logger.error(f"Plugin error: {e}")
       # Fallback logic
   ```

## Next Steps

You've completed the learning path! Here are some advanced topics to explore:

1. **Build a production plugin** - Package and distribute your own domain plugin
2. **Create an MCP server** - Deploy a server for your organization
3. **Contribute to SpreadsheetDL** - Add formulas to the core library
4. **Integrate with your stack** - Connect SpreadsheetDL to your existing tools

## Additional Resources

- [Plugin Development Guide](../../docs/guides/plugin-development.md)
- [MCP Server Documentation](../../docs/api/_mcp/server.md)
- [Formula Development Guide](../../docs/guides/formula-development.md)
- [API Reference](../../docs/api/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

## Contributing

Want to contribute a plugin or formula? See:

- [CONTRIBUTING.md](../../CONTRIBUTING.md)
- [Plugin Guidelines](../../docs/guides/plugin-development.md)
- [Formula Guidelines](../../docs/guides/formula-development.md)

## Questions?

- Check the plugin development guide
- Review MCP documentation
- Open an issue on GitHub
- Join the community discussions
