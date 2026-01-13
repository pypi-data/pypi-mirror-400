"""Tests for process module - main entry point."""

from __future__ import annotations

import pytest

from preflights.core.process import process
from preflights.core.types import (
    ArchitectureState,
    Completed,
    ConversationState,
    CoreError,
    DecisionPatch,
    ErrorCode,
    FileContext,
    HeuristicsConfig,
    Intention,
    NeedsClarification,
    ProcessResult,
    Question,
    ReadyToBuild,
    Answer,
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
def auth_file_context() -> FileContext:
    """File context with auth-related paths."""
    return FileContext(
        paths=(
            "src/auth/login.ts",
            "src/auth/session.ts",
            "src/components/LoginButton.tsx",
        ),
        high_level_dirs=("src/", "src/auth/"),
    )


@pytest.fixture
def auth_intention() -> Intention:
    """Authentication intention."""
    return Intention(text="Add OAuth authentication with Google")


@pytest.fixture
def auth_patch() -> DecisionPatch:
    """Authentication patch."""
    return DecisionPatch(
        category="Authentication",
        fields=(("Strategy", "OAuth"), ("Library", "next-auth")),
    )


@pytest.fixture
def valid_uid_adr() -> str:
    """Valid ADR UID."""
    return "20250106T120000.000Z"


@pytest.fixture
def valid_uid_task() -> str:
    """Valid Task UID."""
    return "20250106T120000.001Z"


@pytest.fixture
def valid_now_utc() -> str:
    """Valid UTC timestamp."""
    return "2025-01-06T12:00:00.001Z"


# =============================================================================
# DETERMINISM TESTS
# =============================================================================


class TestProcessDeterminism:
    """Tests for process determinism - Core MUST be deterministic."""

    def test_determinism_completed_exact_equality(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
        auth_patch: DecisionPatch,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
    ) -> None:
        """Same inputs produce EXACTLY same Completed output."""
        # Call 1
        result1 = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        # Call 2 (identical inputs)
        result2 = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        # MUST be Completed, not just "same type"
        assert isinstance(result1, Completed), f"Expected Completed, got {type(result1)}"
        assert isinstance(result2, Completed), f"Expected Completed, got {type(result2)}"

        # Total equality
        assert result1 == result2

        # Explicit verification of injected values
        assert result1.task.uid == valid_uid_task
        assert result1.adr is not None
        assert result1.adr.uid == valid_uid_adr
        assert result1.adr.snapshot.uid == valid_uid_adr

    def test_determinism_needs_clarification_same_questions(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
    ) -> None:
        """NeedsClarification returns SAME questions in SAME order."""
        result1 = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        result2 = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result1, NeedsClarification)
        assert isinstance(result2, NeedsClarification)

        # Exact equality including order
        assert result1 == result2
        assert result1.questions == result2.questions

    def test_determinism_ready_to_build_exact_equality(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
        auth_patch: DecisionPatch,
    ) -> None:
        """ReadyToBuild returns EXACTLY same output."""
        result1 = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
        )

        result2 = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
        )

        assert isinstance(result1, ReadyToBuild)
        assert isinstance(result2, ReadyToBuild)
        assert result1 == result2

    def test_determinism_core_error_exact_equality(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
    ) -> None:
        """CoreError returns SAME code and message."""
        invalid_patch = DecisionPatch(category="UnknownCategory", fields=())

        result1 = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=invalid_patch,
        )

        result2 = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=invalid_patch,
        )

        assert isinstance(result1, CoreError)
        assert isinstance(result2, CoreError)
        assert result1 == result2
        assert result1.code == result2.code
        assert result1.message == result2.message


# =============================================================================
# NEEDS CLARIFICATION TESTS
# =============================================================================


class TestNeedsClarification:
    """Tests for NeedsClarification result."""

    def test_returns_needs_clarification_when_no_patch(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
    ) -> None:
        """Returns NeedsClarification when decision_patch is None."""
        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)
        assert len(result.questions) > 0

    def test_questions_are_relevant_to_intention(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
    ) -> None:
        """Generated questions are relevant to the intention."""
        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)
        question_ids = {q.id for q in result.questions}
        # Auth intention MUST generate auth-related questions
        assert "auth_strategy" in question_ids, f"Expected auth_strategy question, got: {question_ids}"


# =============================================================================
# READY TO BUILD TESTS
# =============================================================================


class TestReadyToBuild:
    """Tests for ReadyToBuild result."""

    def test_returns_ready_to_build_with_exact_values(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
        auth_patch: DecisionPatch,
    ) -> None:
        """ReadyToBuild contains exact expected values, not just truthy."""
        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
        )

        assert isinstance(result, ReadyToBuild)

        # Exact values for ADR decision
        assert result.needs_adr is True
        assert result.category == "Authentication"

        # Title must contain relevant info
        assert "OAuth" in result.title or "auth" in result.title.lower()

        # Allowlist must contain paths from file_context
        assert len(result.allowlist) > 0
        allowlist_str = " ".join(result.allowlist)
        assert "auth" in allowlist_str.lower()

        # Technical constraints from patch fields
        assert len(result.technical_constraints) > 0
        constraints_str = " ".join(result.technical_constraints)
        assert "OAuth" in constraints_str or "next-auth" in constraints_str

        # ADR fields must be pre-filled for next call
        assert result.decision_context != ""
        assert result.decision_text != ""
        assert "OAuth" in result.decision_text

    def test_ready_to_build_indicates_adr_need(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
        auth_patch: DecisionPatch,
    ) -> None:
        """ReadyToBuild.needs_adr reflects DecisionDetector output."""
        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
        )

        assert isinstance(result, ReadyToBuild)
        # Auth intention should trigger ADR
        assert result.needs_adr is True
        assert result.category == "Authentication"

    def test_ready_to_build_no_adr_for_simple_change(
        self,
        heuristics: HeuristicsConfig,
    ) -> None:
        """Simple changes don't need ADR."""
        intention = Intention(text="Fix typo in button text")
        patch = DecisionPatch(category="Frontend", fields=(("Styling", "CSS"),))
        file_context = FileContext(
            paths=("src/components/Button.tsx",),
            high_level_dirs=("src/components/",),
        )

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        assert isinstance(result, ReadyToBuild)
        assert result.needs_adr is False
        assert result.category is None  # No category when no ADR needed

    def test_ready_to_build_contains_enough_info_for_completed(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
        auth_patch: DecisionPatch,
    ) -> None:
        """ReadyToBuild contains all info Application needs to call process() again."""
        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
        )

        assert isinstance(result, ReadyToBuild)

        # These fields are required for Application to proceed
        assert result.title != ""
        assert len(result.allowlist) > 0
        assert result.objective != ""

        # If needs_adr, ADR fields must be ready
        if result.needs_adr:
            assert result.category is not None
            assert result.decision_context != ""
            assert result.decision_text != ""
            assert result.rationale != ""


# =============================================================================
# COMPLETED TESTS
# =============================================================================


class TestCompleted:
    """Tests for Completed result."""

    def test_returns_completed_with_adr(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
        auth_patch: DecisionPatch,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
    ) -> None:
        """Returns Completed with ADR when UIDs provided and ADR needed."""
        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, Completed)
        assert result.task is not None
        assert result.adr is not None
        assert result.updated_architecture is not None

        # Validate task
        assert result.task.uid == valid_uid_task
        assert result.task.related_adr_uid == valid_uid_adr

        # Validate ADR
        assert result.adr.uid == valid_uid_adr
        assert result.adr.category == "Authentication"

    def test_returns_completed_without_adr(
        self,
        heuristics: HeuristicsConfig,
        valid_uid_task: str,
        valid_now_utc: str,
    ) -> None:
        """Returns Completed without ADR for simple tasks."""
        intention = Intention(text="Fix typo in button")
        patch = DecisionPatch(category="Frontend", fields=(("Styling", "CSS"),))
        file_context = FileContext(
            paths=("src/components/Button.tsx",),
            high_level_dirs=("src/components/",),
        )

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, Completed)
        assert result.task is not None
        assert result.adr is None
        assert result.updated_architecture is None


# =============================================================================
# ERROR TESTS
# =============================================================================


class TestCoreError:
    """Tests for CoreError result."""

    def test_error_on_unknown_category(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
    ) -> None:
        """Returns CoreError for unknown category in patch."""
        invalid_patch = DecisionPatch(
            category="UnknownCategory",
            fields=(("Field", "Value"),),
        )

        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=invalid_patch,
        )

        assert isinstance(result, CoreError)
        assert result.code == ErrorCode.UNKNOWN_CATEGORY

    def test_error_on_unknown_field(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
    ) -> None:
        """Returns CoreError for unknown field in patch."""
        invalid_patch = DecisionPatch(
            category="Authentication",
            fields=(("UnknownField", "Value"),),
        )

        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=invalid_patch,
        )

        assert isinstance(result, CoreError)
        assert result.code == ErrorCode.UNKNOWN_FIELD

    def test_error_when_now_utc_missing_with_uids(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
        auth_patch: DecisionPatch,
        valid_uid_adr: str,
        valid_uid_task: str,
    ) -> None:
        """Returns CoreError when now_utc is missing but UIDs provided."""
        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=None,  # Missing
        )

        assert isinstance(result, CoreError)
        assert result.code == ErrorCode.VALIDATION_FAILED

    def test_error_when_adr_uid_missing_but_needed(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
        auth_patch: DecisionPatch,
        valid_uid_task: str,
        valid_now_utc: str,
    ) -> None:
        """Returns CoreError when ADR is needed but uid_for_adr is missing."""
        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=auth_patch,
            uid_for_adr=None,  # Missing but needed
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, CoreError)
        assert result.code == ErrorCode.VALIDATION_FAILED


# =============================================================================
# CONVERSATION STATE TESTS
# =============================================================================


class TestConversationState:
    """Tests for conversation state handling."""

    def test_respects_already_asked_questions(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        auth_intention: Intention,
    ) -> None:
        """Doesn't re-ask already asked questions."""
        conversation_state = ConversationState(
            asked_questions=(
                Question(
                    id="auth_strategy",
                    type="single_choice",
                    question="Which strategy?",
                    options=("OAuth", "Email"),
                ),
            ),
            answers=(
                Answer(question_id="auth_strategy", value="OAuth"),
            ),
        )

        result = process(
            intention=auth_intention,
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=conversation_state,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)
        question_ids = {q.id for q in result.questions}
        assert "auth_strategy" not in question_ids


# =============================================================================
# ARCHITECTURE STATE TESTS
# =============================================================================


class TestArchitectureState:
    """Tests for architecture state handling."""

    def test_builds_on_existing_architecture(
        self,
        heuristics: HeuristicsConfig,
        auth_file_context: FileContext,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
    ) -> None:
        """New ADR builds on existing architecture."""
        existing = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(
                ("Database", (("Type", "PostgreSQL (ADR 20250106T100000.000Z)"),)),
            ),
        )

        intention = Intention(text="Add OAuth authentication")
        patch = DecisionPatch(
            category="Authentication",
            fields=(("Strategy", "OAuth"),),
        )

        result = process(
            intention=intention,
            current_architecture=existing,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, Completed)
        assert result.adr is not None
        assert result.updated_architecture is not None

        # Updated architecture should have both categories
        cat_names = [cat[0] for cat in result.updated_architecture.categories]
        assert "Database" in cat_names
        assert "Authentication" in cat_names

        # Previous UID should be set
        assert result.adr.previous_uid == existing.uid


class TestAllowlistFromAnswers:
    """Tests for using allowlist_paths from user answers."""

    def test_uses_allowlist_from_conversation_state(
        self, heuristics: HeuristicsConfig
    ) -> None:
        """Core uses allowlist_paths answer instead of derive_allowlist()."""
        # Empty file context - derive_allowlist() would return None
        empty_context = FileContext(paths=(), high_level_dirs=())

        # But user already answered allowlist_paths
        conversation_state = ConversationState(
            asked_questions=(
                Question(
                    id="allowlist_paths",
                    type="free_text",
                    question="Which files?",
                ),
            ),
            answers=(
                Answer(question_id="allowlist_paths", value="src/custom, lib/utils"),
            ),
        )

        result = process(
            intention=Intention(text="Add custom feature"),
            current_architecture=None,
            file_context=empty_context,
            conversation_state=conversation_state,
            heuristics_config=heuristics,
            decision_patch=DecisionPatch(
                category="Frontend",
                fields=(("Framework", "React"),),
            ),
            uid_for_adr=None,
            uid_for_task=None,
            now_utc=None,
        )

        # Should return ReadyToBuild (not NeedsClarification)
        assert isinstance(result, ReadyToBuild), f"Expected ReadyToBuild, got {type(result)}"
        # Allowlist should be from user answer
        assert "src/custom" in result.allowlist
        assert "lib/utils" in result.allowlist

    def test_falls_back_to_derive_allowlist_if_no_answer(
        self, heuristics: HeuristicsConfig, auth_file_context: FileContext
    ) -> None:
        """Core uses derive_allowlist() when allowlist_paths not answered."""
        result = process(
            intention=Intention(text="Add OAuth authentication"),
            current_architecture=None,
            file_context=auth_file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=DecisionPatch(
                category="Authentication",
                fields=(("Strategy", "OAuth"),),
            ),
            uid_for_adr=None,
            uid_for_task=None,
            now_utc=None,
        )

        # Should derive from file context
        assert isinstance(result, ReadyToBuild)
        assert any("auth" in p.lower() for p in result.allowlist)
