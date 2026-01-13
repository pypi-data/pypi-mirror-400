"""Tests for adr_builder module."""

from __future__ import annotations

import pytest

from preflights.core.adr_builder import (
    build_adr,
    generate_adr_title,
    generate_changes_description,
    generate_context,
    generate_decision,
    generate_rationale,
)
from preflights.core.types import (
    ADR,
    ArchitectureState,
    DecisionPatch,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def valid_uid() -> str:
    """Valid UID."""
    return "20250106T120000.000Z"


@pytest.fixture
def auth_patch() -> DecisionPatch:
    """Authentication patch."""
    return DecisionPatch(
        category="Authentication",
        fields=(("Strategy", "OAuth"), ("Library", "next-auth")),
    )


@pytest.fixture
def auth_snapshot(valid_uid: str) -> ArchitectureState:
    """Architecture snapshot with auth."""
    return ArchitectureState(
        uid=valid_uid,
        schema_version="v1",
        categories=(
            (
                "Authentication",
                (
                    ("Strategy", f"OAuth (ADR {valid_uid})"),
                    ("Library", f"next-auth (ADR {valid_uid})"),
                ),
            ),
        ),
    )


@pytest.fixture
def previous_snapshot() -> ArchitectureState:
    """Previous architecture snapshot."""
    return ArchitectureState(
        uid="20250106T100000.000Z",
        schema_version="v1",
        categories=(
            ("Authentication", (("Strategy", "Email/Password (ADR 20250106T100000.000Z)"),)),
        ),
    )


# =============================================================================
# BUILD ADR TESTS
# =============================================================================


class TestBuildAdr:
    """Tests for build_adr function."""

    def test_build_adr_basic(
        self,
        valid_uid: str,
        auth_patch: DecisionPatch,
        auth_snapshot: ArchitectureState,
    ) -> None:
        """Build basic ADR."""
        adr = build_adr(
            uid=valid_uid,
            date_utc="2025-01-06",
            title="OAuth Authentication Strategy",
            category="Authentication",
            decision_patch=auth_patch,
            new_snapshot=auth_snapshot,
            previous_uid=None,
            context="Need user authentication",
            decision="Use OAuth with Google",
            rationale="Standard, secure, no password management",
            alternatives=("Email/Password - rejected",),
            consequences_positive=("No password storage",),
            consequences_negative=("Requires Google account",),
            consequences_neutral=("Need OAuth credentials",),
            changes_in_this_version=("Added: Authentication.Strategy = OAuth",),
        )

        assert adr.uid == valid_uid
        assert adr.title == "OAuth Authentication Strategy"
        assert adr.category == "Authentication"
        assert adr.snapshot == auth_snapshot
        assert len(adr.alternatives) == 1
        assert adr.supersedes_uid is None

    def test_build_adr_with_previous(
        self,
        valid_uid: str,
        auth_patch: DecisionPatch,
        auth_snapshot: ArchitectureState,
    ) -> None:
        """Build ADR with previous reference."""
        previous_uid = "20250106T100000.000Z"
        adr = build_adr(
            uid=valid_uid,
            date_utc="2025-01-06",
            title="Update Auth Strategy",
            category="Authentication",
            decision_patch=auth_patch,
            new_snapshot=auth_snapshot,
            previous_uid=previous_uid,
            context="Changing auth strategy",
            decision="Switch to OAuth",
            rationale="Better UX",
            alternatives=("Keep email/password",),
            consequences_positive=("Simpler login",),
            consequences_negative=(),
            consequences_neutral=(),
            changes_in_this_version=("Modified: Authentication.Strategy",),
        )

        assert adr.previous_uid == previous_uid

    def test_build_adr_supersedes(
        self,
        valid_uid: str,
        auth_patch: DecisionPatch,
        auth_snapshot: ArchitectureState,
    ) -> None:
        """Build ADR that supersedes another."""
        superseded_uid = "20250106T080000.000Z"
        adr = build_adr(
            uid=valid_uid,
            date_utc="2025-01-06",
            title="New Auth Strategy",
            category="Authentication",
            decision_patch=auth_patch,
            new_snapshot=auth_snapshot,
            previous_uid="20250106T100000.000Z",
            context="Superseding previous auth decision",
            decision="Use OAuth",
            rationale="Previous decision was wrong",
            alternatives=("Keep previous",),
            consequences_positive=("Better approach",),
            consequences_negative=(),
            consequences_neutral=(),
            changes_in_this_version=("Supersedes ADR-080",),
            supersedes_uid=superseded_uid,
        )

        assert adr.supersedes_uid == superseded_uid


# =============================================================================
# GENERATE TITLE TESTS
# =============================================================================


class TestGenerateAdrTitle:
    """Tests for generate_adr_title function."""

    def test_generate_title_with_fields(self, auth_patch: DecisionPatch) -> None:
        """Generate title from patch fields."""
        result = generate_adr_title("Authentication", auth_patch)

        assert "Authentication" in result
        assert "Strategy" in result
        assert "OAuth" in result

    def test_generate_title_empty_fields(self) -> None:
        """Generate title with empty fields."""
        patch = DecisionPatch(category="Frontend", fields=())
        result = generate_adr_title("Frontend", patch)

        assert result == "Frontend Decision"


# =============================================================================
# GENERATE CONTEXT TESTS
# =============================================================================


class TestGenerateContext:
    """Tests for generate_context function."""

    def test_generate_context(self) -> None:
        """Generate context includes category and intention."""
        result = generate_context("Add OAuth login", "Authentication")

        assert "Authentication" in result
        assert "Add OAuth login" in result


# =============================================================================
# GENERATE DECISION TESTS
# =============================================================================


class TestGenerateDecision:
    """Tests for generate_decision function."""

    def test_generate_decision(self, auth_patch: DecisionPatch) -> None:
        """Generate decision from patch."""
        result = generate_decision(auth_patch)

        assert "Authentication" in result
        assert "Strategy: OAuth" in result
        assert "Library: next-auth" in result


# =============================================================================
# GENERATE RATIONALE TESTS
# =============================================================================


class TestGenerateRationale:
    """Tests for generate_rationale function."""

    def test_generate_rationale(self, auth_patch: DecisionPatch) -> None:
        """Generate rationale includes category."""
        result = generate_rationale(auth_patch)

        assert "Authentication" in result


# =============================================================================
# GENERATE CHANGES DESCRIPTION TESTS
# =============================================================================


class TestGenerateChangesDescription:
    """Tests for generate_changes_description function."""

    def test_changes_added(self, auth_patch: DecisionPatch, valid_uid: str) -> None:
        """Detect added fields."""
        result = generate_changes_description(None, auth_patch, valid_uid)

        assert len(result) == 2
        assert all("Added" in c for c in result)

    def test_changes_modified(
        self, auth_patch: DecisionPatch, previous_snapshot: ArchitectureState, valid_uid: str
    ) -> None:
        """Detect modified fields."""
        result = generate_changes_description(previous_snapshot, auth_patch, valid_uid)

        # Strategy was modified (Email/Password -> OAuth)
        # Library was added
        assert any("Modified" in c and "Strategy" in c for c in result)
        assert any("Added" in c and "Library" in c for c in result)
