# MCP Server Research Notes

## FastMCP Framework Overview

### Installation
```bash
pip install fastmcp
# or
uv add fastmcp
```

### Basic Server Structure
```python
from fastmcp import FastMCP

mcp = FastMCP("Server Name")

@mcp.tool
def my_tool(param: str) -> str:
    """Tool description for LLM."""
    return f"Result: {param}"

if __name__ == "__main__":
    mcp.run()  # Default: STDIO transport
```

### Key Features
1. **@mcp.tool decorator** - Registers functions as MCP tools
2. **Automatic schema generation** - Type hints → JSON schema
3. **Docstring as description** - LLMs see the docstring
4. **Multiple transports** - STDIO, HTTP, SSE
5. **Context injection** - Access to MCP capabilities via `Context` parameter

### Tool Decorator Options
```python
@mcp.tool(
    name="custom_name",           # Override function name
    description="Custom desc",     # Override docstring
    tags={"category", "type"},     # For filtering
    meta={"version": "1.0"}        # Custom metadata
)
def my_tool(x: int) -> int:
    return x * 2
```

### Return Types
- **Primitives**: `int`, `str`, `float`, `bool` → wrapped in `{"result": value}`
- **Dicts/Lists**: Returned as-is in `structured_content`
- **ToolResult**: Full control over output

### Error Handling Patterns
```python
@mcp.tool
def safe_tool(x: int) -> str:
    if x < 0:
        return "✗ Error: Value must be non-negative"
    return f"✓ Result: {x}"
```

---

## Official MCP Server Patterns

### mcp-server-time (Python)
**Location:** `modelcontextprotocol/servers/src/time`

**Pattern Highlights:**
- Enum for tool names: `class TimeTools(str, Enum)`
- Pydantic models for structured responses
- Clean `@server.list_tools()` and `@server.call_tool()` handlers
- Local timezone detection with override option

**Tools:**
1. `get_current_time(timezone: str)` → TimeResult
2. `convert_time(source_tz, time, target_tz)` → TimeConversionResult

### mcp-server-fetch (Python)
**Location:** `modelcontextprotocol/servers/src/fetch`

**Pattern Highlights:**
- Pydantic models for input validation
- Robots.txt compliance
- Content truncation with pagination
- User-agent configuration

### mcp-server-git (Python)
**Location:** `modelcontextprotocol/servers/src/git`

**Pattern Highlights:**
- Multiple related tools (status, diff, commit, log, etc.)
- Repository path handling
- Pydantic models for each tool's input schema

### mcp-server-everything (TypeScript)
**Location:** `modelcontextprotocol/servers/src/everything`

**Pattern Highlights:**
- Comprehensive feature showcase
- Multi-transport support
- Server factory pattern
- Resource subscriptions

---

## Project-Specific Patterns

### Resistor Color Code Decoder
**Data Structure:**
```python
COLOR_VALUES = {
    "Black": 0, "Brown": 1, "Red": 2, "Orange": 3,
    "Yellow": 4, "Green": 5, "Blue": 6, "Violet": 7,
    "Grey": 8, "White": 9
}

MULTIPLIERS = {
    "Black": 1, "Brown": 10, "Red": 100, "Orange": 1000,
    "Yellow": 10000, "Green": 100000, "Blue": 1000000,
    "Gold": 0.1, "Silver": 0.01
}

TOLERANCES = {
    "Brown": "±1%", "Red": "±2%", "Green": "±0.5%",
    "Blue": "±0.25%", "Violet": "±0.1%", "Grey": "±0.05%",
    "Gold": "±5%", "Silver": "±10%"
}
```

**E-Series Standard Values:**
```python
E12_VALUES = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E24_VALUES = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
              3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
```

### Capacitor Calculator
**Key Formulas:**
```python
# Capacitive Reactance
Xc = 1 / (2 * π * f * C)

# RC Time Constant
τ = R * C

# Resonant Frequency
f = 1 / (2 * π * √(L * C))

# Filter Cutoff Frequency
fc = 1 / (2 * π * R * C)
# Therefore: C = 1 / (2 * π * R * fc)
```

### GPIO Pin Reference
**Database Structure:**
```python
PIN_DATABASE = {
    "ESP32": {
        0: {
            "name": "GPIO0",
            "features": ["Bootstrap", "ADC2_1", "Touch1"],
            "notes": "Must be HIGH during boot"
        },
        # ... more pins
    },
    "Arduino UNO": {
        0: {"name": "D0/RX", "features": ["UART_RX"]},
        # ... more pins
    }
}
```

---

## Running MCP Servers

### Development
```bash
# With FastMCP CLI
fastmcp run server.py

# Direct Python
python server.py

# With uv
uv run server.py
```

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "resistor-decoder": {
      "command": "python",
      "args": ["/path/to/resistor_decoder.py"]
    }
  }
}
```

### VS Code Configuration
```json
{
  "servers": {
    "resistor-decoder": {
      "command": "python",
      "args": ["${workspaceFolder}/resistor_decoder.py"]
    }
  }
}
```

---

## Best Practices Summary

1. **Clear Tool Names**: Use descriptive, action-oriented names
2. **Comprehensive Docstrings**: LLMs rely on these for understanding
3. **Type Hints Everywhere**: Required for schema generation
4. **Human-Readable Output**: Include units, symbols, formatting
5. **Error Messages**: Start with ✗ for errors, ✓ for success
6. **Unit Formatting**: Auto-detect best unit (Ω, kΩ, MΩ)
7. **Validation**: Check inputs before processing
8. **Examples in Docstrings**: Help LLMs understand usage
