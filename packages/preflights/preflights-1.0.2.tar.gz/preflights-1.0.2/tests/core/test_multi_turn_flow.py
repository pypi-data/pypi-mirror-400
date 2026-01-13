"""Tests du flux complet multi-tour.

Ces tests vérifient le contrat Core :
NeedsClarification → ReadyToBuild → Completed
"""

from __future__ import annotations

import pytest

from preflights.core.process import process
from preflights.core.types import (
    ArchitectureState,
    Completed,
    DecisionPatch,
    FileContext,
    HeuristicsConfig,
    Intention,
    NeedsClarification,
    ReadyToBuild,
    default_v1_heuristics,
)


@pytest.fixture
def heuristics() -> HeuristicsConfig:
    """Default V1 heuristics."""
    return default_v1_heuristics()


# =============================================================================
# FLUX COMPLET AVEC ADR
# =============================================================================


class TestMultiTurnFlowWithAdr:
    """Flux complet pour une décision architecturale (avec ADR)."""

    def test_full_flow_auth_decision(self, heuristics: HeuristicsConfig) -> None:
        """Tour 1 → 2 → 3 pour une décision auth."""
        intention = Intention(text="Add OAuth authentication")
        file_context = FileContext(
            paths=("src/auth/login.ts", "src/auth/session.ts"),
            high_level_dirs=("src/auth/",),
        )

        # =========================================================
        # TOUR 1 : Sans patch → NeedsClarification
        # =========================================================
        result1 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result1, NeedsClarification)
        assert len(result1.questions) > 0

        # Vérifier qu'on a des questions auth - auth_strategy est obligatoire pour intentions auth
        question_ids = {q.id for q in result1.questions}
        assert "auth_strategy" in question_ids, f"Expected auth_strategy question for auth intention, got: {question_ids}"

        # =========================================================
        # TOUR 2 : Avec patch, sans UIDs → ReadyToBuild
        # =========================================================
        patch = DecisionPatch(
            category="Authentication",
            fields=(("Strategy", "OAuth"), ("Library", "next-auth")),
        )

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
        assert result2.category == "Authentication"

        # ReadyToBuild doit contenir assez d'info pour le tour 3
        assert result2.title != ""
        assert len(result2.allowlist) > 0
        assert result2.decision_context != ""
        assert result2.decision_text != ""

        # =========================================================
        # TOUR 3 : Avec UIDs → Completed
        # =========================================================
        result3 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr="20250106T120000.000Z",
            uid_for_task="20250106T120000.001Z",
            now_utc="2025-01-06T12:00:00Z",
        )

        assert isinstance(result3, Completed)

        # Task créé avec bon UID
        assert result3.task.uid == "20250106T120000.001Z"
        assert result3.task.related_adr_uid == "20250106T120000.000Z"

        # ADR créé avec bon UID et catégorie
        assert result3.adr is not None
        assert result3.adr.uid == "20250106T120000.000Z"
        assert result3.adr.category == "Authentication"

        # Architecture mise à jour
        assert result3.updated_architecture is not None
        assert result3.updated_architecture.uid == "20250106T120000.000Z"

        # Vérifier que le snapshot contient bien les champs du patch
        cat_dict = {cat[0]: dict(cat[1]) for cat in result3.updated_architecture.categories}
        assert "Authentication" in cat_dict
        assert "Strategy" in cat_dict["Authentication"]
        assert "OAuth" in cat_dict["Authentication"]["Strategy"]

    def test_full_flow_database_decision(self, heuristics: HeuristicsConfig) -> None:
        """Tour 1 → 2 → 3 pour une décision database."""
        intention = Intention(text="Add PostgreSQL database for users")
        file_context = FileContext(
            paths=("src/db/connection.ts", "src/db/models/user.ts"),
            high_level_dirs=("src/db/",),
        )

        # Tour 1
        result1 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )
        assert isinstance(result1, NeedsClarification)

        # Tour 2
        patch = DecisionPatch(
            category="Database",
            fields=(("Type", "PostgreSQL"), ("ORM", "Prisma")),
        )
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
        assert result2.category == "Database"

        # Tour 3
        result3 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr="20250106T130000.000Z",
            uid_for_task="20250106T130000.001Z",
            now_utc="2025-01-06T13:00:00Z",
        )
        assert isinstance(result3, Completed)
        assert result3.adr is not None
        assert result3.adr.category == "Database"


# =============================================================================
# FLUX COMPLET SANS ADR
# =============================================================================


class TestMultiTurnFlowWithoutAdr:
    """Flux complet pour une tâche simple (pas d'ADR)."""

    def test_full_flow_simple_fix(self, heuristics: HeuristicsConfig) -> None:
        """Typo fix ne nécessite pas d'ADR."""
        intention = Intention(text="Fix typo in button text")
        file_context = FileContext(paths=("src/components/Button.tsx",))
        patch = DecisionPatch(category="Frontend", fields=(("Styling", "CSS"),))

        # Tour 1 : Sans patch
        result1 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )
        assert isinstance(result1, NeedsClarification)

        # Tour 2 : Avec patch → ReadyToBuild avec needs_adr=False
        result2 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )
        assert isinstance(result2, ReadyToBuild)
        assert result2.needs_adr is False

        # Tour 3 : Completed SANS ADR
        result3 = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_task="20250106T120000.000Z",
            now_utc="2025-01-06T12:00:00Z",
        )
        assert isinstance(result3, Completed)
        assert result3.task is not None
        assert result3.adr is None
        assert result3.updated_architecture is None


# =============================================================================
# FLUX AVEC ARCHITECTURE EXISTANTE
# =============================================================================


class TestMultiTurnWithExistingArchitecture:
    """Flux avec architecture existante."""

    def test_new_adr_builds_on_existing(self, heuristics: HeuristicsConfig) -> None:
        """Nouvel ADR préserve les catégories existantes."""
        existing = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(
                ("Database", (("Type", "PostgreSQL (ADR 20250106T100000.000Z)"),)),
            ),
        )

        intention = Intention(text="Add OAuth authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        patch = DecisionPatch(category="Authentication", fields=(("Strategy", "OAuth"),))

        result = process(
            intention=intention,
            current_architecture=existing,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr="20250106T120000.000Z",
            uid_for_task="20250106T120000.001Z",
            now_utc="2025-01-06T12:00:00Z",
        )

        assert isinstance(result, Completed)
        assert result.updated_architecture is not None
        assert result.adr is not None

        # L'architecture mise à jour doit avoir LES DEUX catégories
        cat_names = {cat[0] for cat in result.updated_architecture.categories}
        assert "Database" in cat_names
        assert "Authentication" in cat_names

        # Les valeurs Database sont PRÉSERVÉES
        cat_dict = {cat[0]: dict(cat[1]) for cat in result.updated_architecture.categories}
        assert "PostgreSQL" in cat_dict["Database"]["Type"]

        # L'ADR référence le précédent
        assert result.adr.previous_uid == "20250106T100000.000Z"

    def test_modify_existing_category(self, heuristics: HeuristicsConfig) -> None:
        """Modifier une catégorie existante préserve les autres champs."""
        existing = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(
                (
                    "Authentication",
                    (
                        ("Strategy", "Email/Password (ADR 20250106T100000.000Z)"),
                        ("Library", "passport (ADR 20250106T100000.000Z)"),
                    ),
                ),
            ),
        )

        intention = Intention(text="Switch to OAuth authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        patch = DecisionPatch(category="Authentication", fields=(("Strategy", "OAuth"),))

        result = process(
            intention=intention,
            current_architecture=existing,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr="20250106T120000.000Z",
            uid_for_task="20250106T120000.001Z",
            now_utc="2025-01-06T12:00:00Z",
        )

        assert isinstance(result, Completed)
        assert result.updated_architecture is not None

        cat_dict = {cat[0]: dict(cat[1]) for cat in result.updated_architecture.categories}

        # Strategy a été mise à jour
        assert "OAuth" in cat_dict["Authentication"]["Strategy"]
        assert "20250106T120000.000Z" in cat_dict["Authentication"]["Strategy"]

        # Library est PRÉSERVÉE (pas touchée par le patch)
        assert "Library" in cat_dict["Authentication"]
        assert "passport" in cat_dict["Authentication"]["Library"]


# =============================================================================
# CAS D'ERREUR DANS LE FLUX
# =============================================================================


class TestMultiTurnFlowErrors:
    """Erreurs possibles dans le flux multi-tour."""

    def test_error_propagates_cleanly(self, heuristics: HeuristicsConfig) -> None:
        """Une erreur de validation retourne CoreError, pas d'exception."""
        from preflights.core.types import CoreError, ErrorCode

        intention = Intention(text="Add auth")
        file_context = FileContext(paths=("src/auth/",))
        invalid_patch = DecisionPatch(category="UnknownCategory", fields=(("Field", "Value"),))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=invalid_patch,
        )

        assert isinstance(result, CoreError)
        assert result.code == ErrorCode.UNKNOWN_CATEGORY

    def test_skip_ready_to_build_with_uids(self, heuristics: HeuristicsConfig) -> None:
        """On peut passer directement de Tour 1 à Tour 3 si on a déjà les UIDs."""
        intention = Intention(text="Add OAuth authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        patch = DecisionPatch(category="Authentication", fields=(("Strategy", "OAuth"),))

        # Sauter le Tour 2 (ReadyToBuild) en fournissant directement les UIDs
        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr="20250106T120000.000Z",
            uid_for_task="20250106T120000.001Z",
            now_utc="2025-01-06T12:00:00Z",
        )

        # Doit quand même fonctionner
        assert isinstance(result, Completed)
        assert result.adr is not None
