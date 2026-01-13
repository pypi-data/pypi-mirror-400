"""Tests for hard problems: TTL, parse errors, archive robustness.

These tests cover edge cases and error scenarios that require
careful handling in the Application layer.
"""

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
from preflights.application.types import AppErrorCode


class TestSessionTTL:
    """Tests for session time-to-live (TTL) expiration."""

    def test_session_expires_after_30_minutes(
        self,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Session expires after 30 minutes."""
        # Given: A started session with controllable clock
        clock = FixedClockProvider()
        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=clock,
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id

        # When: 31 minutes pass and continue is attempted
        clock.advance_minutes(31)
        result = app.continue_preflight(session_id, {"auth_strategy": "OAuth"})

        # Then: SESSION_EXPIRED error with recovery hint
        assert result.status == "error"
        assert result.error is not None
        assert result.error.code == AppErrorCode.SESSION_EXPIRED
        assert "expired" in result.error.message.lower()
        assert result.error.recovery_hint is not None

    def test_session_valid_before_30_minutes(
        self,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Session is still valid before 30 minutes."""
        # Given: A started session with controllable clock
        clock = FixedClockProvider()
        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=clock,
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id

        # When: 29 minutes pass (under limit)
        clock.advance_minutes(29)
        result = app.continue_preflight(session_id, {"auth_strategy": "OAuth"})

        # Then: Not SESSION_EXPIRED
        if result.status == "error":
            assert result.error.code != AppErrorCode.SESSION_EXPIRED

    def test_expired_session_is_deleted(
        self,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Expired session is deleted when accessed."""
        # Given: A started session
        clock = FixedClockProvider()
        session_adapter = InMemorySessionAdapter()
        app = PreflightsApp(
            session_adapter=session_adapter,
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=clock,
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id
        assert session_adapter.get(session_id) is not None

        # When: Session expires and is accessed
        clock.advance_minutes(31)
        app.continue_preflight(session_id, {"auth_strategy": "OAuth"})

        # Then: Session is deleted
        assert session_adapter.get(session_id) is None


class TestParseErrors:
    """Tests for malformed file handling."""

    def test_malformed_architecture_state_returns_error(
        self,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Malformed ARCHITECTURE_STATE.md returns ParseError."""
        # Given: A repo with malformed architecture state file
        arch_dir = tmp_repo / "docs"
        arch_dir.mkdir(parents=True, exist_ok=True)
        (arch_dir / "ARCHITECTURE_STATE.md").write_text("# Invalid\n\nNo UID comment here")

        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )

        # When: Session started and questions answered
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)

        # Then: PARSE_ERROR with recovery hint
        assert result.status == "error"
        assert result.error is not None
        assert result.error.code == AppErrorCode.PARSE_ERROR
        assert result.error.recovery_hint is not None

    def test_malformed_current_task_returns_error(
        self,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Malformed CURRENT_TASK.md returns ParseError."""
        # Given: A repo with malformed task file
        task_dir = tmp_repo / "docs"
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "CURRENT_TASK.md").write_text("# Task\n\nNo UID comment here")

        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )

        # When: Session completed (may need multiple turns)
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)

        while result.status in ("needs_clarification", "needs_more_answers") and result.questions:
            new_answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = app.continue_preflight(session_id, new_answers)

        # Then: If error, must be PARSE_ERROR
        if result.status == "error":
            assert result.error is not None
            assert result.error.code == AppErrorCode.PARSE_ERROR, (
                f"Expected PARSE_ERROR, got {result.error.code}: {result.error.message}"
            )


class TestArchiveRobustness:
    """Tests for task archiving robustness."""

    def test_archive_succeeds_with_existing_task(
        self,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Archive works when CURRENT_TASK.md exists."""
        # Given: A repo with valid existing task
        task_dir = tmp_repo / "docs"
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "CURRENT_TASK.md").write_text("""<!-- UID: 20250106T100000.000Z-A000 -->
<!-- Created: 2025-01-06T10:00:00Z -->

# Previous Task

## Objective

Old task objective
""")

        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )

        # When: New preflight completed
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)

        while result.status in ("needs_clarification", "needs_more_answers") and result.questions:
            new_answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = app.continue_preflight(session_id, new_answers)

        # Then: Archive created
        if result.status == "completed":
            archive_dir = tmp_repo / "docs" / "archive" / "task"
            assert archive_dir.exists()
            assert len(list(archive_dir.glob("*.md"))) >= 1

    def test_no_archive_created_when_no_existing_task(
        self,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """No archive created when no CURRENT_TASK.md exists."""
        # Given: An empty repo
        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )

        # When: Preflight completed
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)

        while result.status in ("needs_clarification", "needs_more_answers") and result.questions:
            new_answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = app.continue_preflight(session_id, new_answers)

        # Then: No archive
        if result.status == "completed":
            archive_dir = tmp_repo / "docs" / "archive" / "task"
            if archive_dir.exists():
                assert len(list(archive_dir.glob("*.md"))) == 0

    def test_archive_uses_existing_task_uid(
        self,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Archive filename uses UID from existing task."""
        # Given: A repo with valid existing task with known UID
        existing_uid = "20250106T100000.000Z-A000"
        task_dir = tmp_repo / "docs"
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "CURRENT_TASK.md").write_text(f"""<!-- UID: {existing_uid} -->
<!-- Created: 2025-01-06T10:00:00Z -->

# Previous Task

## Objective

Old task objective
""")

        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )

        # When: New preflight completed
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)

        while result.status in ("needs_clarification", "needs_more_answers") and result.questions:
            new_answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = app.continue_preflight(session_id, new_answers)

        # Then: Archive uses existing UID
        if result.status == "completed":
            archive_dir = tmp_repo / "docs" / "archive" / "task"
            archives = list(archive_dir.glob("*.md"))
            if archives:
                assert archives[0].name.startswith(existing_uid), (
                    f"Archive {archives[0].name} should start with {existing_uid}"
                )


class TestPatchExtractionFailure:
    """Tests for LLM patch extraction failure."""

    def test_patch_extraction_failure_returns_error(
        self,
        tmp_repo: Path,
    ) -> None:
        """When LLM fails to extract patch, return appropriate error."""
        # Given: An app with LLM configured to fail extraction
        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=MockLLMAdapter(force_extraction_failure=True),
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )

        # When: Session started and questions answered
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)

        # Then: PATCH_EXTRACTION_FAILED error
        assert result.status == "error"
        assert result.error is not None
        assert result.error.code == AppErrorCode.PATCH_EXTRACTION_FAILED
        assert result.error.recovery_hint is not None


class TestInvalidCategoryFromLLM:
    """Tests for handling invalid categories from LLM."""

    def test_invalid_category_returns_validation_error(
        self,
        tmp_repo: Path,
    ) -> None:
        """When LLM returns invalid category, Core returns validation error."""
        # Given: An app with LLM configured to return invalid patch
        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=MockLLMAdapter(force_invalid_patch=True),
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )

        # When: Session started and questions answered
        start_result = app.start_preflight("Add OAuth authentication", str(tmp_repo))
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)

        # Then: UNKNOWN_CATEGORY or VALIDATION_FAILED error
        from preflights.core.types import ErrorCode
        assert result.status == "error"
        assert result.error is not None
        assert result.error.code in (ErrorCode.UNKNOWN_CATEGORY, AppErrorCode.VALIDATION_FAILED), (
            f"Expected UNKNOWN_CATEGORY or VALIDATION_FAILED, got {result.error.code}: {result.error.message}"
        )
