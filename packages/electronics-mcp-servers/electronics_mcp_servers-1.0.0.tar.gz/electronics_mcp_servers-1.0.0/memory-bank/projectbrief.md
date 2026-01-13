# Project Brief

## Goal
Build three educational MCP (Model Context Protocol) servers for electronics/embedded development practice:
1. **GPIO Pin Reference MCP** - Query GPIO pin information for various development boards
2. **Capacitor Calculator MCP** - Calculate capacitive reactance, RC time constants, and resonant frequencies
3. **Resistor Color Code Decoder MCP** - Decode and encode resistor color bands

## Constraints
- Use **FastMCP** framework (Python) for rapid development
- Keep each server simple and focused (< 200 lines per server)
- Follow MCP best practices from official documentation
- Support multiple boards (ESP32, Arduino UNO, STM32) for GPIO server
- Include comprehensive color code mappings for 4-band and 5-band resistors
- Provide accurate electrical calculations with proper unit formatting

## Stakeholders
- Developer (learning MCP server development)
- Claude/AI assistants (end users of the tools)
- Hardware engineers (beneficiaries of the tools)

## Definition of Done
- [ ] All three MCP servers are functional and tested
- [ ] Each server can be run standalone via `fastmcp run` or `python -m`
- [ ] Tools return properly formatted, human-readable results
- [ ] Comprehensive error handling for invalid inputs
- [ ] Documentation for each server's tools and usage

---
*Created: 2026-01-05 | Last Updated: 2026-01-05*
