"""
Preflights MCP Server.

Provides MCP (Model Context Protocol) tools for Claude Code integration:
- require_clarification: Start/continue clarification sessions
- read_architecture: Read current architecture snapshot

Note: MCP does NOT generate prompts. That's CLI/UX responsibility.
"""

from preflights.mcp.server import create_server, run_server

__all__ = ["create_server", "run_server"]
