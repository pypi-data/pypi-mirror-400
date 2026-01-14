"""Tests for decision_detector module."""

from __future__ import annotations

import pytest

from preflights.core.decision_detector import (
    ADRDecision,
    detect_adr_need,
    extract_category_from_intention,
)
from preflights.core.types import (
    ArchitectureState,
    DecisionPatch,
    HeuristicsConfig,
    Intention,
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
def auth_patch() -> DecisionPatch:
    """Authentication patch."""
    return DecisionPatch(
        category="Authentication",
        fields=(("Strategy", "OAuth"),),
    )


@pytest.fixture
def existing_auth_architecture() -> ArchitectureState:
    """Architecture with existing Authentication category."""
    return ArchitectureState(
        uid="20250106T100000.000Z",
        schema_version="v1",
        categories=(
            ("Authentication", (("Strategy", "Email/Password"),)),
        ),
    )


# =============================================================================
# DETECT ADR NEED TESTS
# =============================================================================


class TestDetectAdrNeed:
    """Tests for detect_adr_need function."""

    def test_keyword_trigger_auth(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """Keyword 'auth' triggers ADR."""
        intention = Intention(text="Add auth to the application")
        result = detect_adr_need(intention, auth_patch, heuristics)

        assert result.needs_adr is True
        assert result.category == "Authentication"
        assert any("keyword:auth" in t for t in result.triggered_by)

    def test_keyword_trigger_database(
        self, heuristics: HeuristicsConfig
    ) -> None:
        """Keyword 'database' triggers ADR."""
        intention = Intention(text="Add a database for storing users")
        patch = DecisionPatch(category="Database", fields=(("Type", "PostgreSQL"),))
        result = detect_adr_need(intention, patch, heuristics)

        assert result.needs_adr is True
        assert result.category == "Database"
        assert any("keyword:database" in t for t in result.triggered_by)

    def test_non_trigger_bugfix(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """Non-trigger 'bugfix' prevents ADR."""
        intention = Intention(text="Bugfix for auth token refresh")
        result = detect_adr_need(intention, auth_patch, heuristics)

        assert result.needs_adr is False
        assert "non-trigger" in result.rationale.lower()

    def test_non_trigger_typo(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """Non-trigger 'typo' prevents ADR."""
        intention = Intention(text="Fix typo in login form")
        result = detect_adr_need(intention, auth_patch, heuristics)

        assert result.needs_adr is False

    def test_non_trigger_refactor(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """Non-trigger 'refactor' prevents ADR."""
        intention = Intention(text="Refactor auth module")
        result = detect_adr_need(intention, auth_patch, heuristics)

        assert result.needs_adr is False

    def test_modifies_existing_category(
        self,
        heuristics: HeuristicsConfig,
        auth_patch: DecisionPatch,
        existing_auth_architecture: ArchitectureState,
    ) -> None:
        """Modifying existing category triggers ADR."""
        intention = Intention(text="Change login method")  # No direct keyword
        result = detect_adr_need(
            intention, auth_patch, heuristics, existing_auth_architecture
        )

        assert result.needs_adr is True
        assert any("modifies_existing_category" in t for t in result.triggered_by)

    def test_file_impact_threshold(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """High file impact triggers ADR."""
        intention = Intention(text="Update login flow")
        metadata = (("estimated_file_impact", "15"),)
        result = detect_adr_need(intention, auth_patch, heuristics, metadata=metadata)

        assert result.needs_adr is True
        assert any("file_impact:15" in t for t in result.triggered_by)

    def test_file_impact_below_threshold(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """Low file impact doesn't trigger ADR on its own."""
        intention = Intention(text="Update button color")  # No keywords
        patch = DecisionPatch(category="Frontend", fields=(("Styling", "Tailwind"),))
        metadata = (("estimated_file_impact", "3"),)
        result = detect_adr_need(intention, patch, heuristics, metadata=metadata)

        assert result.needs_adr is False

    def test_new_dependencies(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """New dependencies triggers ADR."""
        intention = Intention(text="Add login feature")
        metadata = (("new_dependencies", "next-auth"),)
        result = detect_adr_need(intention, auth_patch, heuristics, metadata=metadata)

        assert result.needs_adr is True
        assert "new_dependencies" in result.triggered_by

    def test_explicit_architecture_keyword(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """Explicit 'architecture' keyword triggers ADR."""
        intention = Intention(text="Define the architecture for user management")
        result = detect_adr_need(intention, auth_patch, heuristics)

        assert result.needs_adr is True
        assert any("explicit:architecture" in t for t in result.triggered_by)

    def test_explicit_strategy_keyword(
        self, heuristics: HeuristicsConfig, auth_patch: DecisionPatch
    ) -> None:
        """Explicit 'strategy' keyword triggers ADR."""
        intention = Intention(text="Define caching strategy")
        patch = DecisionPatch(category="Infra", fields=(("Caching", "Redis"),))
        result = detect_adr_need(intention, patch, heuristics)

        assert result.needs_adr is True
        assert any("explicit:strategy" in t for t in result.triggered_by)

    def test_no_triggers(self, heuristics: HeuristicsConfig) -> None:
        """No triggers means no ADR."""
        intention = Intention(text="Update button styling")
        patch = DecisionPatch(category="Frontend", fields=(("Styling", "CSS"),))
        result = detect_adr_need(intention, patch, heuristics)

        assert result.needs_adr is False
        assert result.category is None
        assert len(result.triggered_by) == 0

    def test_multiple_triggers(
        self,
        heuristics: HeuristicsConfig,
        auth_patch: DecisionPatch,
        existing_auth_architecture: ArchitectureState,
    ) -> None:
        """Multiple triggers are all recorded."""
        intention = Intention(text="Change auth strategy")
        metadata = (("estimated_file_impact", "20"),)
        result = detect_adr_need(
            intention,
            auth_patch,
            heuristics,
            existing_auth_architecture,
            metadata,
        )

        assert result.needs_adr is True
        # Should have keyword, modifies_existing, and file_impact
        assert len(result.triggered_by) >= 2


# =============================================================================
# EXTRACT CATEGORY TESTS
# =============================================================================


class TestExtractCategory:
    """Tests for extract_category_from_intention function."""

    def test_extract_auth_category(self, heuristics: HeuristicsConfig) -> None:
        """Extract Authentication category."""
        intention = Intention(text="Add OAuth login")
        result = extract_category_from_intention(intention, heuristics)
        assert result == "Authentication"

    def test_extract_database_category(self, heuristics: HeuristicsConfig) -> None:
        """Extract Database category."""
        intention = Intention(text="Set up PostgreSQL database")
        result = extract_category_from_intention(intention, heuristics)
        assert result == "Database"

    def test_extract_frontend_category(self, heuristics: HeuristicsConfig) -> None:
        """Extract Frontend category."""
        intention = Intention(text="Add React component library")
        result = extract_category_from_intention(intention, heuristics)
        assert result == "Frontend"

    def test_no_category_match(self, heuristics: HeuristicsConfig) -> None:
        """No match returns None."""
        intention = Intention(text="Update readme file")
        result = extract_category_from_intention(intention, heuristics)
        assert result is None

    def test_highest_score_wins(self, heuristics: HeuristicsConfig) -> None:
        """Category with most keyword matches wins."""
        # "database storage redis" has 2 Database keywords (database, storage, redis)
        # vs 1 Infra keyword (cache/redis)
        intention = Intention(text="Set up database storage with redis")
        result = extract_category_from_intention(intention, heuristics)
        # Database has more matches
        assert result == "Database"
