"""
Preflights MCP Server.

Implements the MCP (Model Context Protocol) server for Claude Code integration.
Exposes 2 tools:
- require_clarification: Start/continue clarification sessions
- read_architecture: Read current architecture snapshot

Sessions are ephemeral per server lifetime.
MCP does NOT generate prompts (CLI responsibility).
"""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

from preflights.adapters.default_config import DefaultConfigLoader
from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
from preflights.adapters.fixed_clock import FixedClockProvider
from preflights.adapters.in_memory_session import InMemorySessionAdapter
from preflights.adapters.mock_llm import MockLLMAdapter
from preflights.adapters.sequential_uid import SequentialUIDProvider
from preflights.adapters.simple_file_context import SimpleFileContextBuilder
from preflights.application.preflights_app import PreflightsApp
from preflights.mcp.tools import MCPTools


def create_app(repo_path: str) -> PreflightsApp:
    """
    Create PreflightsApp with production adapters.

    Args:
        repo_path: Repository path for all operations

    Returns:
        Configured PreflightsApp instance
    """
    # Use real filesystem adapter (not fake/test)
    from pathlib import Path

    return PreflightsApp(
        session_adapter=InMemorySessionAdapter(),
        llm_adapter=MockLLMAdapter(),  # TODO: Replace with real LLM adapter
        filesystem_adapter=FakeFilesystemAdapter(Path(repo_path)),
        uid_provider=SequentialUIDProvider(),
        clock_provider=FixedClockProvider(),  # TODO: Replace with real clock
        file_context_builder=SimpleFileContextBuilder(),
        config_loader=DefaultConfigLoader(),
    )


def create_server(repo_path: str | None = None) -> Server:
    """
    Create MCP server with Preflights tools.

    Args:
        repo_path: Default repository path (defaults to current directory).
                   Individual tool calls can override with repo_path parameter.

    Returns:
        Configured MCP Server
    """
    default_repo_path = repo_path or os.getcwd()

    # Create app and tools
    app = create_app(default_repo_path)
    tools = MCPTools(app, default_repo_path)

    # Create MCP server
    server = Server("preflights")

    @server.list_tools()  # type: ignore[no-untyped-call,untyped-decorator]
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="require_clarification",
                description=(
                    "Start or continue a clarification session. "
                    "Forces clarification for ambiguous or structurally impactful requests. "
                    "Generates ADR and TASK artifacts when complete."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_intention": {
                            "type": "string",
                            "description": "The user's intention or request",
                        },
                        "optional_context": {
                            "type": "string",
                            "description": "Additional context for the request",
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to continue (omit to start new)",
                        },
                        "answers": {
                            "type": "object",
                            "description": "Answers to clarification questions",
                            "additionalProperties": True,
                        },
                        "preferences": {
                            "type": "object",
                            "description": "Preferences like force_adr",
                            "properties": {
                                "force_adr": {"type": "boolean"},
                            },
                        },
                        "repo_path": {
                            "type": "string",
                            "description": (
                                "Repository path (optional). "
                                "If not provided, discovers repo root from cwd by climbing to .git"
                            ),
                        },
                    },
                    "required": ["user_intention"],
                },
            ),
            Tool(
                name="read_architecture",
                description=(
                    "Read current architecture snapshot. "
                    "Returns the current state of architectural decisions."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": (
                                "Repository path (optional). "
                                "If not provided, discovers repo root from cwd by climbing to .git"
                            ),
                        },
                    },
                },
            ),
        ]

    @server.call_tool()  # type: ignore[untyped-decorator]
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        if name == "require_clarification":
            result = tools.require_clarification(
                user_intention=arguments.get("user_intention", ""),
                optional_context=arguments.get("optional_context"),
                session_id=arguments.get("session_id"),
                answers=arguments.get("answers"),
                preferences=arguments.get("preferences"),
                repo_path=arguments.get("repo_path"),
            )
            return [TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]

        elif name == "read_architecture":
            arch_result = tools.read_architecture(
                repo_path=arguments.get("repo_path"),
            )
            return [TextContent(type="text", text=json.dumps(arch_result.to_dict(), indent=2))]

        else:
            return [TextContent(type="text", text=json.dumps({
                "status": "error",
                "error": {
                    "code": "UNKNOWN_TOOL",
                    "message": f"Unknown tool: {name}",
                },
            }, indent=2))]

    return server


async def run_server(repo_path: str | None = None) -> None:
    """
    Run MCP server on stdio.

    Args:
        repo_path: Repository path (defaults to current directory)
    """
    server = create_server(repo_path)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Main entry point for MCP server."""
    import asyncio
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
