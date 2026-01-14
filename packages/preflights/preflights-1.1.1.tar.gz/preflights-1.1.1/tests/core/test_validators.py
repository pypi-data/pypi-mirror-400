"""Tests for validators module."""

from __future__ import annotations

import pytest

from preflights.core.types import (
    ADR,
    ArchitectureState,
    DecisionPatch,
    ErrorCode,
    SnapshotSchema,
    Task,
    default_v1_schema,
)
from preflights.core.validators import (
    validate_adr,
    validate_decision_patch,
    validate_snapshot,
    validate_task,
    validate_uid_format,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def v1_schema() -> SnapshotSchema:
    """Default V1 schema."""
    return default_v1_schema()


@pytest.fixture
def valid_uid() -> str:
    """Valid UID format."""
    return "20250106T120000.000Z"


@pytest.fixture
def valid_task(valid_uid: str) -> Task:
    """Valid task fixture."""
    return Task(
        uid=valid_uid,
        title="Add OAuth Authentication",
        objective="Implement OAuth login with Google",
        context="User needs social login capability",
        allowlist=("src/auth/", "src/components/LoginButton.tsx"),
        forbidden=("src/legacy/",),
        technical_constraints=("Use next-auth library",),
        acceptance_criteria=(
            "User can click 'Login with Google' button",
            "User is redirected to dashboard after successful login",
        ),
        created_at_utc="2025-01-06T12:00:00Z",
        related_adr_uid=None,
    )


@pytest.fixture
def valid_snapshot(valid_uid: str) -> ArchitectureState:
    """Valid architecture snapshot fixture."""
    return ArchitectureState(
        uid=valid_uid,
        schema_version="v1",
        categories=(
            (
                "Authentication",
                (
                    ("Strategy", "OAuth"),
                    ("Library", "next-auth"),
                ),
            ),
        ),
    )


@pytest.fixture
def valid_adr(valid_uid: str, valid_snapshot: ArchitectureState) -> ADR:
    """Valid ADR fixture."""
    return ADR(
        uid=valid_uid,
        title="OAuth Authentication Strategy",
        category="Authentication",
        date_utc="2025-01-06",
        previous_uid=None,
        snapshot=valid_snapshot,
        changes_in_this_version=("Added: Authentication.Strategy = OAuth",),
        context="We need user authentication for the application.",
        decision="Use OAuth with Google as the primary provider.",
        rationale="OAuth provides secure, standard authentication without password management.",
        alternatives=("Email/Password - rejected due to password management complexity",),
        consequences_positive=("No password storage required", "Users can use existing Google accounts"),
        consequences_negative=("Requires Google account",),
        consequences_neutral=("Need to configure OAuth credentials",),
        supersedes_uid=None,
    )


# =============================================================================
# UID FORMAT TESTS
# =============================================================================


class TestValidateUidFormat:
    """Tests for validate_uid_format."""

    def test_valid_uid(self, valid_uid: str) -> None:
        """Valid UID passes validation."""
        result = validate_uid_format(valid_uid)
        assert result is None

    def test_valid_uid_with_nonzero_ms(self) -> None:
        """Valid UID with non-zero milliseconds."""
        result = validate_uid_format("20250106T143512.237Z")
        assert result is None

    def test_invalid_uid_missing_z(self) -> None:
        """UID without Z suffix fails."""
        result = validate_uid_format("20250106T120000.000")
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_invalid_uid_wrong_format(self) -> None:
        """Wrong format fails."""
        result = validate_uid_format("2025-01-06T12:00:00Z")
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_invalid_uid_missing_ms(self) -> None:
        """UID without milliseconds fails."""
        result = validate_uid_format("20250106T120000Z")
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_invalid_uid_empty(self) -> None:
        """Empty string fails."""
        result = validate_uid_format("")
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    # =========================================================================
    # NEW FORMAT WITH ANTI-COLLISION SUFFIX
    # =========================================================================

    def test_valid_uid_with_suffix(self) -> None:
        """UID with anti-collision suffix passes validation."""
        result = validate_uid_format("20250106T143512.237Z-A3F9")
        assert result is None

    def test_valid_uid_with_lowercase_suffix(self) -> None:
        """UID with lowercase hex suffix passes validation."""
        result = validate_uid_format("20250106T143512.237Z-a3f9")
        assert result is None

    def test_valid_uid_with_mixed_case_suffix(self) -> None:
        """UID with mixed case hex suffix passes validation."""
        result = validate_uid_format("20250106T143512.237Z-A3f9")
        assert result is None

    def test_invalid_uid_suffix_too_short(self) -> None:
        """UID with suffix shorter than 4 chars fails."""
        result = validate_uid_format("20250106T143512.237Z-A3F")
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_invalid_uid_suffix_too_long(self) -> None:
        """UID with suffix longer than 4 chars fails."""
        result = validate_uid_format("20250106T143512.237Z-A3F9B")
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_invalid_uid_suffix_non_hex(self) -> None:
        """UID with non-hex suffix chars fails."""
        result = validate_uid_format("20250106T143512.237Z-GHIJ")
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_invalid_uid_suffix_missing_dash(self) -> None:
        """UID with suffix but no dash fails."""
        result = validate_uid_format("20250106T143512.237ZA3F9")
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_backward_compatibility_legacy_format(self) -> None:
        """Legacy format (without suffix) still works."""
        # This is critical for reading existing ADRs
        result = validate_uid_format("20250106T120000.000Z")
        assert result is None


# =============================================================================
# DECISION PATCH TESTS
# =============================================================================


class TestValidateDecisionPatch:
    """Tests for validate_decision_patch."""

    def test_valid_patch(self, v1_schema: SnapshotSchema) -> None:
        """Valid patch passes validation."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(("Strategy", "OAuth"), ("Library", "next-auth")),
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is None

    def test_unknown_category(self, v1_schema: SnapshotSchema) -> None:
        """Unknown category fails."""
        patch = DecisionPatch(
            category="UnknownCategory",
            fields=(("Strategy", "OAuth"),),
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.UNKNOWN_CATEGORY
        assert "UnknownCategory" in result.message

    def test_unknown_field(self, v1_schema: SnapshotSchema) -> None:
        """Unknown field fails."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(("UnknownField", "value"),),
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.UNKNOWN_FIELD
        assert "UnknownField" in result.message

    def test_case_insensitive_category(self, v1_schema: SnapshotSchema) -> None:
        """Category matching is case-insensitive."""
        patch = DecisionPatch(
            category="authentication",  # lowercase
            fields=(("Strategy", "OAuth"),),
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is None

    def test_case_insensitive_field(self, v1_schema: SnapshotSchema) -> None:
        """Field matching is case-insensitive."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(("strategy", "OAuth"),),  # lowercase
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is None

    # =========================================================================
    # OTHER CATEGORY (WILDCARD) TESTS
    # =========================================================================

    def test_other_category_accepts_any_field(self, v1_schema: SnapshotSchema) -> None:
        """Other category with wildcard accepts any field name."""
        patch = DecisionPatch(
            category="Other",
            fields=(
                ("Technology", "Supabase"),
                ("Purpose", "Authentication + Database"),
                ("CustomField", "Any value"),
            ),
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is None

    def test_other_category_case_insensitive(self, v1_schema: SnapshotSchema) -> None:
        """Other category matching is case-insensitive."""
        patch = DecisionPatch(
            category="other",  # lowercase
            fields=(("AnyField", "value"),),
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is None

    def test_other_category_with_single_field(self, v1_schema: SnapshotSchema) -> None:
        """Other category works with single arbitrary field."""
        patch = DecisionPatch(
            category="Other",
            fields=(("SomeNewTechnology", "value"),),
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is None

    def test_other_category_with_special_chars_in_field(
        self, v1_schema: SnapshotSchema
    ) -> None:
        """Other category accepts field names with special characters."""
        patch = DecisionPatch(
            category="Other",
            fields=(
                ("Field_With_Underscores", "value1"),
                ("Field-With-Dashes", "value2"),
            ),
        )
        result = validate_decision_patch(patch, v1_schema)
        assert result is None


# =============================================================================
# SNAPSHOT TESTS
# =============================================================================


class TestValidateSnapshot:
    """Tests for validate_snapshot."""

    def test_valid_snapshot(
        self, valid_snapshot: ArchitectureState, v1_schema: SnapshotSchema
    ) -> None:
        """Valid snapshot passes validation."""
        result = validate_snapshot(valid_snapshot, None, v1_schema)
        assert result is None

    def test_unknown_category_in_snapshot(self, v1_schema: SnapshotSchema) -> None:
        """Unknown category in snapshot fails."""
        snapshot = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(("UnknownCategory", (("Field", "Value"),)),),
        )
        result = validate_snapshot(snapshot, None, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.UNKNOWN_CATEGORY

    def test_unknown_field_in_snapshot(self, v1_schema: SnapshotSchema) -> None:
        """Unknown field in snapshot fails."""
        snapshot = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(("Authentication", (("UnknownField", "Value"),)),),
        )
        result = validate_snapshot(snapshot, None, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.UNKNOWN_FIELD

    def test_silent_drop_category(
        self, valid_snapshot: ArchitectureState, v1_schema: SnapshotSchema
    ) -> None:
        """Silent drop of category fails."""
        previous = ArchitectureState(
            uid="20250106T110000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"),)),
                ("Database", (("Type", "PostgreSQL"),)),
            ),
        )
        # Current snapshot is missing Database category
        result = validate_snapshot(valid_snapshot, previous, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.VALIDATION_FAILED
        assert "silently dropped" in result.message

    def test_silent_drop_field(self, v1_schema: SnapshotSchema) -> None:
        """Silent drop of field fails."""
        previous = ArchitectureState(
            uid="20250106T110000.000Z",
            schema_version="v1",
            categories=(
                (
                    "Authentication",
                    (("Strategy", "OAuth"), ("Library", "next-auth")),
                ),
            ),
        )
        current = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"),)),  # Missing Library
            ),
        )
        result = validate_snapshot(current, previous, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.VALIDATION_FAILED
        assert "silently dropped" in result.message

    def test_empty_snapshot_valid(self, v1_schema: SnapshotSchema) -> None:
        """Empty snapshot is valid if no previous."""
        snapshot = ArchitectureState(
            uid=None,
            schema_version="v1",
            categories=(),
        )
        result = validate_snapshot(snapshot, None, v1_schema)
        assert result is None

    # =========================================================================
    # OTHER CATEGORY (WILDCARD) SNAPSHOT TESTS
    # =========================================================================

    def test_other_category_snapshot_accepts_any_field(
        self, v1_schema: SnapshotSchema
    ) -> None:
        """Snapshot with Other category accepts any field names."""
        snapshot = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                (
                    "Other",
                    (
                        ("Technology", "Supabase (ADR 20250106T120000.000Z)"),
                        ("Purpose", "All-in-one solution"),
                        ("ArbitraryField", "Any value"),
                    ),
                ),
            ),
        )
        result = validate_snapshot(snapshot, None, v1_schema)
        assert result is None

    def test_other_category_with_mixed_categories(
        self, v1_schema: SnapshotSchema
    ) -> None:
        """Snapshot with Other and standard categories validates correctly."""
        snapshot = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"),)),
                ("Other", (("CustomTech", "Value"),)),
            ),
        )
        result = validate_snapshot(snapshot, None, v1_schema)
        assert result is None


# =============================================================================
# TASK TESTS
# =============================================================================


class TestValidateTask:
    """Tests for validate_task."""

    def test_valid_task(self, valid_task: Task) -> None:
        """Valid task passes validation."""
        result = validate_task(valid_task)
        assert result is None

    def test_empty_allowlist(self, valid_task: Task) -> None:
        """Empty allowlist fails."""
        task = Task(
            uid=valid_task.uid,
            title=valid_task.title,
            objective=valid_task.objective,
            context=valid_task.context,
            allowlist=(),  # Empty
            forbidden=valid_task.forbidden,
            technical_constraints=valid_task.technical_constraints,
            acceptance_criteria=valid_task.acceptance_criteria,
            created_at_utc=valid_task.created_at_utc,
        )
        result = validate_task(task)
        assert result is not None
        assert result.code == ErrorCode.EMPTY_ALLOWLIST

    def test_forbidden_overlap(self, valid_task: Task) -> None:
        """Overlapping allowlist and forbidden fails."""
        task = Task(
            uid=valid_task.uid,
            title=valid_task.title,
            objective=valid_task.objective,
            context=valid_task.context,
            allowlist=("src/auth/", "src/components/"),
            forbidden=("src/auth/",),  # Overlaps with allowlist
            technical_constraints=valid_task.technical_constraints,
            acceptance_criteria=valid_task.acceptance_criteria,
            created_at_utc=valid_task.created_at_utc,
        )
        result = validate_task(task)
        assert result is not None
        assert result.code == ErrorCode.FORBIDDEN_OVERLAP

    def test_empty_acceptance_criteria(self, valid_task: Task) -> None:
        """Empty acceptance criteria fails."""
        task = Task(
            uid=valid_task.uid,
            title=valid_task.title,
            objective=valid_task.objective,
            context=valid_task.context,
            allowlist=valid_task.allowlist,
            forbidden=valid_task.forbidden,
            technical_constraints=valid_task.technical_constraints,
            acceptance_criteria=(),  # Empty
            created_at_utc=valid_task.created_at_utc,
        )
        result = validate_task(task)
        assert result is not None
        assert result.code == ErrorCode.EMPTY_ACCEPTANCE_CRITERIA

    def test_invalid_uid_format(self, valid_task: Task) -> None:
        """Invalid UID format fails."""
        task = Task(
            uid="invalid-uid",
            title=valid_task.title,
            objective=valid_task.objective,
            context=valid_task.context,
            allowlist=valid_task.allowlist,
            forbidden=valid_task.forbidden,
            technical_constraints=valid_task.technical_constraints,
            acceptance_criteria=valid_task.acceptance_criteria,
            created_at_utc=valid_task.created_at_utc,
        )
        result = validate_task(task)
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT


# =============================================================================
# ADR TESTS
# =============================================================================


class TestValidateAdr:
    """Tests for validate_adr."""

    def test_valid_adr(self, valid_adr: ADR, v1_schema: SnapshotSchema) -> None:
        """Valid ADR passes validation."""
        result = validate_adr(valid_adr, v1_schema)
        assert result is None

    def test_invalid_uid_format(self, valid_adr: ADR, v1_schema: SnapshotSchema) -> None:
        """Invalid UID format fails."""
        adr = ADR(
            uid="invalid-uid",
            title=valid_adr.title,
            category=valid_adr.category,
            date_utc=valid_adr.date_utc,
            previous_uid=valid_adr.previous_uid,
            snapshot=valid_adr.snapshot,
            changes_in_this_version=valid_adr.changes_in_this_version,
            context=valid_adr.context,
            decision=valid_adr.decision,
            rationale=valid_adr.rationale,
            alternatives=valid_adr.alternatives,
            consequences_positive=valid_adr.consequences_positive,
            consequences_negative=valid_adr.consequences_negative,
            consequences_neutral=valid_adr.consequences_neutral,
        )
        result = validate_adr(adr, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_empty_context(self, valid_adr: ADR, v1_schema: SnapshotSchema) -> None:
        """Empty context fails."""
        adr = ADR(
            uid=valid_adr.uid,
            title=valid_adr.title,
            category=valid_adr.category,
            date_utc=valid_adr.date_utc,
            previous_uid=valid_adr.previous_uid,
            snapshot=valid_adr.snapshot,
            changes_in_this_version=valid_adr.changes_in_this_version,
            context="",  # Empty
            decision=valid_adr.decision,
            rationale=valid_adr.rationale,
            alternatives=valid_adr.alternatives,
            consequences_positive=valid_adr.consequences_positive,
            consequences_negative=valid_adr.consequences_negative,
            consequences_neutral=valid_adr.consequences_neutral,
        )
        result = validate_adr(adr, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert "context" in result.message

    def test_empty_alternatives(self, valid_adr: ADR, v1_schema: SnapshotSchema) -> None:
        """Empty alternatives fails."""
        adr = ADR(
            uid=valid_adr.uid,
            title=valid_adr.title,
            category=valid_adr.category,
            date_utc=valid_adr.date_utc,
            previous_uid=valid_adr.previous_uid,
            snapshot=valid_adr.snapshot,
            changes_in_this_version=valid_adr.changes_in_this_version,
            context=valid_adr.context,
            decision=valid_adr.decision,
            rationale=valid_adr.rationale,
            alternatives=(),  # Empty
            consequences_positive=valid_adr.consequences_positive,
            consequences_negative=valid_adr.consequences_negative,
            consequences_neutral=valid_adr.consequences_neutral,
        )
        result = validate_adr(adr, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert "alternatives" in result.message

    def test_empty_changes(self, valid_adr: ADR, v1_schema: SnapshotSchema) -> None:
        """Empty changes_in_this_version fails."""
        adr = ADR(
            uid=valid_adr.uid,
            title=valid_adr.title,
            category=valid_adr.category,
            date_utc=valid_adr.date_utc,
            previous_uid=valid_adr.previous_uid,
            snapshot=valid_adr.snapshot,
            changes_in_this_version=(),  # Empty
            context=valid_adr.context,
            decision=valid_adr.decision,
            rationale=valid_adr.rationale,
            alternatives=valid_adr.alternatives,
            consequences_positive=valid_adr.consequences_positive,
            consequences_negative=valid_adr.consequences_negative,
            consequences_neutral=valid_adr.consequences_neutral,
        )
        result = validate_adr(adr, v1_schema)
        assert result is not None
        assert result.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert "changes" in result.message
