"""Property-based tests for SnapshotBuilder.

Uses Hypothesis to prove invariants:
- apply_patch preserves all previous categories
- apply_patch never drops keys silently
- merge_snapshots is idempotent
- compute_changes detects all actual changes
"""

from __future__ import annotations

import string

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from preflights.core.snapshot_builder import (
    apply_patch,
    compute_changes,
    merge_snapshots,
)
from preflights.core.types import (
    ArchitectureState,
    DecisionPatch,
    SnapshotSchema,
)


# =============================================================================
# STRATEGIES
# =============================================================================


# Valid field names (alphanumeric with underscores)
field_name_strategy = st.text(
    alphabet=string.ascii_letters + "_",
    min_size=1,
    max_size=20,
).filter(lambda x: x[0].isalpha())

# Valid field values
field_value_strategy = st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != "")

# Valid UID format
uid_strategy = st.from_regex(r"^\d{8}T\d{6}\.\d{3}Z$", fullmatch=True)


@st.composite
def snapshot_schema_strategy(draw: st.DrawFn) -> SnapshotSchema:
    """Generate a valid SnapshotSchema."""
    num_categories = draw(st.integers(min_value=1, max_value=5))
    categories: list[tuple[str, tuple[str, ...]]] = []

    for i in range(num_categories):
        cat_name = f"Category{i}"
        num_fields = draw(st.integers(min_value=1, max_value=5))
        fields = tuple(f"Field{j}" for j in range(num_fields))
        categories.append((cat_name, fields))

    return SnapshotSchema(categories=tuple(categories))


@st.composite
def architecture_state_strategy(
    draw: st.DrawFn, schema: SnapshotSchema
) -> ArchitectureState:
    """Generate a valid ArchitectureState matching the schema."""
    uid = draw(uid_strategy)

    # Pick a subset of categories from schema
    schema_cats = list(schema.categories)
    num_cats = draw(st.integers(min_value=0, max_value=len(schema_cats)))
    selected_cats = draw(st.sampled_from(
        [tuple(schema_cats[:n]) for n in range(num_cats + 1)]
    ))

    categories: list[tuple[str, tuple[tuple[str, str], ...]]] = []
    for cat_name, cat_fields in selected_cats:
        # Pick a subset of fields
        num_fields = draw(st.integers(min_value=0, max_value=len(cat_fields)))
        selected_fields = cat_fields[:num_fields]

        fields: list[tuple[str, str]] = []
        for field_name in selected_fields:
            value = draw(field_value_strategy)
            fields.append((field_name, value))

        if fields:  # Only add category if it has fields
            categories.append((cat_name, tuple(fields)))

    return ArchitectureState(
        uid=uid,
        schema_version="v1",
        categories=tuple(categories),
    )


@st.composite
def decision_patch_strategy(
    draw: st.DrawFn, schema: SnapshotSchema
) -> DecisionPatch:
    """Generate a valid DecisionPatch matching the schema."""
    # Pick a category from schema
    cat_name, cat_fields = draw(st.sampled_from(schema.categories))

    # Pick at least one field
    num_fields = draw(st.integers(min_value=1, max_value=len(cat_fields)))
    selected_fields = cat_fields[:num_fields]

    fields: list[tuple[str, str]] = []
    for field_name in selected_fields:
        value = draw(field_value_strategy)
        fields.append((field_name, value))

    return DecisionPatch(
        category=cat_name,
        fields=tuple(fields),
    )


# =============================================================================
# PROPERTY: apply_patch preserves all previous categories
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_apply_patch_preserves_previous_categories(data: st.DataObject) -> None:
    """
    PROPERTY: apply_patch never drops existing categories.

    For any previous state and any patch:
    - All categories from previous MUST exist in result
    - Category names are preserved exactly
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    previous = data.draw(architecture_state_strategy(schema))
    patch = data.draw(decision_patch_strategy(schema))
    new_uid = data.draw(uid_strategy)

    result = apply_patch(previous, patch, new_uid, schema)

    # All previous categories must still exist
    previous_cat_names = {cat[0] for cat in previous.categories}
    result_cat_names = {cat[0] for cat in result.categories}

    for prev_cat in previous_cat_names:
        assert prev_cat in result_cat_names, (
            f"Category '{prev_cat}' was dropped by apply_patch"
        )


# =============================================================================
# PROPERTY: apply_patch never drops fields silently
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_apply_patch_never_drops_fields(data: st.DataObject) -> None:
    """
    PROPERTY: apply_patch preserves all existing fields.

    For any previous state and any patch:
    - All fields from previous (not touched by patch) MUST exist in result
    - Field values are preserved exactly (unless overwritten by patch)
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    previous = data.draw(architecture_state_strategy(schema))
    patch = data.draw(decision_patch_strategy(schema))
    new_uid = data.draw(uid_strategy)

    result = apply_patch(previous, patch, new_uid, schema)

    # Build lookups
    prev_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in previous.categories:
        prev_fields[cat_name] = dict(cat_fields)

    result_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in result.categories:
        result_fields[cat_name] = dict(cat_fields)

    patch_fields = {f[0] for f in patch.fields}

    # Check all previous fields exist in result
    for cat_name, fields in prev_fields.items():
        assert cat_name in result_fields, f"Category {cat_name} was dropped"

        for field_name, field_value in fields.items():
            assert field_name in result_fields[cat_name], (
                f"Field {cat_name}.{field_name} was dropped"
            )

            # If field is NOT in patch, value must be preserved exactly
            if cat_name != patch.category or field_name not in patch_fields:
                assert result_fields[cat_name][field_name] == field_value, (
                    f"Field {cat_name}.{field_name} was modified but not in patch"
                )


# =============================================================================
# PROPERTY: apply_patch correctly updates target fields
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_apply_patch_updates_target_fields(data: st.DataObject) -> None:
    """
    PROPERTY: apply_patch correctly updates fields from patch.

    For any patch:
    - All fields from patch MUST exist in result
    - Values contain the patch value and ADR reference
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    previous = data.draw(architecture_state_strategy(schema))
    patch = data.draw(decision_patch_strategy(schema))
    new_uid = data.draw(uid_strategy)

    result = apply_patch(previous, patch, new_uid, schema)

    # Build result lookup
    result_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in result.categories:
        result_fields[cat_name] = dict(cat_fields)

    # Check all patch fields are in result with correct format
    assert patch.category in result_fields, (
        f"Patch category {patch.category} not in result"
    )

    for field_name, field_value in patch.fields:
        assert field_name in result_fields[patch.category], (
            f"Patch field {field_name} not in result"
        )

        result_value = result_fields[patch.category][field_name]
        assert field_value in result_value, (
            f"Patch value '{field_value}' not in result '{result_value}'"
        )
        assert new_uid in result_value, (
            f"ADR UID '{new_uid}' not in result '{result_value}'"
        )


# =============================================================================
# PROPERTY: merge_snapshots is idempotent
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_merge_snapshots_idempotent(data: st.DataObject) -> None:
    """
    PROPERTY: merge(a, a) == a (idempotent).

    Merging a snapshot with itself produces the same snapshot.
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    state = data.draw(architecture_state_strategy(schema))
    assume(len(state.categories) >= 1)  # Need at least one category

    result = merge_snapshots(state, state)

    # Categories should be identical
    assert len(result.categories) == len(state.categories)

    state_cats = dict((c[0], dict(c[1])) for c in state.categories)
    result_cats = dict((c[0], dict(c[1])) for c in result.categories)

    assert state_cats == result_cats


# =============================================================================
# PROPERTY: merge_snapshots overlay wins
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_merge_snapshots_overlay_wins(data: st.DataObject) -> None:
    """
    PROPERTY: In merge(base, overlay), overlay values take precedence.

    For overlapping fields, overlay value must be in result.
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    base = data.draw(architecture_state_strategy(schema))
    overlay = data.draw(architecture_state_strategy(schema))

    result = merge_snapshots(base, overlay)

    # Build lookups
    overlay_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in overlay.categories:
        overlay_fields[cat_name] = dict(cat_fields)

    result_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in result.categories:
        result_fields[cat_name] = dict(cat_fields)

    # All overlay fields must be in result with same value
    for cat_name, fields in overlay_fields.items():
        assert cat_name in result_fields
        for field_name, field_value in fields.items():
            assert result_fields[cat_name][field_name] == field_value


# =============================================================================
# PROPERTY: compute_changes detects all additions
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_compute_changes_detects_additions(data: st.DataObject) -> None:
    """
    PROPERTY: compute_changes detects all newly added fields.

    If a field exists in current but not in previous, it must appear in changes.
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    previous = data.draw(architecture_state_strategy(schema))
    current = data.draw(architecture_state_strategy(schema))

    changes = compute_changes(previous, current)

    # Build lookups
    prev_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in previous.categories:
        prev_fields[cat_name] = dict(cat_fields)

    curr_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in current.categories:
        curr_fields[cat_name] = dict(cat_fields)

    # Check all additions are detected
    for cat_name, fields in curr_fields.items():
        prev_cat_fields = prev_fields.get(cat_name, {})
        for field_name, field_value in fields.items():
            if field_name not in prev_cat_fields:
                # This is an addition - must be in changes
                expected_prefix = f"Added: {cat_name}.{field_name}"
                found = any(c.startswith(expected_prefix) for c in changes)
                assert found, (
                    f"Addition of {cat_name}.{field_name} not detected in changes"
                )


# =============================================================================
# PROPERTY: compute_changes detects all modifications
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_compute_changes_detects_modifications(data: st.DataObject) -> None:
    """
    PROPERTY: compute_changes detects all modified fields.

    If a field value differs between previous and current, it must appear in changes.
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    previous = data.draw(architecture_state_strategy(schema))
    current = data.draw(architecture_state_strategy(schema))

    changes = compute_changes(previous, current)

    # Build lookups
    prev_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in previous.categories:
        prev_fields[cat_name] = dict(cat_fields)

    curr_fields: dict[str, dict[str, str]] = {}
    for cat_name, cat_fields in current.categories:
        curr_fields[cat_name] = dict(cat_fields)

    # Check all modifications are detected
    for cat_name, fields in curr_fields.items():
        prev_cat_fields = prev_fields.get(cat_name, {})
        for field_name, field_value in fields.items():
            if field_name in prev_cat_fields and prev_cat_fields[field_name] != field_value:
                # This is a modification - must be in changes
                expected_prefix = f"Modified: {cat_name}.{field_name}"
                found = any(c.startswith(expected_prefix) for c in changes)
                assert found, (
                    f"Modification of {cat_name}.{field_name} not detected in changes"
                )


# =============================================================================
# PROPERTY: apply_patch from None creates valid state
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_apply_patch_from_none_creates_valid_state(data: st.DataObject) -> None:
    """
    PROPERTY: apply_patch(None, patch) creates a valid initial state.

    When previous is None:
    - Result must contain exactly the patch category
    - Result must contain exactly the patch fields
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    patch = data.draw(decision_patch_strategy(schema))
    new_uid = data.draw(uid_strategy)

    result = apply_patch(None, patch, new_uid, schema)

    # Result must have the new UID
    assert result.uid == new_uid

    # Result must have exactly one category (the patch category)
    assert len(result.categories) == 1
    result_cat_name, result_cat_fields = result.categories[0]
    assert result_cat_name == patch.category

    # Result must have exactly the patch fields
    result_fields = dict(result_cat_fields)
    assert len(result_fields) == len(patch.fields)

    for field_name, field_value in patch.fields:
        assert field_name in result_fields
        assert field_value in result_fields[field_name]
        assert new_uid in result_fields[field_name]


# =============================================================================
# PROPERTY: result UID always matches new_adr_uid
# =============================================================================


@given(st.data())
@settings(max_examples=100)
def test_apply_patch_result_uid_matches_input(data: st.DataObject) -> None:
    """
    PROPERTY: apply_patch result.uid always equals new_adr_uid.

    The output UID must be exactly the injected UID.
    """
    schema = data.draw(snapshot_schema_strategy())
    assume(len(schema.categories) >= 1)

    previous = data.draw(architecture_state_strategy(schema))
    patch = data.draw(decision_patch_strategy(schema))
    new_uid = data.draw(uid_strategy)

    result = apply_patch(previous, patch, new_uid, schema)

    assert result.uid == new_uid, (
        f"Result UID '{result.uid}' does not match input '{new_uid}'"
    )
