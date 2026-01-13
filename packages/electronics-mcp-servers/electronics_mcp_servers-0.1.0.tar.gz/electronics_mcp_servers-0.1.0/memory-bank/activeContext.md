# Active Context

## Current Focus
- Planning and designing three MCP servers for electronics/embedded development
- Researching FastMCP framework and MCP server patterns
- Creating project structure and implementation plan

## Open Questions / Blockers
- None currently - research phase complete

## Notes
### Research Summary: FastMCP Framework
FastMCP is the recommended Python framework for building MCP servers. Key features:
- Simple `@mcp.tool` decorator for registering tools
- Automatic JSON schema generation from type hints
- Docstrings become tool descriptions
- Support for async/sync functions
- Multiple transport options (STDIO, HTTP, SSE)

### Key Patterns Learned
1. **Tool Registration**: Use `@mcp.tool` decorator on functions
2. **Type Hints**: Required for automatic schema generation
3. **Docstrings**: Used as tool descriptions for LLMs
4. **Return Types**: Support for primitives, dicts, lists, and custom types
5. **Error Handling**: Return descriptive error strings or raise exceptions

### Reference MCP Servers Studied
- **mcp-server-time**: Time/timezone conversions (good pattern for calculations)
- **mcp-server-fetch**: Web content fetching (good error handling)
- **mcp-server-git**: Git operations (good multi-tool structure)
- **mcp-server-everything**: Feature showcase (comprehensive example)

---
*Last Updated: 2026-01-05*
