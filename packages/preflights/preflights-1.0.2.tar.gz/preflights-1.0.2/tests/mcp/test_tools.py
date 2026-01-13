"""Tests for MCP tools."""

from __future__ import annotations

from pathlib import Path

import pytest

from preflights.adapters.default_config import DefaultConfigLoader
from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
from preflights.adapters.fixed_clock import FixedClockProvider
from preflights.adapters.in_memory_session import InMemorySessionAdapter
from preflights.adapters.mock_llm import MockLLMAdapter
from preflights.adapters.sequential_uid import SequentialUIDProvider
from preflights.adapters.simple_file_context import SimpleFileContextBuilder
from preflights.application.preflights_app import PreflightsApp
from preflights.mcp.tools import MCPTools
from preflights.mcp.types import (
    CompletedResult,
    ErrorResult,
    NeedsClarificationResult,
)


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Create a temporary repository with .git directory."""
    # Create .git directory (required for repo discovery)
    (tmp_path / ".git").mkdir()
    # Create minimal structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "auth").mkdir()
    (tmp_path / "src" / "auth" / "login.ts").write_text("// Login")
    return tmp_path


@pytest.fixture
def app(tmp_repo: Path) -> PreflightsApp:
    """Create PreflightsApp with test adapters."""
    return PreflightsApp(
        session_adapter=InMemorySessionAdapter(),
        llm_adapter=MockLLMAdapter(),
        filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
        uid_provider=SequentialUIDProvider(),
        clock_provider=FixedClockProvider(),
        file_context_builder=SimpleFileContextBuilder(),
        config_loader=DefaultConfigLoader(),
    )


@pytest.fixture
def tools(app: PreflightsApp, tmp_repo: Path) -> MCPTools:
    """Create MCPTools instance."""
    return MCPTools(app, str(tmp_repo))


class TestRequireClarification:
    """Tests for require_clarification tool."""

    def test_start_new_session(self, tools: MCPTools) -> None:
        """Starting new session returns needs_clarification."""
        result = tools.require_clarification(
            user_intention="Add OAuth authentication",
        )

        assert isinstance(result, NeedsClarificationResult)
        assert result.status == "needs_clarification"
        assert result.session_id != ""
        assert len(result.questions) > 0
        assert result.progress is not None
        assert result.progress.asked_so_far > 0
        assert result.progress.answered == 0

    def test_continue_session_with_answers(self, tools: MCPTools) -> None:
        """Continuing session with answers progresses correctly."""
        # Start session
        start_result = tools.require_clarification(
            user_intention="Add OAuth authentication",
        )
        assert isinstance(start_result, NeedsClarificationResult)
        session_id = start_result.session_id

        # Answer questions
        answers = {}
        for q in start_result.questions:
            if q.options:
                answers[q.id] = q.options[0]
            else:
                answers[q.id] = "test answer"

        # Continue
        result = tools.require_clarification(
            user_intention="Add OAuth authentication",
            session_id=session_id,
            answers=answers,
        )

        # Should complete or need more clarification
        assert result.status in ("completed", "needs_clarification", "needs_more_answers")

    def test_complete_flow(self, tools: MCPTools) -> None:
        """Full clarification flow reaches completed status."""
        # Start session
        result = tools.require_clarification(
            user_intention="Add OAuth authentication",
        )
        assert isinstance(result, NeedsClarificationResult)
        session_id = result.session_id

        # Answer all questions until completed (max 10 turns)
        turns = 0
        while isinstance(result, NeedsClarificationResult) and turns < 10:
            answers = {}
            for q in result.questions:
                if q.options:
                    answers[q.id] = q.options[0]
                else:
                    answers[q.id] = "test answer"

            result = tools.require_clarification(
                user_intention="Add OAuth authentication",
                session_id=session_id,
                answers=answers,
            )
            turns += 1

        # Should eventually complete
        assert isinstance(result, CompletedResult), f"Expected completed, got {result.status}"
        assert result.status == "completed"
        assert len(result.artifacts_created) > 0

    def test_completed_has_task_artifact(self, tools: MCPTools) -> None:
        """Completed result includes task artifact."""
        # Run full flow
        result = tools.require_clarification(user_intention="Add OAuth authentication")
        assert isinstance(result, NeedsClarificationResult)
        session_id = result.session_id

        turns = 0
        while isinstance(result, NeedsClarificationResult) and turns < 10:
            answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = tools.require_clarification(
                user_intention="Add OAuth authentication",
                session_id=session_id,
                answers=answers,
            )
            turns += 1

        assert isinstance(result, CompletedResult)
        task_artifacts = [a for a in result.artifacts_created if a.type == "task"]
        assert len(task_artifacts) == 1
        assert task_artifacts[0].path == "docs/CURRENT_TASK.md"

    def test_completed_has_adr_for_auth(self, tools: MCPTools) -> None:
        """Auth intention produces ADR artifact."""
        # Run full flow
        result = tools.require_clarification(user_intention="Add OAuth authentication")
        assert isinstance(result, NeedsClarificationResult)
        session_id = result.session_id

        turns = 0
        while isinstance(result, NeedsClarificationResult) and turns < 10:
            answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = tools.require_clarification(
                user_intention="Add OAuth authentication",
                session_id=session_id,
                answers=answers,
            )
            turns += 1

        assert isinstance(result, CompletedResult)
        adr_artifacts = [a for a in result.artifacts_created if a.type == "adr"]
        assert len(adr_artifacts) == 1
        assert adr_artifacts[0].uid is not None

    def test_error_on_unknown_session(self, tools: MCPTools) -> None:
        """Unknown session_id returns error."""
        result = tools.require_clarification(
            user_intention="Add OAuth",
            session_id="unknown-session-id",
            answers={"q1": "a"},
        )

        assert isinstance(result, ErrorResult)
        assert result.status == "error"
        assert result.error is not None
        assert result.error.code == "SESSION_NOT_FOUND"

    def test_questions_have_required_fields(self, tools: MCPTools) -> None:
        """Questions in response have all required fields."""
        result = tools.require_clarification(user_intention="Add OAuth")

        assert isinstance(result, NeedsClarificationResult)
        for q in result.questions:
            assert q.id != ""
            assert q.type in ("single_choice", "multi_choice", "free_text")
            assert q.question != ""

    def test_to_dict_serializable(self, tools: MCPTools) -> None:
        """Result can be serialized to dict."""
        result = tools.require_clarification(user_intention="Add OAuth")

        assert isinstance(result, NeedsClarificationResult)
        d = result.to_dict()
        assert "status" in d
        assert "session_id" in d
        assert "questions" in d


class TestReadArchitecture:
    """Tests for read_architecture tool."""

    def test_no_architecture_returns_empty(self, tools: MCPTools) -> None:
        """No architecture file returns empty with uid: null."""
        result = tools.read_architecture()

        assert result.status == "success"
        assert result.architecture["uid"] is None
        assert result.architecture["categories"] == {}

    def test_reads_existing_architecture(self, tools: MCPTools, tmp_repo: Path) -> None:
        """Reads existing architecture state file."""
        # Create architecture state file
        docs_dir = tmp_repo / "docs"
        docs_dir.mkdir(exist_ok=True)
        arch_file = docs_dir / "ARCHITECTURE_STATE.md"
        arch_file.write_text("""<!-- UID: 20250106T120000.000Z-A000 -->
<!-- Schema: v1 -->

# Architecture State

Current architecture decisions snapshot.

## Categories

### Authentication
- **Strategy**: OAuth
- **Library**: next-auth
""")

        result = tools.read_architecture()

        assert result.status == "success"
        assert result.architecture["uid"] == "20250106T120000.000Z-A000"
        assert "Authentication" in result.architecture["categories"]
        assert result.architecture["categories"]["Authentication"]["Strategy"] == "OAuth"

    def test_to_dict_serializable(self, tools: MCPTools) -> None:
        """Result can be serialized to dict."""
        result = tools.read_architecture()

        d = result.to_dict()
        assert "status" in d
        assert "architecture" in d
        assert "source_file" in d


class TestMCPTypesSerialize:
    """Tests for MCP type serialization."""

    def test_needs_clarification_to_dict(self) -> None:
        """NeedsClarificationResult serializes correctly."""
        from preflights.mcp.types import MCPProgress, MCPQuestion

        result = NeedsClarificationResult(
            session_id="sess-123",
            questions=[
                MCPQuestion(
                    id="q1",
                    type="single_choice",
                    question="Choose one",
                    options=["A", "B"],
                )
            ],
            progress=MCPProgress(asked_so_far=1, answered=0),
        )

        d = result.to_dict()
        assert d["status"] == "needs_clarification"
        assert d["session_id"] == "sess-123"
        assert len(d["questions"]) == 1
        assert d["questions"][0]["id"] == "q1"
        assert d["progress"]["asked_so_far"] == 1

    def test_completed_to_dict(self) -> None:
        """CompletedResult serializes correctly."""
        from preflights.mcp.types import MCPArtifact

        result = CompletedResult(
            artifacts_created=[
                MCPArtifact(path="docs/CURRENT_TASK.md", type="task"),
                MCPArtifact(path="docs/adr/20250106_auth.md", type="adr", uid="20250106T120000.000Z"),
            ],
            summary="Done",
        )

        d = result.to_dict()
        assert d["status"] == "completed"
        assert len(d["artifacts_created"]) == 2
        assert d["artifacts_created"][0]["type"] == "task"
        assert d["artifacts_created"][1]["uid"] == "20250106T120000.000Z"

    def test_error_to_dict(self) -> None:
        """ErrorResult serializes correctly."""
        from preflights.mcp.types import MCPError

        result = ErrorResult(
            error=MCPError(
                code="TEST_ERROR",
                message="Test message",
                details={"key": "value"},
                recovery_hint="Try again",
            )
        )

        d = result.to_dict()
        assert d["status"] == "error"
        assert d["error"]["code"] == "TEST_ERROR"
        assert d["error"]["message"] == "Test message"
        assert d["error"]["details"]["key"] == "value"
        assert d["error"]["recovery_hint"] == "Try again"
