"""Tests for task_builder module."""

from __future__ import annotations

import pytest

from preflights.core.task_builder import (
    build_task,
    derive_allowlist,
    derive_forbidden,
    generate_objective,
    generate_title,
)
from preflights.core.types import (
    DecisionPatch,
    FileContext,
    Intention,
    Task,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def valid_uid() -> str:
    """Valid UID."""
    return "20250106T120000.000Z"


@pytest.fixture
def auth_file_context() -> FileContext:
    """File context with auth-related paths."""
    return FileContext(
        paths=(
            "src/auth/login.ts",
            "src/auth/session.ts",
            "src/components/LoginButton.tsx",
            "src/pages/login.tsx",
        ),
        high_level_dirs=("src/", "src/auth/", "src/components/", "src/pages/"),
    )


@pytest.fixture
def mixed_file_context() -> FileContext:
    """File context with various paths."""
    return FileContext(
        paths=(
            "src/auth/login.ts",
            "src/db/models/user.ts",
            "src/api/routes/auth.ts",
            "src/components/Button.tsx",
            ".env",
            "node_modules/package/index.js",
        ),
        high_level_dirs=("src/", "src/auth/", "src/db/", "src/api/"),
    )


@pytest.fixture
def auth_patch() -> DecisionPatch:
    """Authentication patch."""
    return DecisionPatch(
        category="Authentication",
        fields=(("Strategy", "OAuth"),),
    )


# =============================================================================
# BUILD TASK TESTS
# =============================================================================


class TestBuildTask:
    """Tests for build_task function."""

    def test_build_task_basic(self, valid_uid: str) -> None:
        """Build basic task."""
        task = build_task(
            uid=valid_uid,
            created_at_utc="2025-01-06T12:00:00Z",
            title="Add OAuth Authentication",
            objective="Implement OAuth login with Google",
            context="User needs social login",
            allowlist=("src/auth/",),
            forbidden=("src/legacy/",),
            technical_constraints=("Use next-auth",),
            acceptance_criteria=("User can login with Google",),
            related_adr_uid=None,
        )

        assert task.uid == valid_uid
        assert task.title == "Add OAuth Authentication"
        assert task.allowlist == ("src/auth/",)
        assert task.related_adr_uid is None

    def test_build_task_with_adr(self, valid_uid: str) -> None:
        """Build task with related ADR."""
        adr_uid = "20250106T110000.000Z"
        task = build_task(
            uid=valid_uid,
            created_at_utc="2025-01-06T12:00:00Z",
            title="Implement OAuth",
            objective="Add OAuth",
            context="See ADR",
            allowlist=("src/",),
            forbidden=(),
            technical_constraints=(),
            acceptance_criteria=("Works",),
            related_adr_uid=adr_uid,
        )

        assert task.related_adr_uid == adr_uid


# =============================================================================
# DERIVE ALLOWLIST TESTS
# =============================================================================


class TestDeriveAllowlist:
    """Tests for derive_allowlist function."""

    def test_derive_allowlist_auth(
        self, auth_file_context: FileContext, auth_patch: DecisionPatch
    ) -> None:
        """Derive allowlist for auth-related intention."""
        intention = Intention(text="Add OAuth authentication")
        result = derive_allowlist(intention, auth_file_context, auth_patch)

        assert result is not None
        assert any("auth" in p.lower() for p in result)

    def test_derive_allowlist_database(
        self, mixed_file_context: FileContext
    ) -> None:
        """Derive allowlist for database-related intention."""
        intention = Intention(text="Add database models")
        patch = DecisionPatch(category="Database", fields=(("Type", "PostgreSQL"),))
        result = derive_allowlist(intention, mixed_file_context, patch)

        assert result is not None
        assert any("db" in p.lower() or "models" in p.lower() for p in result)

    def test_derive_allowlist_empty_context(self) -> None:
        """Return None for empty file context."""
        intention = Intention(text="Add auth")
        context = FileContext(paths=())
        result = derive_allowlist(intention, context, None)

        assert result is None

    def test_derive_allowlist_no_match(self) -> None:
        """Return None when no patterns match."""
        intention = Intention(text="Update readme")
        context = FileContext(paths=("README.md", "package.json"))
        result = derive_allowlist(intention, context, None)

        assert result is None

    def test_derive_allowlist_uses_directories(
        self, auth_file_context: FileContext, auth_patch: DecisionPatch
    ) -> None:
        """Allowlist should contain directories, not individual files."""
        intention = Intention(text="Add auth")
        result = derive_allowlist(intention, auth_file_context, auth_patch)

        assert result is not None
        # Should have directories (ending with /)
        assert any(p.endswith("/") for p in result)


# =============================================================================
# DERIVE FORBIDDEN TESTS
# =============================================================================


class TestDeriveForbidden:
    """Tests for derive_forbidden function."""

    def test_derive_forbidden_common_patterns(
        self, mixed_file_context: FileContext
    ) -> None:
        """Forbidden includes common sensitive patterns."""
        allowlist = ("src/auth/",)
        result = derive_forbidden(allowlist, mixed_file_context)

        # Should include common patterns that exist in context
        assert ".env" in result or any(".env" in p for p in result)

    def test_derive_forbidden_excludes_allowlist(
        self, mixed_file_context: FileContext
    ) -> None:
        """Forbidden should not include allowlist paths."""
        allowlist = ("src/auth/", ".env")
        result = derive_forbidden(allowlist, mixed_file_context)

        assert ".env" not in result


# =============================================================================
# GENERATE TITLE TESTS
# =============================================================================


class TestGenerateTitle:
    """Tests for generate_title function."""

    def test_generate_title_basic(self) -> None:
        """Generate basic title."""
        intention = Intention(text="add oauth authentication")
        result = generate_title(intention, None)

        assert result == "Add oauth authentication"

    def test_generate_title_truncates(self) -> None:
        """Long titles are truncated."""
        long_text = "A" * 100
        intention = Intention(text=long_text)
        result = generate_title(intention, None)

        assert len(result) <= 80
        assert result.endswith("...")


# =============================================================================
# GENERATE OBJECTIVE TESTS
# =============================================================================


class TestGenerateObjective:
    """Tests for generate_objective function."""

    def test_generate_objective_basic(self) -> None:
        """Generate basic objective."""
        intention = Intention(text="Add OAuth login")
        result = generate_objective(intention, None)

        assert result == "Add OAuth login"

    def test_generate_objective_with_patch(self, auth_patch: DecisionPatch) -> None:
        """Objective includes patch information."""
        intention = Intention(text="Add auth")
        result = generate_objective(intention, auth_patch)

        assert "Add auth" in result
        assert "Authentication" in result
        assert "Strategy=OAuth" in result
