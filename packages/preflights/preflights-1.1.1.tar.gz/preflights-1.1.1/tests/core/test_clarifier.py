"""Tests for clarifier module."""

from __future__ import annotations

import pytest

from preflights.core.clarifier import generate_questions
from preflights.core.types import (
    ArchitectureState,
    FileContext,
    HeuristicsConfig,
    Intention,
    Question,
    default_v1_heuristics,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def heuristics() -> HeuristicsConfig:
    """Default V1 heuristics."""
    return default_v1_heuristics()


@pytest.fixture
def empty_file_context() -> FileContext:
    """Empty file context."""
    return FileContext(paths=())


@pytest.fixture
def nextjs_file_context() -> FileContext:
    """Next.js file context."""
    return FileContext(
        paths=(
            "src/pages/index.tsx",
            "src/components/Button.tsx",
            "next.config.js",
            "package.json",
        ),
        signals=(("nextjs", "true"),),
    )


@pytest.fixture
def python_file_context() -> FileContext:
    """Python file context."""
    return FileContext(
        paths=(
            "src/main.py",
            "src/api/routes.py",
            "requirements.txt",
        ),
    )


# =============================================================================
# GENERATE QUESTIONS TESTS
# =============================================================================


class TestGenerateQuestions:
    """Tests for generate_questions function."""

    def test_max_5_questions(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Never returns more than 5 questions."""
        intention = Intention(text="Add authentication with OAuth and database storage")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        assert len(result) <= 5

    def test_never_reask_questions(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Never re-ask already asked questions."""
        intention = Intention(text="Add authentication")
        already_asked = frozenset({"auth_strategy", "auth_library"})

        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            already_asked,
        )

        question_ids = {q.id for q in result}
        assert "auth_strategy" not in question_ids
        assert "auth_library" not in question_ids

    def test_auth_intention_generates_auth_questions(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Auth-related intention generates auth_strategy question."""
        intention = Intention(text="Add OAuth login")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        question_ids = {q.id for q in result}
        # Auth intention MUST generate auth_strategy as first question
        assert "auth_strategy" in question_ids, f"Expected auth_strategy, got: {question_ids}"

    def test_database_intention_generates_db_questions(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Database-related intention generates database questions."""
        intention = Intention(text="Add PostgreSQL database")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        question_ids = {q.id for q in result}
        # Database intention MUST generate db_type as primary question
        assert "db_type" in question_ids, f"Expected db_type question for database intention, got: {question_ids}"

    def test_nextjs_context_affects_options(
        self, heuristics: HeuristicsConfig, nextjs_file_context: FileContext
    ) -> None:
        """Next.js context affects library options."""
        intention = Intention(text="Add authentication")
        result = generate_questions(
            intention,
            None,
            nextjs_file_context,
            heuristics,
            frozenset(),
        )

        # Find auth_library question
        auth_lib_q = next((q for q in result if q.id == "auth_library"), None)
        if auth_lib_q and auth_lib_q.options:
            # Should include NextAuth.js for Next.js projects
            assert "NextAuth.js" in auth_lib_q.options

    def test_generic_questions_when_no_category(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Generic questions when no category detected."""
        intention = Intention(text="Update readme file")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        # Should have at least one generic question
        assert len(result) > 0
        question_ids = {q.id for q in result}
        # Generic intentions MUST generate scope question as primary clarification
        assert "scope" in question_ids, f"Expected scope question for generic intention, got: {question_ids}"

    def test_questions_are_choice_type_preferred(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Choice questions are preferred over free-text."""
        intention = Intention(text="Add authentication with database")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        # Most questions should be choice type
        choice_questions = [
            q for q in result if q.type in ("single_choice", "multi_choice")
        ]
        assert len(choice_questions) >= len(result) // 2

    def test_questions_have_unique_ids(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """All questions have unique IDs."""
        intention = Intention(text="Add authentication and database")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        question_ids = [q.id for q in result]
        assert len(question_ids) == len(set(question_ids))

    def test_multi_choice_has_min_selections(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Multi-choice questions have min_selections set."""
        intention = Intention(text="Add OAuth authentication")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        for q in result:
            if q.type == "multi_choice":
                # Should have min_selections (even if optional)
                assert q.min_selections is not None or q.optional

    def test_empty_already_asked(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Works with empty already_asked set."""
        intention = Intention(text="Add auth")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        assert len(result) > 0

    def test_with_existing_architecture(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Works with existing architecture state."""
        existing = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(("Authentication", (("Strategy", "OAuth"),)),),
        )
        intention = Intention(text="Add database")
        result = generate_questions(
            intention,
            existing,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        # Should generate database questions - db_type is primary for database intentions
        question_ids = {q.id for q in result}
        assert "db_type" in question_ids, f"Expected db_type question for database intention, got: {question_ids}"


class TestQuestionStructure:
    """Tests for question structure."""

    def test_single_choice_has_options(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Single choice questions have options."""
        intention = Intention(text="Add authentication")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        for q in result:
            if q.type == "single_choice":
                assert q.options is not None
                assert len(q.options) >= 2

    def test_multi_choice_has_options(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """Multi choice questions have options."""
        intention = Intention(text="Add OAuth")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        for q in result:
            if q.type == "multi_choice":
                assert q.options is not None
                assert len(q.options) >= 2

    def test_all_questions_have_id_and_text(
        self, heuristics: HeuristicsConfig, empty_file_context: FileContext
    ) -> None:
        """All questions have id and question text."""
        intention = Intention(text="Add auth")
        result = generate_questions(
            intention,
            None,
            empty_file_context,
            heuristics,
            frozenset(),
        )

        for q in result:
            assert q.id
            assert q.question
            assert len(q.id) > 0
            assert len(q.question) > 0
