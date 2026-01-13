"""Tests for start_preflight() function.

Tests the first public API: starting a new preflight session.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from preflights.adapters.fixed_clock import FixedClockProvider
from preflights.adapters.mock_llm import MockLLMAdapter
from preflights.adapters.simple_file_context import SimpleFileContextBuilder
from preflights.application.preflights_app import PreflightAppError, PreflightsApp
from preflights.application.types import AppErrorCode
from preflights.core.types import FileContext


class TestStartPreflightBasic:
    """Basic start_preflight tests."""

    def test_start_preflight_returns_session_id(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """start_preflight returns a session ID with expected format."""
        # Given: A valid intention and repository path
        intention = valid_intention
        repo_path = valid_repo_path

        # When: start_preflight is called
        result = app.start_preflight(intention, repo_path)

        # Then: A properly formatted session ID is returned
        assert result.session_id is not None
        assert result.session_id.startswith("session-"), (
            f"Session ID '{result.session_id}' should start with 'session-'"
        )
        assert len(result.session_id) >= 12, (
            f"Session ID '{result.session_id}' too short"
        )

    def test_start_preflight_returns_questions(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """start_preflight returns initial questions with proper structure."""
        # Given: A valid intention and repository path
        intention = valid_intention
        repo_path = valid_repo_path

        # When: start_preflight is called
        result = app.start_preflight(intention, repo_path)

        # Then: Questions are returned with proper structure
        assert result.questions is not None
        assert len(result.questions) >= 1, "Must return at least one question"
        first_q = result.questions[0]
        assert first_q.id, "Question must have an ID"
        assert first_q.question, "Question must have question text"
        assert first_q.type in ("single_choice", "multi_choice", "free_text"), (
            f"Invalid question type: {first_q.type}"
        )

    def test_start_preflight_creates_session(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """start_preflight creates a session that can be continued."""
        # Given: A started preflight session
        result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = result.session_id

        # When: continue_preflight is called with the session ID
        continue_result = app.continue_preflight(session_id, {})

        # Then: Session exists (no SESSION_NOT_FOUND error)
        assert continue_result.status != "error" or (
            continue_result.error is not None
            and continue_result.error.code != "SESSION_NOT_FOUND"
        ), "Session should exist and be retrievable"

    def test_start_preflight_session_has_correct_expiry(
        self,
        valid_intention: str,
        valid_repo_path: str,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Session expires after 30 minutes."""
        from preflights.adapters.default_config import DefaultConfigLoader
        from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
        from preflights.adapters.in_memory_session import InMemorySessionAdapter
        from preflights.adapters.sequential_uid import SequentialUIDProvider

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
        result = app.start_preflight(valid_intention, str(tmp_repo))
        session_id = result.session_id

        # When: 29 minutes pass
        clock.advance_minutes(29)
        continue_result = app.continue_preflight(session_id, {})

        # Then: Session is still valid
        if continue_result.status == "error":
            assert continue_result.error.code != "SESSION_EXPIRED", (
                "Session should not expire before 30 minutes"
            )

        # When: 2 more minutes pass (31 total)
        clock.advance_minutes(2)
        continue_result = app.continue_preflight(session_id, {})

        # Then: Session is expired
        assert continue_result.status == "error"
        assert continue_result.error.code == "SESSION_EXPIRED", (
            "Session should expire after 30 minutes"
        )


class TestStartPreflightValidation:
    """Validation tests for start_preflight."""

    def test_start_preflight_rejects_nonexistent_repo(
        self,
        valid_intention: str,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """start_preflight raises error for non-existent repository."""
        from preflights.adapters.default_config import DefaultConfigLoader
        from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
        from preflights.adapters.in_memory_session import InMemorySessionAdapter
        from preflights.adapters.sequential_uid import SequentialUIDProvider

        # Given: An app without base_path (checks actual filesystem)
        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )

        # When: start_preflight is called with non-existent path
        # Then: PreflightAppError is raised with REPO_NOT_FOUND
        with pytest.raises(PreflightAppError) as exc_info:
            app.start_preflight(valid_intention, "/nonexistent/path")

        assert exc_info.value.code == AppErrorCode.REPO_NOT_FOUND
        assert "not found" in exc_info.value.message.lower()
        assert exc_info.value.recovery_hint is not None


class TestStartPreflightQuestions:
    """Tests for question generation in start_preflight."""

    def test_questions_have_required_fields(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """Questions have all required fields."""
        # Given: A valid intention
        intention = valid_intention

        # When: start_preflight is called
        result = app.start_preflight(intention, valid_repo_path)

        # Then: All questions have required fields
        for question in result.questions:
            assert question.id is not None
            assert len(question.id) > 0
            assert question.type in ("single_choice", "multi_choice", "free_text")
            assert question.question is not None
            assert len(question.question) > 0

    def test_choice_questions_have_options(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """Choice questions have options."""
        # Given: A valid intention
        intention = valid_intention

        # When: start_preflight is called
        result = app.start_preflight(intention, valid_repo_path)

        # Then: Choice questions have at least 2 options
        for question in result.questions:
            if question.type in ("single_choice", "multi_choice"):
                assert question.options is not None
                assert len(question.options) >= 2


class TestStartPreflightDeterminism:
    """Tests for deterministic behavior."""

    def test_same_inputs_produce_same_session_id(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """Sequential UID provider produces deterministic session IDs."""
        # Given: An app with SequentialUIDProvider
        # (fixture provides this)

        # When: start_preflight is called twice
        result1 = app.start_preflight(valid_intention, valid_repo_path)
        result2 = app.start_preflight(valid_intention, valid_repo_path)

        # Then: Session IDs follow sequential pattern
        assert result1.session_id == "session-0001"
        assert result2.session_id == "session-0002"

    def test_questions_are_deterministic(
        self,
        valid_intention: str,
        valid_repo_path: str,
        tmp_repo: Path,
    ) -> None:
        """Same intention produces same questions with same adapters."""
        from preflights.adapters.default_config import DefaultConfigLoader
        from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
        from preflights.adapters.in_memory_session import InMemorySessionAdapter
        from preflights.adapters.sequential_uid import SequentialUIDProvider

        # Given: Two independent apps with identical configuration
        def create_app() -> PreflightsApp:
            return PreflightsApp(
                session_adapter=InMemorySessionAdapter(),
                llm_adapter=MockLLMAdapter(),
                filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
                uid_provider=SequentialUIDProvider(),
                clock_provider=FixedClockProvider(),
                file_context_builder=SimpleFileContextBuilder(),
                config_loader=DefaultConfigLoader(),
            )

        app1 = create_app()
        app2 = create_app()

        # When: Both apps process the same intention
        result1 = app1.start_preflight(valid_intention, valid_repo_path)
        result2 = app2.start_preflight(valid_intention, valid_repo_path)

        # Then: Questions are identical
        assert len(result1.questions) == len(result2.questions)
        for q1, q2 in zip(result1.questions, result2.questions):
            assert q1.id == q2.id
            assert q1.question == q2.question


class TestStartPreflightWithFileContext:
    """Tests for file context integration."""

    def test_uses_file_context_builder(
        self,
        app: PreflightsApp,
        valid_intention: str,
        tmp_repo: Path,
    ) -> None:
        """start_preflight uses file context builder."""
        # Given: A repository with source files
        (tmp_repo / "src").mkdir()
        (tmp_repo / "src" / "main.py").write_text("# Main")

        # When: start_preflight is called
        result = app.start_preflight(valid_intention, str(tmp_repo))

        # Then: Session is created successfully (file context was built)
        assert result.session_id is not None

    def test_can_inject_fixed_file_context(
        self,
        valid_intention: str,
        tmp_repo: Path,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Can inject fixed file context for testing."""
        from preflights.adapters.default_config import DefaultConfigLoader
        from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
        from preflights.adapters.in_memory_session import InMemorySessionAdapter
        from preflights.adapters.sequential_uid import SequentialUIDProvider

        # Given: An app with fixed file context
        fixed_context = FileContext(
            paths=("custom/path.ts",),
            high_level_dirs=("custom/",),
            signals=(("language", "typescript"),),
        )
        file_context_builder = SimpleFileContextBuilder(fixed_context=fixed_context)

        app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=llm_adapter,
            filesystem_adapter=FakeFilesystemAdapter(tmp_repo),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=file_context_builder,
            config_loader=DefaultConfigLoader(),
        )

        # When: start_preflight is called
        result = app.start_preflight(valid_intention, str(tmp_repo))

        # Then: Session is created with injected context
        assert result.session_id is not None
