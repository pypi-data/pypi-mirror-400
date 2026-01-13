"""Shared fixtures for Core tests.

Provides reusable, deterministic fixtures for testing.
All fixtures are pure data (no I/O, no mocks).
"""

from __future__ import annotations

import pytest

from preflights.core.types import (
    ArchitectureState,
    DecisionPatch,
    FileContext,
    HeuristicsConfig,
    Intention,
    SnapshotSchema,
    default_v1_heuristics,
    default_v1_schema,
)


# =============================================================================
# CORE FIXTURES
# =============================================================================


@pytest.fixture
def schema() -> SnapshotSchema:
    """Default V1 schema."""
    return default_v1_schema()


@pytest.fixture
def heuristics() -> HeuristicsConfig:
    """Default V1 heuristics."""
    return default_v1_heuristics()


# =============================================================================
# VALID UIDs (deterministic)
# =============================================================================


@pytest.fixture
def valid_uid_adr() -> str:
    """A valid ADR UID."""
    return "20250106T120000.000Z"


@pytest.fixture
def valid_uid_task() -> str:
    """A valid Task UID."""
    return "20250106T120000.001Z"


@pytest.fixture
def valid_now_utc() -> str:
    """A valid UTC timestamp."""
    return "2025-01-06T12:00:00Z"


@pytest.fixture
def previous_uid() -> str:
    """A previous ADR UID for testing updates."""
    return "20250106T100000.000Z"


# =============================================================================
# CATEGORY-SPECIFIC FIXTURES
# =============================================================================


@pytest.fixture
def auth_intention() -> Intention:
    """Authentication-related intention."""
    return Intention(text="Add OAuth authentication")


@pytest.fixture
def auth_file_context() -> FileContext:
    """Authentication-related file context."""
    return FileContext(
        paths=("src/auth/login.ts", "src/auth/session.ts"),
        high_level_dirs=("src/auth/",),
    )


@pytest.fixture
def auth_patch() -> DecisionPatch:
    """Authentication decision patch."""
    return DecisionPatch(
        category="Authentication",
        fields=(("Strategy", "OAuth"), ("Library", "next-auth")),
    )


@pytest.fixture
def database_intention() -> Intention:
    """Database-related intention."""
    return Intention(text="Add PostgreSQL database for users")


@pytest.fixture
def database_file_context() -> FileContext:
    """Database-related file context."""
    return FileContext(
        paths=("src/db/connection.ts", "src/db/models/user.ts"),
        high_level_dirs=("src/db/",),
    )


@pytest.fixture
def database_patch() -> DecisionPatch:
    """Database decision patch."""
    return DecisionPatch(
        category="Database",
        fields=(("Type", "PostgreSQL"), ("ORM", "Prisma")),
    )


@pytest.fixture
def frontend_intention() -> Intention:
    """Frontend-related intention."""
    return Intention(text="Add React for UI components")


@pytest.fixture
def frontend_file_context() -> FileContext:
    """Frontend-related file context."""
    return FileContext(
        paths=("src/components/App.tsx", "src/components/Button.tsx"),
        high_level_dirs=("src/components/",),
    )


@pytest.fixture
def frontend_patch() -> DecisionPatch:
    """Frontend decision patch."""
    return DecisionPatch(
        category="Frontend",
        fields=(("Framework", "React"), ("Styling", "Tailwind")),
    )


@pytest.fixture
def backend_intention() -> Intention:
    """Backend-related intention."""
    return Intention(text="Add FastAPI for REST API")


@pytest.fixture
def backend_file_context() -> FileContext:
    """Backend-related file context."""
    return FileContext(
        paths=("src/api/routes.py", "src/api/handlers.py"),
        high_level_dirs=("src/api/",),
    )


@pytest.fixture
def backend_patch() -> DecisionPatch:
    """Backend decision patch."""
    return DecisionPatch(
        category="Backend",
        fields=(("Framework", "FastAPI"), ("API_Style", "REST")),
    )


@pytest.fixture
def infra_intention() -> Intention:
    """Infrastructure-related intention."""
    return Intention(text="Add Docker for containerization")


@pytest.fixture
def infra_file_context() -> FileContext:
    """Infrastructure-related file context."""
    return FileContext(
        paths=("Dockerfile", "docker-compose.yml"),
        high_level_dirs=("infra/",),
    )


@pytest.fixture
def infra_patch() -> DecisionPatch:
    """Infrastructure decision patch."""
    return DecisionPatch(
        category="Infra",
        fields=(("Hosting", "Docker"), ("CI_CD", "GitHub Actions")),
    )


# =============================================================================
# SIMPLE/NON-ADR FIXTURES
# =============================================================================


@pytest.fixture
def simple_fix_intention() -> Intention:
    """Simple fix intention (no ADR needed)."""
    return Intention(text="Fix typo in button text")


@pytest.fixture
def simple_file_context() -> FileContext:
    """Simple file context for non-ADR tasks."""
    return FileContext(paths=("src/components/Button.tsx",))


# =============================================================================
# EXISTING ARCHITECTURE FIXTURES
# =============================================================================


@pytest.fixture
def existing_database_architecture(previous_uid: str) -> ArchitectureState:
    """Existing architecture with Database category."""
    return ArchitectureState(
        uid=previous_uid,
        schema_version="v1",
        categories=(
            ("Database", (("Type", f"PostgreSQL (ADR {previous_uid})"),)),
        ),
    )


@pytest.fixture
def existing_auth_architecture(previous_uid: str) -> ArchitectureState:
    """Existing architecture with Authentication category."""
    return ArchitectureState(
        uid=previous_uid,
        schema_version="v1",
        categories=(
            (
                "Authentication",
                (
                    ("Strategy", f"Email/Password (ADR {previous_uid})"),
                    ("Library", f"passport (ADR {previous_uid})"),
                ),
            ),
        ),
    )


@pytest.fixture
def existing_multi_category_architecture(previous_uid: str) -> ArchitectureState:
    """Existing architecture with multiple categories."""
    return ArchitectureState(
        uid=previous_uid,
        schema_version="v1",
        categories=(
            ("Authentication", (("Strategy", f"OAuth (ADR {previous_uid})"),)),
            ("Database", (("Type", f"PostgreSQL (ADR {previous_uid})"),)),
            ("Frontend", (("Framework", f"React (ADR {previous_uid})"),)),
        ),
    )
