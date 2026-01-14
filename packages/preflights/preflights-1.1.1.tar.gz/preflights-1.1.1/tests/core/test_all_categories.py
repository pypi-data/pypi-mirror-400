"""Parameterized tests for all categories.

Uses pytest.mark.parametrize to test the same behavior
across all schema categories without code duplication.
"""

from __future__ import annotations

import pytest

from preflights.core.process import process
from preflights.core.snapshot_builder import apply_patch
from preflights.core.types import (
    ArchitectureState,
    Completed,
    CoreError,
    DecisionPatch,
    ErrorCode,
    FileContext,
    HeuristicsConfig,
    Intention,
    NeedsClarification,
    ReadyToBuild,
)


# =============================================================================
# TEST DATA FOR ALL CATEGORIES
# =============================================================================


# (category, fields, intention_keyword, file_path_pattern)
ALL_CATEGORIES_DATA = [
    pytest.param(
        "Authentication",
        (("Strategy", "OAuth"), ("Library", "next-auth")),
        "authentication",
        "src/auth/login.ts",
        id="authentication",
    ),
    pytest.param(
        "Database",
        (("Type", "PostgreSQL"), ("ORM", "Prisma")),
        "database",
        "src/db/connection.ts",
        id="database",
    ),
    pytest.param(
        "Frontend",
        (("Framework", "React"), ("Styling", "Tailwind")),
        "frontend",
        "src/components/App.tsx",
        id="frontend",
    ),
    pytest.param(
        "Backend",
        (("Framework", "FastAPI"), ("API_Style", "REST")),
        "API",
        "src/api/routes.py",
        id="backend",
    ),
    pytest.param(
        "Infra",
        (("Hosting", "Docker"), ("CI_CD", "GitHub Actions")),
        "infrastructure",
        "Dockerfile",
        id="infra",
    ),
]


# =============================================================================
# PARAMETERIZED: Full Flow Tests
# =============================================================================


class TestAllCategoriesFullFlow:
    """Full flow tests for all categories."""

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_full_flow_produces_completed(
        self,
        heuristics: HeuristicsConfig,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """Full flow from intention to Completed works for all categories."""
        intention = Intention(text=f"Add {intention_keyword}")
        file_context = FileContext(paths=(file_path,))
        patch = DecisionPatch(category=category, fields=fields)

        # Tour 1: NeedsClarification
        result1 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )
        assert isinstance(result1, NeedsClarification)

        # Tour 2: ReadyToBuild
        result2 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )
        assert isinstance(result2, ReadyToBuild)
        assert result2.needs_adr is True
        assert result2.category == category

        # Tour 3: Completed
        result3 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )
        assert isinstance(result3, Completed)
        assert result3.adr is not None
        assert result3.adr.category == category
        assert result3.task.uid == valid_uid_task
        assert result3.adr.uid == valid_uid_adr

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_apply_patch_creates_correct_category(
        self,
        heuristics: HeuristicsConfig,
        valid_uid_adr: str,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """apply_patch creates correct category structure for all categories."""
        patch = DecisionPatch(category=category, fields=fields)

        result = apply_patch(None, patch, valid_uid_adr, heuristics.schema)

        # Check category exists
        cat_dict = {cat[0]: dict(cat[1]) for cat in result.categories}
        assert category in cat_dict

        # Check all fields exist
        for field_name, field_value in fields:
            assert field_name in cat_dict[category]
            assert field_value in cat_dict[category][field_name]
            assert valid_uid_adr in cat_dict[category][field_name]


# =============================================================================
# PARAMETERIZED: Architecture Update Tests
# =============================================================================


class TestAllCategoriesArchitectureUpdate:
    """Architecture update tests for all categories."""

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_new_category_preserves_existing(
        self,
        heuristics: HeuristicsConfig,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
        previous_uid: str,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """Adding a new category preserves existing ones."""
        # Create existing architecture with a different category
        # Use category + field that exist in schema
        if category != "Database":
            existing_category = "Database"
            existing_field = ("Type", f"PostgreSQL (ADR {previous_uid})")
        else:
            existing_category = "Authentication"
            existing_field = ("Strategy", f"OAuth (ADR {previous_uid})")

        existing = ArchitectureState(
            uid=previous_uid,
            schema_version="v1",
            categories=(
                (existing_category, (existing_field,)),
            ),
        )

        intention = Intention(text=f"Add {intention_keyword}")
        file_context = FileContext(paths=(file_path,))
        patch = DecisionPatch(category=category, fields=fields)

        result = process(
            intention=intention,
            current_architecture=existing,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, Completed)
        assert result.updated_architecture is not None

        cat_names = {cat[0] for cat in result.updated_architecture.categories}
        assert existing_category in cat_names, "Existing category was dropped"
        assert category in cat_names, "New category was not added"


# =============================================================================
# PARAMETERIZED: Error Tests
# =============================================================================


# Invalid fields for each category
INVALID_FIELDS_DATA = [
    pytest.param("Authentication", "NonExistentField", id="auth-invalid-field"),
    pytest.param("Database", "InvalidDBField", id="db-invalid-field"),
    pytest.param("Frontend", "BadFrontendField", id="frontend-invalid-field"),
    pytest.param("Backend", "WrongBackendField", id="backend-invalid-field"),
    pytest.param("Infra", "MissingInfraField", id="infra-invalid-field"),
]


class TestAllCategoriesErrors:
    """Error tests for all categories."""

    @pytest.mark.parametrize("category,invalid_field", INVALID_FIELDS_DATA)
    def test_unknown_field_returns_error(
        self,
        heuristics: HeuristicsConfig,
        category: str,
        invalid_field: str,
    ) -> None:
        """Unknown field in any category returns CoreError."""
        intention = Intention(text="Add something")
        file_context = FileContext(paths=("src/app.ts",))
        patch = DecisionPatch(category=category, fields=((invalid_field, "Value"),))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        assert isinstance(result, CoreError)
        assert result.code == ErrorCode.UNKNOWN_FIELD
        assert invalid_field in result.message


# =============================================================================
# PARAMETERIZED: ReadyToBuild Content Tests
# =============================================================================


class TestAllCategoriesReadyToBuildContent:
    """ReadyToBuild content tests for all categories."""

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_ready_to_build_has_required_fields(
        self,
        heuristics: HeuristicsConfig,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """ReadyToBuild contains all required fields for any category."""
        intention = Intention(text=f"Add {intention_keyword}")
        file_context = FileContext(paths=(file_path,))
        patch = DecisionPatch(category=category, fields=fields)

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        assert isinstance(result, ReadyToBuild)

        # Required fields for ADR generation
        assert result.needs_adr is True
        assert result.category == category
        assert result.title != ""
        assert len(result.allowlist) > 0
        assert result.decision_context != ""
        assert result.decision_text != ""

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_ready_to_build_decision_text_contains_values(
        self,
        heuristics: HeuristicsConfig,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """ReadyToBuild decision_text contains patch field values."""
        intention = Intention(text=f"Add {intention_keyword}")
        file_context = FileContext(paths=(file_path,))
        patch = DecisionPatch(category=category, fields=fields)

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        assert isinstance(result, ReadyToBuild)

        # Decision text should mention at least one field value
        decision_text_lower = result.decision_text.lower()
        found_any_value = any(
            value.lower() in decision_text_lower
            for _, value in fields
        )
        assert found_any_value, (
            f"decision_text '{result.decision_text}' does not contain any field values"
        )


# =============================================================================
# PARAMETERIZED: ADR Content Tests
# =============================================================================


class TestAllCategoriesADRContent:
    """ADR content tests for all categories."""

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_adr_has_valid_structure(
        self,
        heuristics: HeuristicsConfig,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """ADR has valid structure for any category."""
        intention = Intention(text=f"Add {intention_keyword}")
        file_context = FileContext(paths=(file_path,))
        patch = DecisionPatch(category=category, fields=fields)

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, Completed)
        assert result.adr is not None

        adr = result.adr
        assert adr.uid == valid_uid_adr
        assert adr.category == category
        assert adr.title != ""
        assert adr.context != ""
        assert adr.decision != ""
        assert adr.rationale != ""
        assert len(adr.alternatives) > 0
        assert len(adr.changes_in_this_version) > 0

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_adr_snapshot_matches_patch(
        self,
        heuristics: HeuristicsConfig,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """ADR snapshot contains patch values for any category."""
        intention = Intention(text=f"Add {intention_keyword}")
        file_context = FileContext(paths=(file_path,))
        patch = DecisionPatch(category=category, fields=fields)

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, Completed)
        assert result.adr is not None

        snapshot = result.adr.snapshot
        cat_dict = {cat[0]: dict(cat[1]) for cat in snapshot.categories}

        assert category in cat_dict

        for field_name, field_value in fields:
            assert field_name in cat_dict[category]
            assert field_value in cat_dict[category][field_name]


# =============================================================================
# PARAMETERIZED: Task Content Tests
# =============================================================================


class TestAllCategoriesTaskContent:
    """Task content tests for all categories."""

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_task_references_adr(
        self,
        heuristics: HeuristicsConfig,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """Task references ADR UID for any category."""
        intention = Intention(text=f"Add {intention_keyword}")
        file_context = FileContext(paths=(file_path,))
        patch = DecisionPatch(category=category, fields=fields)

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, Completed)
        assert result.task.related_adr_uid == valid_uid_adr

    @pytest.mark.parametrize(
        "category,fields,intention_keyword,file_path",
        ALL_CATEGORIES_DATA,
    )
    def test_task_has_acceptance_criteria(
        self,
        heuristics: HeuristicsConfig,
        valid_uid_adr: str,
        valid_uid_task: str,
        valid_now_utc: str,
        category: str,
        fields: tuple[tuple[str, str], ...],
        intention_keyword: str,
        file_path: str,
    ) -> None:
        """Task has acceptance criteria for any category."""
        intention = Intention(text=f"Add {intention_keyword}")
        file_context = FileContext(paths=(file_path,))
        patch = DecisionPatch(category=category, fields=fields)

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr=valid_uid_adr,
            uid_for_task=valid_uid_task,
            now_utc=valid_now_utc,
        )

        assert isinstance(result, Completed)
        assert len(result.task.acceptance_criteria) > 0
