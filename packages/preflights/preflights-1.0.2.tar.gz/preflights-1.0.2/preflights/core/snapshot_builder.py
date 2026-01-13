"""
Preflights Core SnapshotBuilder.

Pure logic for building architecture snapshots.
No I/O.
"""

from __future__ import annotations

from preflights.core.types import (
    ArchitectureState,
    DecisionPatch,
    SnapshotSchema,
)


def apply_patch(
    previous: ArchitectureState | None,
    patch: DecisionPatch,
    new_adr_uid: str,
    schema: SnapshotSchema,
) -> ArchitectureState:
    """
    Build new snapshot by applying patch to previous.

    Rules:
    - Preserve all existing categories/fields from previous
    - Only mutate target category/fields from patch
    - Never drop keys silently
    - New fields are added to target category
    - Existing fields in target category are updated

    Args:
        previous: Previous architecture state (None if first ADR)
        patch: DecisionPatch to apply
        new_adr_uid: UID for the new ADR
        schema: Schema to validate against (not used for validation here, just structure)

    Returns:
        New ArchitectureState with patch applied
    """
    # Build mutable dict from previous
    categories_dict: dict[str, dict[str, str]] = {}

    if previous is not None:
        for prev_cat_name, prev_cat_fields in previous.categories:
            categories_dict[prev_cat_name] = {}
            for prev_field_key, prev_field_val in prev_cat_fields:
                categories_dict[prev_cat_name][prev_field_key] = prev_field_val

    # Apply patch to target category
    target_category = _normalize_category_name(patch.category, schema)

    if target_category not in categories_dict:
        categories_dict[target_category] = {}

    # Apply field updates
    for field_key, field_val in patch.fields:
        normalized_field = _normalize_field_name(field_key, target_category, schema)
        # Format value with ADR reference
        categories_dict[target_category][normalized_field] = f"{field_val} (ADR {new_adr_uid})"

    # Convert back to immutable tuples
    categories_tuple: list[tuple[str, tuple[tuple[str, str], ...]]] = []
    for out_cat_name, out_cat_fields_dict in sorted(categories_dict.items()):
        fields_tuple = tuple(sorted(out_cat_fields_dict.items()))
        categories_tuple.append((out_cat_name, fields_tuple))

    return ArchitectureState(
        uid=new_adr_uid,
        schema_version="v1",
        categories=tuple(categories_tuple),
    )


def _normalize_category_name(category: str, schema: SnapshotSchema) -> str:
    """
    Normalize category name to match schema casing.

    Returns the schema's canonical casing for the category.
    """
    category_lower = category.lower()
    for cat_name, _ in schema.categories:
        if cat_name.lower() == category_lower:
            return cat_name
    # Fallback to original (should be caught by validation earlier)
    return category


def _normalize_field_name(
    field: str, category: str, schema: SnapshotSchema
) -> str:
    """
    Normalize field name to match schema casing.

    Returns the schema's canonical casing for the field.
    """
    field_lower = field.lower()
    category_lower = category.lower()

    for cat_name, cat_fields in schema.categories:
        if cat_name.lower() == category_lower:
            for schema_field in cat_fields:
                if schema_field.lower() == field_lower:
                    return schema_field
            break

    # Fallback to original (should be caught by validation earlier)
    return field


def merge_snapshots(
    base: ArchitectureState,
    overlay: ArchitectureState,
) -> ArchitectureState:
    """
    Merge two snapshots, with overlay taking precedence.

    Used when combining multiple patches or resolving conflicts.

    Args:
        base: Base snapshot
        overlay: Overlay snapshot (takes precedence)

    Returns:
        Merged ArchitectureState
    """
    # Build mutable dict from base
    categories_dict: dict[str, dict[str, str]] = {}

    for base_cat_name, base_cat_fields in base.categories:
        categories_dict[base_cat_name] = {}
        for base_field_key, base_field_val in base_cat_fields:
            categories_dict[base_cat_name][base_field_key] = base_field_val

    # Apply overlay
    for overlay_cat_name, overlay_cat_fields in overlay.categories:
        if overlay_cat_name not in categories_dict:
            categories_dict[overlay_cat_name] = {}
        for overlay_field_key, overlay_field_val in overlay_cat_fields:
            categories_dict[overlay_cat_name][overlay_field_key] = overlay_field_val

    # Convert back to immutable tuples
    categories_tuple: list[tuple[str, tuple[tuple[str, str], ...]]] = []
    for out_cat_name, out_cat_fields_dict in sorted(categories_dict.items()):
        fields_tuple = tuple(sorted(out_cat_fields_dict.items()))
        categories_tuple.append((out_cat_name, fields_tuple))

    return ArchitectureState(
        uid=overlay.uid,
        schema_version=overlay.schema_version,
        categories=tuple(categories_tuple),
    )


def compute_changes(
    previous: ArchitectureState | None,
    current: ArchitectureState,
) -> tuple[str, ...]:
    """
    Compute changes between previous and current snapshot.

    Returns a tuple of change descriptions.

    Args:
        previous: Previous state (None if first)
        current: Current state

    Returns:
        Tuple of change descriptions (e.g., "Added: Authentication.Strategy = OAuth")
    """
    changes: list[str] = []

    # Build lookups
    prev_cats: dict[str, dict[str, str]] = {}
    if previous is not None:
        for prev_cat_name, prev_cat_fields in previous.categories:
            prev_cats[prev_cat_name] = {}
            for prev_field_key, prev_field_val in prev_cat_fields:
                prev_cats[prev_cat_name][prev_field_key] = prev_field_val

    curr_cats: dict[str, dict[str, str]] = {}
    for curr_cat_name, curr_cat_fields in current.categories:
        curr_cats[curr_cat_name] = {}
        for curr_field_key, curr_field_val in curr_cat_fields:
            curr_cats[curr_cat_name][curr_field_key] = curr_field_val

    # Find added/modified
    for compare_cat_name, compare_cat_fields in curr_cats.items():
        compare_prev_fields = prev_cats.get(compare_cat_name, {})

        for compare_field_key, compare_field_val in compare_cat_fields.items():
            prev_val = compare_prev_fields.get(compare_field_key)

            if prev_val is None:
                changes.append(f"Added: {compare_cat_name}.{compare_field_key} = {compare_field_val}")
            elif prev_val != compare_field_val:
                changes.append(
                    f"Modified: {compare_cat_name}.{compare_field_key} = {compare_field_val} (was: {prev_val})"
                )

    # Find removed
    for removed_cat_name, removed_cat_fields in prev_cats.items():
        curr_fields = curr_cats.get(removed_cat_name, {})

        for removed_field_key in removed_cat_fields:
            if removed_field_key not in curr_fields:
                changes.append(f"Removed: {removed_cat_name}.{removed_field_key}")

        if removed_cat_name not in curr_cats:
            changes.append(f"Removed: {removed_cat_name} (entire category)")

    return tuple(changes)
