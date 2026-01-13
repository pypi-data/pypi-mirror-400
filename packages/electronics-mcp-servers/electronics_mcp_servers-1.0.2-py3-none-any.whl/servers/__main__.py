# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Samuel F.
"""
Electronics MCP Server - Combined Entry Point
"""
from servers.combined_server import mcp

def main():
    """Main entry point for the combined electronics MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
