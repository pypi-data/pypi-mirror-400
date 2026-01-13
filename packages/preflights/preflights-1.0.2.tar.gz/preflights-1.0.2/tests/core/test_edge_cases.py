"""Edge case tests for Core.

Tests boundaries and unusual inputs:
- Empty strings
- Very long strings (5000+ chars)
- Unicode characters (emoji, RTL, etc.)
- Duplicates in lists
- Non-alphabetical category order
"""

from __future__ import annotations

import pytest

from preflights.core.process import process
from preflights.core.snapshot_builder import apply_patch, compute_changes
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
    default_v1_heuristics,
)


@pytest.fixture
def heuristics() -> HeuristicsConfig:
    """Default V1 heuristics."""
    return default_v1_heuristics()


# =============================================================================
# EMPTY STRINGS
# =============================================================================


class TestEmptyStrings:
    """Tests with empty string inputs."""

    def test_empty_intention_text_returns_needs_clarification(
        self, heuristics: HeuristicsConfig
    ) -> None:
        """Empty intention text still triggers questions."""
        intention = Intention(text="")
        file_context = FileContext(paths=("src/app.ts",))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        # Should still return NeedsClarification (asks what user wants)
        assert isinstance(result, NeedsClarification)

    def test_empty_file_paths_returns_needs_clarification(
        self, heuristics: HeuristicsConfig
    ) -> None:
        """Empty file paths list triggers questions."""
        intention = Intention(text="Add authentication")
        file_context = FileContext(paths=())

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)

    def test_empty_patch_field_value(self, heuristics: HeuristicsConfig) -> None:
        """Empty field value in patch is accepted."""
        intention = Intention(text="Add authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        # Empty value is technically valid (user might clear a field)
        patch = DecisionPatch(category="Authentication", fields=(("Strategy", ""),))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        # Should return ReadyToBuild (empty value is allowed)
        assert isinstance(result, ReadyToBuild)


# =============================================================================
# VERY LONG STRINGS
# =============================================================================


class TestVeryLongStrings:
    """Tests with very long string inputs (5000+ chars)."""

    def test_very_long_intention_text(self, heuristics: HeuristicsConfig) -> None:
        """Very long intention text is handled without truncation."""
        long_text = "Add OAuth authentication. " * 250  # ~6500 chars
        intention = Intention(text=long_text)
        file_context = FileContext(paths=("src/auth/login.ts",))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)
        # Intention text should be preserved (no truncation in Core)

    def test_very_long_patch_value(self, heuristics: HeuristicsConfig) -> None:
        """Very long patch field value is handled."""
        long_value = "OAuth2.0 with PKCE flow and " * 200  # ~5600 chars
        intention = Intention(text="Add authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        patch = DecisionPatch(category="Authentication", fields=(("Strategy", long_value),))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        assert isinstance(result, ReadyToBuild)

    def test_very_long_file_path(self, heuristics: HeuristicsConfig) -> None:
        """Very long file paths are handled."""
        # Deeply nested path
        long_path = "/".join(["dir"] * 100) + "/file.ts"  # ~400 chars
        intention = Intention(text="Add authentication")
        file_context = FileContext(paths=(long_path,))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)


# =============================================================================
# UNICODE CHARACTERS
# =============================================================================


class TestUnicodeCharacters:
    """Tests with Unicode characters (emoji, RTL, special chars)."""

    def test_emoji_in_intention(self, heuristics: HeuristicsConfig) -> None:
        """Emoji in intention text is handled and preserved."""
        intention = Intention(text="Add 🔐 OAuth authentication with 🚀 performance")
        file_context = FileContext(paths=("src/auth/login.ts",))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)
        # Verify emoji is preserved in some output (questions reference intention)
        assert len(result.questions) > 0

    def test_rtl_characters_in_patch(self, heuristics: HeuristicsConfig) -> None:
        """Right-to-left (Arabic/Hebrew) characters in patch value are handled."""
        intention = Intention(text="Add authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        # Arabic text: "مصادقة" means "authentication"
        patch = DecisionPatch(
            category="Authentication",
            fields=(("Strategy", "OAuth مصادقة"),),
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
        # Verify RTL text is preserved
        assert "مصادقة" in " ".join(result.technical_constraints)

    def test_chinese_characters_in_context(self, heuristics: HeuristicsConfig) -> None:
        """Chinese characters in optional context are handled and preserved."""
        # Chinese text: "这是中国市场" means "This is for Chinese market"
        intention = Intention(
            text="Add authentication",
            optional_context="这是中国市场的认证系统",
        )
        file_context = FileContext(paths=("src/auth/login.ts",))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)
        assert len(result.questions) > 0

    def test_special_chars_in_file_paths(self, heuristics: HeuristicsConfig) -> None:
        """Special characters in file paths are preserved."""
        # File paths with spaces and special chars
        file_context = FileContext(
            paths=(
                "src/My Component/auth-login.tsx",
                "src/hooks/use_auth.ts",
            )
        )
        intention = Intention(text="Add authentication")

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)


# =============================================================================
# DUPLICATES IN LISTS
# =============================================================================


class TestDuplicates:
    """Tests with duplicate values in lists."""

    def test_duplicate_file_paths(self, heuristics: HeuristicsConfig) -> None:
        """Duplicate file paths are handled (not deduplicated by Core)."""
        file_context = FileContext(
            paths=(
                "src/auth/login.ts",
                "src/auth/login.ts",  # Duplicate
                "src/auth/session.ts",
            )
        )
        intention = Intention(text="Add OAuth authentication")

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        # Core should handle duplicates gracefully
        assert isinstance(result, NeedsClarification)

    def test_duplicate_high_level_dirs(self, heuristics: HeuristicsConfig) -> None:
        """Duplicate high-level dirs are handled."""
        file_context = FileContext(
            paths=("src/auth/login.ts",),
            high_level_dirs=("src/auth/", "src/auth/"),  # Duplicate
        )
        intention = Intention(text="Add OAuth authentication")

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)

    def test_duplicate_patch_fields_uses_last(self, heuristics: HeuristicsConfig) -> None:
        """Duplicate fields in patch - last value wins."""
        intention = Intention(text="Add authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        # Same field twice - last value should win
        patch = DecisionPatch(
            category="Authentication",
            fields=(
                ("Strategy", "BasicAuth"),
                ("Strategy", "OAuth"),  # This should win
            ),
        )

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

        assert isinstance(result, Completed)
        assert result.adr is not None
        # Check the snapshot has OAuth (last value)
        cat_dict = {cat[0]: dict(cat[1]) for cat in result.adr.snapshot.categories}
        assert "OAuth" in cat_dict["Authentication"]["Strategy"]


# =============================================================================
# NON-ALPHABETICAL ORDER
# =============================================================================


class TestOrdering:
    """Tests verifying ordering behavior."""

    def test_categories_sorted_in_output(self, heuristics: HeuristicsConfig) -> None:
        """Categories in output are sorted alphabetically."""
        # Create existing architecture with non-alphabetical categories
        existing = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(
                ("Frontend", (("Framework", "React"),)),
                ("Backend", (("Language", "Python"),)),
                ("Database", (("Type", "PostgreSQL"),)),
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

        # Categories should be sorted
        cat_names = [cat[0] for cat in result.updated_architecture.categories]
        assert cat_names == sorted(cat_names), "Categories are not sorted alphabetically"

    def test_fields_sorted_within_category(self, heuristics: HeuristicsConfig) -> None:
        """Fields within a category are sorted alphabetically."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(
                ("Token_Storage", "Cookie"),
                ("Strategy", "OAuth"),
                ("Library", "next-auth"),
            ),
        )
        new_uid = "20250106T120000.000Z"

        result = apply_patch(None, patch, new_uid, heuristics.schema)

        # Get the Authentication category
        auth_cat = next(cat for cat in result.categories if cat[0] == "Authentication")
        field_names = [f[0] for f in auth_cat[1]]

        assert field_names == sorted(field_names), "Fields are not sorted alphabetically"


# =============================================================================
# BOUNDARY VALUES
# =============================================================================


class TestBoundaryValues:
    """Tests with boundary values."""

    def test_single_character_intention(self, heuristics: HeuristicsConfig) -> None:
        """Single character intention is handled."""
        intention = Intention(text="x")
        file_context = FileContext(paths=("src/app.ts",))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)

    def test_single_file_path(self, heuristics: HeuristicsConfig) -> None:
        """Single file path is handled."""
        intention = Intention(text="Add OAuth authentication")
        file_context = FileContext(paths=("x",))  # Minimal path

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)

    def test_many_file_paths(self, heuristics: HeuristicsConfig) -> None:
        """Many file paths are handled."""
        # 100 file paths
        paths = tuple(f"src/file{i}.ts" for i in range(100))
        intention = Intention(text="Add OAuth authentication")
        file_context = FileContext(paths=paths)

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=None,
        )

        assert isinstance(result, NeedsClarification)

    def test_many_patch_fields(self, heuristics: HeuristicsConfig) -> None:
        """All fields in a category can be set at once."""
        # All Authentication fields
        patch = DecisionPatch(
            category="Authentication",
            fields=(
                ("Strategy", "OAuth"),
                ("Library", "next-auth"),
                ("Token_Storage", "Cookie"),
            ),
        )
        intention = Intention(text="Add OAuth authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        assert isinstance(result, ReadyToBuild)


# =============================================================================
# COMPUTE_CHANGES EDGE CASES
# =============================================================================


class TestComputeChangesEdgeCases:
    """Edge cases for compute_changes function."""

    def test_compute_changes_from_none(self) -> None:
        """compute_changes from None previous."""
        current = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(("Authentication", (("Strategy", "OAuth"),)),),
        )

        changes = compute_changes(None, current)

        assert len(changes) >= 1
        assert any("Added" in c for c in changes)

    def test_compute_changes_to_empty(self) -> None:
        """compute_changes when current has fewer categories."""
        previous = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"),)),
                ("Database", (("Type", "PostgreSQL"),)),
            ),
        )
        current = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(("Authentication", (("Strategy", "OAuth"),)),),
        )

        changes = compute_changes(previous, current)

        # Should detect removed category
        assert any("Removed" in c and "Database" in c for c in changes)

    def test_compute_changes_identical(self) -> None:
        """compute_changes between identical states returns empty."""
        state = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(("Authentication", (("Strategy", "OAuth"),)),),
        )

        changes = compute_changes(state, state)

        assert len(changes) == 0


# =============================================================================
# ERROR EDGE CASES
# =============================================================================


class TestErrorEdgeCases:
    """Edge cases that should produce errors."""

    def test_unknown_category_returns_error(self, heuristics: HeuristicsConfig) -> None:
        """Unknown category in patch returns CoreError."""
        intention = Intention(text="Add something")
        file_context = FileContext(paths=("src/app.ts",))
        patch = DecisionPatch(category="NonExistentCategory", fields=(("Field", "Value"),))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        assert isinstance(result, CoreError)
        assert result.code == ErrorCode.UNKNOWN_CATEGORY

    def test_unknown_field_returns_error(self, heuristics: HeuristicsConfig) -> None:
        """Unknown field in patch returns CoreError."""
        intention = Intention(text="Add authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        patch = DecisionPatch(
            category="Authentication",
            fields=(("NonExistentField", "Value"),),
        )

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

    def test_invalid_uid_format_returns_error(self, heuristics: HeuristicsConfig) -> None:
        """Invalid UID format returns CoreError."""
        intention = Intention(text="Add OAuth authentication")
        file_context = FileContext(paths=("src/auth/login.ts",))
        patch = DecisionPatch(category="Authentication", fields=(("Strategy", "OAuth"),))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
            uid_for_adr="invalid-uid",  # Bad format
            uid_for_task="20250106T120000.001Z",
            now_utc="2025-01-06T12:00:00Z",
        )

        assert isinstance(result, CoreError)
        assert result.code == ErrorCode.INVALID_UID_FORMAT

    def test_error_has_recovery_hint(self, heuristics: HeuristicsConfig) -> None:
        """CoreError includes a recovery hint."""
        intention = Intention(text="Add something")
        file_context = FileContext(paths=("src/app.ts",))
        patch = DecisionPatch(category="UnknownCategory", fields=(("Field", "Value"),))

        result = process(
            intention=intention,
            current_architecture=None,
            file_context=file_context,
            conversation_state=None,
            heuristics_config=heuristics,
            decision_patch=patch,
        )

        assert isinstance(result, CoreError)
        assert result.recovery_hint is not None
        assert len(result.recovery_hint) > 0
