"""Tests for snapshot_builder module."""

from __future__ import annotations

import pytest

from preflights.core.snapshot_builder import (
    apply_patch,
    compute_changes,
    merge_snapshots,
)
from preflights.core.types import (
    ArchitectureState,
    DecisionPatch,
    SnapshotSchema,
    default_v1_schema,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def v1_schema() -> SnapshotSchema:
    """Default V1 schema."""
    return default_v1_schema()


@pytest.fixture
def empty_snapshot() -> ArchitectureState:
    """Empty snapshot (no categories)."""
    return ArchitectureState(
        uid=None,
        schema_version="v1",
        categories=(),
    )


@pytest.fixture
def auth_snapshot() -> ArchitectureState:
    """Snapshot with Authentication category."""
    return ArchitectureState(
        uid="20250106T100000.000Z",
        schema_version="v1",
        categories=(
            (
                "Authentication",
                (
                    ("Strategy", "OAuth (ADR 20250106T100000.000Z)"),
                    ("Library", "next-auth (ADR 20250106T100000.000Z)"),
                ),
            ),
        ),
    )


@pytest.fixture
def multi_category_snapshot() -> ArchitectureState:
    """Snapshot with multiple categories."""
    return ArchitectureState(
        uid="20250106T100000.000Z",
        schema_version="v1",
        categories=(
            (
                "Authentication",
                (("Strategy", "OAuth (ADR 20250106T100000.000Z)"),),
            ),
            (
                "Database",
                (("Type", "PostgreSQL (ADR 20250106T100000.000Z)"),),
            ),
        ),
    )


# =============================================================================
# APPLY PATCH TESTS
# =============================================================================


class TestApplyPatch:
    """Tests for apply_patch function."""

    def test_apply_patch_to_empty_snapshot(
        self, v1_schema: SnapshotSchema
    ) -> None:
        """Apply patch to empty snapshot creates new category."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(("Strategy", "OAuth"),),
        )
        result = apply_patch(None, patch, "20250106T120000.000Z", v1_schema)

        assert result.uid == "20250106T120000.000Z"
        assert result.schema_version == "v1"
        assert len(result.categories) == 1
        assert result.categories[0][0] == "Authentication"
        assert ("Strategy", "OAuth (ADR 20250106T120000.000Z)") in result.categories[0][1]

    def test_apply_patch_preserves_existing_categories(
        self, auth_snapshot: ArchitectureState, v1_schema: SnapshotSchema
    ) -> None:
        """Apply patch to new category preserves existing categories."""
        patch = DecisionPatch(
            category="Database",
            fields=(("Type", "PostgreSQL"),),
        )
        result = apply_patch(auth_snapshot, patch, "20250106T120000.000Z", v1_schema)

        # Both categories should exist
        cat_names = [cat[0] for cat in result.categories]
        assert "Authentication" in cat_names
        assert "Database" in cat_names

        # Authentication should still have its fields
        auth_cat = next(cat for cat in result.categories if cat[0] == "Authentication")
        assert ("Strategy", "OAuth (ADR 20250106T100000.000Z)") in auth_cat[1]

    def test_apply_patch_updates_existing_field(
        self, auth_snapshot: ArchitectureState, v1_schema: SnapshotSchema
    ) -> None:
        """Apply patch updates existing field in same category."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(("Strategy", "Email/Password"),),
        )
        result = apply_patch(auth_snapshot, patch, "20250106T120000.000Z", v1_schema)

        auth_cat = next(cat for cat in result.categories if cat[0] == "Authentication")

        # Strategy should be updated
        fields_dict = dict(auth_cat[1])
        assert fields_dict["Strategy"] == "Email/Password (ADR 20250106T120000.000Z)"

        # Library should be preserved
        assert "Library" in fields_dict

    def test_apply_patch_adds_new_field(
        self, auth_snapshot: ArchitectureState, v1_schema: SnapshotSchema
    ) -> None:
        """Apply patch adds new field to existing category."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(("Token_Storage", "httpOnly cookie"),),
        )
        result = apply_patch(auth_snapshot, patch, "20250106T120000.000Z", v1_schema)

        auth_cat = next(cat for cat in result.categories if cat[0] == "Authentication")
        fields_dict = dict(auth_cat[1])

        # New field should exist
        assert fields_dict["Token_Storage"] == "httpOnly cookie (ADR 20250106T120000.000Z)"

        # Existing fields preserved
        assert "Strategy" in fields_dict
        assert "Library" in fields_dict

    def test_apply_patch_case_insensitive_category(
        self, v1_schema: SnapshotSchema
    ) -> None:
        """Category matching is case-insensitive, output uses schema casing."""
        patch = DecisionPatch(
            category="authentication",  # lowercase
            fields=(("Strategy", "OAuth"),),
        )
        result = apply_patch(None, patch, "20250106T120000.000Z", v1_schema)

        # Should use schema casing
        assert result.categories[0][0] == "Authentication"

    def test_apply_patch_case_insensitive_field(
        self, v1_schema: SnapshotSchema
    ) -> None:
        """Field matching is case-insensitive, output uses schema casing."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(("strategy", "OAuth"),),  # lowercase
        )
        result = apply_patch(None, patch, "20250106T120000.000Z", v1_schema)

        auth_cat = result.categories[0]
        fields_dict = dict(auth_cat[1])

        # Should use schema casing
        assert "Strategy" in fields_dict

    def test_apply_patch_multiple_fields(
        self, v1_schema: SnapshotSchema
    ) -> None:
        """Apply patch with multiple fields."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(
                ("Strategy", "OAuth"),
                ("Library", "next-auth"),
                ("Token_Storage", "httpOnly cookie"),
            ),
        )
        result = apply_patch(None, patch, "20250106T120000.000Z", v1_schema)

        auth_cat = result.categories[0]
        fields_dict = dict(auth_cat[1])

        assert len(fields_dict) == 3
        assert "Strategy" in fields_dict
        assert "Library" in fields_dict
        assert "Token_Storage" in fields_dict

    def test_apply_patch_deterministic_ordering(
        self, v1_schema: SnapshotSchema
    ) -> None:
        """Categories and fields are sorted for deterministic output."""
        patch = DecisionPatch(
            category="Authentication",
            fields=(
                ("Token_Storage", "cookie"),
                ("Strategy", "OAuth"),
                ("Library", "next-auth"),
            ),
        )
        result = apply_patch(None, patch, "20250106T120000.000Z", v1_schema)

        # Fields should be sorted alphabetically
        auth_cat = result.categories[0]
        field_names = [f[0] for f in auth_cat[1]]
        assert field_names == sorted(field_names)


# =============================================================================
# MERGE SNAPSHOTS TESTS
# =============================================================================


class TestMergeSnapshots:
    """Tests for merge_snapshots function."""

    def test_merge_disjoint_categories(
        self, auth_snapshot: ArchitectureState
    ) -> None:
        """Merge snapshots with disjoint categories."""
        overlay = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                ("Database", (("Type", "PostgreSQL"),)),
            ),
        )

        result = merge_snapshots(auth_snapshot, overlay)

        cat_names = [cat[0] for cat in result.categories]
        assert "Authentication" in cat_names
        assert "Database" in cat_names

    def test_merge_overlapping_categories(
        self, auth_snapshot: ArchitectureState
    ) -> None:
        """Merge snapshots with overlapping categories, overlay wins."""
        overlay = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "Email/Password"),)),
            ),
        )

        result = merge_snapshots(auth_snapshot, overlay)

        auth_cat = next(cat for cat in result.categories if cat[0] == "Authentication")
        fields_dict = dict(auth_cat[1])

        # Overlay value should win
        assert fields_dict["Strategy"] == "Email/Password"
        # Base value preserved for non-overlapping field
        assert "Library" in fields_dict

    def test_merge_uses_overlay_uid(
        self, auth_snapshot: ArchitectureState
    ) -> None:
        """Merged snapshot uses overlay's UID."""
        overlay = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(),
        )

        result = merge_snapshots(auth_snapshot, overlay)
        assert result.uid == "20250106T120000.000Z"


# =============================================================================
# COMPUTE CHANGES TESTS
# =============================================================================


class TestComputeChanges:
    """Tests for compute_changes function."""

    def test_compute_changes_added_field(self) -> None:
        """Detect added field."""
        previous = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(),
        )
        current = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"),)),
            ),
        )

        changes = compute_changes(previous, current)
        assert len(changes) == 1
        assert "Added" in changes[0]
        assert "Authentication.Strategy" in changes[0]

    def test_compute_changes_modified_field(self) -> None:
        """Detect modified field."""
        previous = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "Email/Password"),)),
            ),
        )
        current = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"),)),
            ),
        )

        changes = compute_changes(previous, current)
        assert len(changes) == 1
        assert "Modified" in changes[0]
        assert "was: Email/Password" in changes[0]

    def test_compute_changes_removed_field(self) -> None:
        """Detect removed field."""
        previous = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"), ("Library", "next-auth"))),
            ),
        )
        current = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"),)),
            ),
        )

        changes = compute_changes(previous, current)
        assert any("Removed" in c and "Library" in c for c in changes)

    def test_compute_changes_from_none(self) -> None:
        """All fields are 'Added' when previous is None."""
        current = ArchitectureState(
            uid="20250106T120000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"), ("Library", "next-auth"))),
            ),
        )

        changes = compute_changes(None, current)
        assert len(changes) == 2
        assert all("Added" in c for c in changes)

    def test_compute_changes_no_changes(self) -> None:
        """Empty changes when snapshots are identical."""
        snapshot = ArchitectureState(
            uid="20250106T100000.000Z",
            schema_version="v1",
            categories=(
                ("Authentication", (("Strategy", "OAuth"),)),
            ),
        )

        changes = compute_changes(snapshot, snapshot)
        assert len(changes) == 0
