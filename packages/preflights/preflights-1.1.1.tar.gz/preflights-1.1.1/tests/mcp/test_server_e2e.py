"""E2E tests for MCP server via stdio subprocess."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import pytest_asyncio

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


@pytest_asyncio.fixture(loop_scope="function")
async def mcp_session_with_path(tmp_path: Path) -> tuple[ClientSession, Path]:
    """Start MCP server and return connected client session with repo path."""
    import anyio
    from typing import AsyncGenerator

    # Create .git directory (required for repo discovery)
    (tmp_path / ".git").mkdir()
    # Create minimal repo structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("# main")

    # Server params
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "preflights.mcp.server"],
        cwd=str(tmp_path),
    )

    # Use explicit async context managers with proper cleanup
    read_stream = None
    write_stream = None
    session = None

    try:
        client_ctx = stdio_client(server_params)
        read_stream, write_stream = await client_ctx.__aenter__()

        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()

        # Initialize
        await session.initialize()
        yield session, tmp_path
    finally:
        # Clean up in reverse order, ignoring errors
        if session is not None:
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass  # Ignore cleanup errors
        if client_ctx is not None:
            try:
                await client_ctx.__aexit__(None, None, None)
            except Exception:
                pass  # Ignore cleanup errors


@pytest_asyncio.fixture(loop_scope="function")
async def mcp_session(mcp_session_with_path: tuple[ClientSession, Path]) -> ClientSession:
    """Start MCP server and return connected client session."""
    session, _ = mcp_session_with_path
    return session


@pytest.mark.asyncio
class TestMCPServerE2E:
    """E2E tests for MCP server."""

    async def test_server_starts_and_initializes(self, mcp_session: ClientSession) -> None:
        """Server starts and completes MCP handshake."""
        # If we got here, initialization succeeded
        assert mcp_session is not None

    async def test_tools_list(self, mcp_session: ClientSession) -> None:
        """Server lists available tools."""
        result = await mcp_session.list_tools()
        tool_names = [t.name for t in result.tools]

        assert "require_clarification" in tool_names
        assert "read_architecture" in tool_names
        assert len(result.tools) == 2

    async def test_require_clarification_start(self, mcp_session: ClientSession) -> None:
        """require_clarification starts a new session."""
        result = await mcp_session.call_tool(
            "require_clarification",
            {"user_intention": "Add OAuth authentication"},
        )

        assert len(result.content) == 1
        data = json.loads(result.content[0].text)  # type: ignore[union-attr]

        assert data["status"] == "needs_clarification"
        assert "session_id" in data
        assert len(data["questions"]) > 0

    async def test_read_architecture_empty(self, mcp_session: ClientSession) -> None:
        """read_architecture returns empty for new repo."""
        result = await mcp_session.call_tool("read_architecture", {})

        data = json.loads(result.content[0].text)  # type: ignore[union-attr]

        assert data["status"] == "success"
        assert data["architecture"]["uid"] is None
        assert data["architecture"]["categories"] == {}

    async def test_full_clarification_flow(self, mcp_session: ClientSession) -> None:
        """Complete clarification flow produces artifacts."""
        # Start session
        r1 = await mcp_session.call_tool(
            "require_clarification",
            {"user_intention": "Add OAuth authentication"},
        )
        result = json.loads(r1.content[0].text)  # type: ignore[union-attr]
        session_id = result["session_id"]

        # Answer questions until completed (max 10 turns)
        turns = 0
        while result["status"] != "completed" and turns < 10:
            # Build answers
            answers = {}
            for q in result.get("questions", []):
                if q.get("options"):
                    answers[q["id"]] = q["options"][0]
                else:
                    answers[q["id"]] = "test answer"

            # Continue session
            r = await mcp_session.call_tool(
                "require_clarification",
                {
                    "user_intention": "Add OAuth authentication",
                    "session_id": session_id,
                    "answers": answers,
                },
            )
            result = json.loads(r.content[0].text)  # type: ignore[union-attr]
            turns += 1

        # Should complete
        assert result["status"] == "completed", f"Expected completed, got {result['status']}"
        assert len(result["artifacts_created"]) > 0

        # Should have task artifact
        task_artifacts = [a for a in result["artifacts_created"] if a["type"] == "task"]
        assert len(task_artifacts) == 1

    async def test_unknown_tool_returns_error(self, mcp_session: ClientSession) -> None:
        """Unknown tool name returns error."""
        result = await mcp_session.call_tool("unknown_tool", {})

        data = json.loads(result.content[0].text)  # type: ignore[union-attr]

        assert data["status"] == "error"
        assert data["error"]["code"] == "UNKNOWN_TOOL"

    async def test_unknown_session_returns_error(self, mcp_session: ClientSession) -> None:
        """Unknown session_id returns error."""
        result = await mcp_session.call_tool(
            "require_clarification",
            {
                "user_intention": "test",
                "session_id": "unknown-session-id",
                "answers": {"q1": "a"},
            },
        )

        data = json.loads(result.content[0].text)  # type: ignore[union-attr]

        assert data["status"] == "error"
        assert data["error"]["code"] == "SESSION_NOT_FOUND"
        assert "recovery_hint" in data["error"]

    async def test_files_created_on_completion(
        self, mcp_session_with_path: tuple[ClientSession, Path]
    ) -> None:
        """Verify CURRENT_TASK.md and AGENT_PROMPT.md exist after completion."""
        mcp_session, tmp_path = mcp_session_with_path

        # Start session
        r1 = await mcp_session.call_tool(
            "require_clarification",
            {"user_intention": "Add OAuth authentication"},
        )
        result = json.loads(r1.content[0].text)  # type: ignore[union-attr]
        session_id = result["session_id"]

        # Answer all questions until completed
        turns = 0
        while result["status"] != "completed" and turns < 10:
            answers = {}
            for q in result.get("questions", []):
                if q.get("options"):
                    answers[q["id"]] = q["options"][0]
                else:
                    answers[q["id"]] = "test answer"

            r = await mcp_session.call_tool(
                "require_clarification",
                {
                    "user_intention": "Add OAuth authentication",
                    "session_id": session_id,
                    "answers": answers,
                },
            )
            result = json.loads(r.content[0].text)  # type: ignore[union-attr]
            turns += 1

        # Verify completion
        assert result["status"] == "completed"

        # Verify files exist
        task_file = tmp_path / "docs" / "CURRENT_TASK.md"
        assert task_file.exists(), f"CURRENT_TASK.md not found at {task_file}"

        agent_prompt_file = tmp_path / "docs" / "AGENT_PROMPT.md"
        assert agent_prompt_file.exists(), f"AGENT_PROMPT.md not found at {agent_prompt_file}"

        # Verify task content has expected structure (markdown with UID header)
        task_content = task_file.read_text()
        assert "<!-- UID:" in task_content, "Task should have UID comment"
        assert "## Objective" in task_content or "## OBJECTIVE" in task_content.upper()

        # Verify agent prompt has expected structure
        prompt_content = agent_prompt_file.read_text()
        assert "docs/CURRENT_TASK.md" in prompt_content, "Agent prompt should reference CURRENT_TASK.md"
