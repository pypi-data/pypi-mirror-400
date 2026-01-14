"""
Preflights Core Validators.

Pure validation logic. No I/O.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from preflights.core.types import (
    ADR,
    ArchitectureState,
    CoreError,
    DecisionPatch,
    ErrorCode,
    SnapshotSchema,
    Task,
)

# UID format: YYYYMMDDTHHMMSS.mmmZ or YYYYMMDDTHHMMSS.mmmZ-XXXX (with anti-collision suffix)
# Legacy: "20250104T143512.237Z"
# New:    "20250104T143512.237Z-A3F9"
UID_PATTERN = re.compile(r"^\d{8}T\d{6}\.\d{3}Z(-[A-Fa-f0-9]{4})?$")


def validate_uid_format(uid: str) -> CoreError | None:
    """
    Validate UID format.

    Supports:
    - Legacy: YYYYMMDDTHHMMSS.mmmZ (e.g., "20250104T143512.237Z")
    - New:    YYYYMMDDTHHMMSS.mmmZ-XXXX (e.g., "20250104T143512.237Z-A3F9")

    The suffix is optional for backward compatibility.
    """
    if not UID_PATTERN.match(uid):
        return CoreError(
            code=ErrorCode.INVALID_UID_FORMAT,
            message=f"Invalid UID format: {uid}",
            details=(("expected", "YYYYMMDDTHHMMSS.mmmZ[-XXXX]"), ("got", uid)),
            recovery_hint="Use format YYYYMMDDTHHMMSS.mmmZ or YYYYMMDDTHHMMSS.mmmZ-XXXX",
        )
    return None


def validate_decision_patch(
    patch: DecisionPatch,
    schema: SnapshotSchema,
) -> CoreError | None:
    """
    Validate DecisionPatch against schema.

    Checks:
    - Category is valid (exists in schema)
    - All field keys are valid for the category
    """
    # Build lookup for schema
    schema_categories: dict[str, tuple[str, ...]] = {}
    for cat_name, cat_fields in schema.categories:
        schema_categories[cat_name.lower()] = cat_fields

    # Check category exists
    category_lower = patch.category.lower()
    if category_lower not in schema_categories:
        valid_categories = [cat for cat, _ in schema.categories]
        return CoreError(
            code=ErrorCode.UNKNOWN_CATEGORY,
            message=f"Unknown category: {patch.category}",
            details=(
                ("category", patch.category),
                ("valid_categories", ", ".join(valid_categories)),
            ),
            recovery_hint=f"Use one of: {', '.join(valid_categories)}",
        )

    # Check all fields are valid
    valid_fields = schema_categories[category_lower]

    # Special case: wildcard "*" accepts any field (for "Other" category)
    if valid_fields == ("*",):
        # Any field is valid for wildcard categories
        return None

    valid_fields_lower = {f.lower() for f in valid_fields}

    for field_key, _ in patch.fields:
        if field_key.lower() not in valid_fields_lower:
            return CoreError(
                code=ErrorCode.UNKNOWN_FIELD,
                message=f"Unknown field '{field_key}' in category '{patch.category}'",
                details=(
                    ("field", field_key),
                    ("category", patch.category),
                    ("valid_fields", ", ".join(valid_fields)),
                ),
                recovery_hint=f"Use one of: {', '.join(valid_fields)}",
            )

    return None


def validate_snapshot(
    snapshot: ArchitectureState,
    previous: ArchitectureState | None,
    schema: SnapshotSchema,
) -> CoreError | None:
    """
    Validate snapshot against schema and previous state.

    Checks:
    - All categories in snapshot are valid (exist in schema)
    - All fields in each category are valid
    - No silent drops from previous (if previous exists)
    """
    # Build schema lookup
    schema_categories: dict[str, set[str]] = {}
    for schema_cat_name, schema_cat_fields in schema.categories:
        schema_categories[schema_cat_name.lower()] = {f.lower() for f in schema_cat_fields}

    # Build current snapshot lookup
    current_cats: dict[str, dict[str, str]] = {}
    for snap_cat_name, snap_cat_fields in snapshot.categories:
        current_cats[snap_cat_name.lower()] = {}
        for snap_field_key, snap_field_val in snap_cat_fields:
            current_cats[snap_cat_name.lower()][snap_field_key.lower()] = snap_field_val

    # Check all categories are valid
    for cat_name, _ in snapshot.categories:
        if cat_name.lower() not in schema_categories:
            valid_categories = [cat for cat, _ in schema.categories]
            return CoreError(
                code=ErrorCode.UNKNOWN_CATEGORY,
                message=f"Unknown category in snapshot: {cat_name}",
                details=(("category", cat_name),),
                recovery_hint=f"Valid categories: {', '.join(valid_categories)}",
            )

        # Check all fields are valid for this category
        valid_fields = schema_categories[cat_name.lower()]

        # Skip field validation for wildcard categories (e.g., "Other")
        if "*" in valid_fields:
            continue

        cat_fields_in_snapshot = current_cats.get(cat_name.lower(), {})
        for field_key in cat_fields_in_snapshot:
            if field_key not in valid_fields:
                return CoreError(
                    code=ErrorCode.UNKNOWN_FIELD,
                    message=f"Unknown field '{field_key}' in category '{cat_name}'",
                    details=(("field", field_key), ("category", cat_name)),
                )

    # Check no silent drops from previous
    if previous is not None:
        previous_cats: dict[str, dict[str, str]] = {}
        for prev_cat_name, prev_cat_fields in previous.categories:
            previous_cats[prev_cat_name.lower()] = {}
            for prev_field_key, prev_field_val in prev_cat_fields:
                previous_cats[prev_cat_name.lower()][prev_field_key.lower()] = prev_field_val

        # Check all previous categories still exist
        for prev_cat, prev_fields in previous_cats.items():
            if prev_cat not in current_cats:
                return CoreError(
                    code=ErrorCode.VALIDATION_FAILED,
                    message=f"Category '{prev_cat}' was silently dropped from snapshot",
                    details=(("dropped_category", prev_cat),),
                    recovery_hint="Categories cannot be silently dropped. Use explicit removal in changes_in_this_version.",
                )

            # Check all previous fields still exist
            current_fields = current_cats[prev_cat]
            for prev_field in prev_fields:
                if prev_field not in current_fields:
                    return CoreError(
                        code=ErrorCode.VALIDATION_FAILED,
                        message=f"Field '{prev_field}' in category '{prev_cat}' was silently dropped",
                        details=(
                            ("dropped_field", prev_field),
                            ("category", prev_cat),
                        ),
                        recovery_hint="Fields cannot be silently dropped. Use explicit removal in changes_in_this_version.",
                    )

    return None


def validate_task(task: Task) -> CoreError | None:
    """
    Validate Task.

    Checks:
    - allowlist is non-empty
    - forbidden doesn't overlap with allowlist
    - acceptance_criteria is non-empty
    """
    # Check allowlist non-empty
    if not task.allowlist:
        return CoreError(
            code=ErrorCode.EMPTY_ALLOWLIST,
            message="Task allowlist cannot be empty",
            details=(),
            recovery_hint="Provide at least one file or pattern in the allowlist.",
        )

    # Check no overlap between allowlist and forbidden
    allowlist_set = set(task.allowlist)
    forbidden_set = set(task.forbidden)
    overlap = allowlist_set & forbidden_set

    if overlap:
        return CoreError(
            code=ErrorCode.FORBIDDEN_OVERLAP,
            message="Allowlist and forbidden list overlap",
            details=(("overlapping_paths", ", ".join(sorted(overlap))),),
            recovery_hint="Remove overlapping paths from either allowlist or forbidden.",
        )

    # Check acceptance_criteria non-empty
    if not task.acceptance_criteria:
        return CoreError(
            code=ErrorCode.EMPTY_ACCEPTANCE_CRITERIA,
            message="Task must have at least one acceptance criterion",
            details=(),
            recovery_hint="Provide at least one testable/observable acceptance criterion.",
        )

    # Validate UID format
    uid_error = validate_uid_format(task.uid)
    if uid_error:
        return uid_error

    return None


def validate_adr(adr: ADR, schema: SnapshotSchema) -> CoreError | None:
    """
    Validate ADR.

    Checks:
    - UID format is valid
    - Snapshot is valid
    - Required fields are non-empty (context, decision, rationale)
    - Alternatives list has at least one entry
    """
    # Validate UID format
    uid_error = validate_uid_format(adr.uid)
    if uid_error:
        return uid_error

    # Validate snapshot
    snapshot_error = validate_snapshot(adr.snapshot, None, schema)
    if snapshot_error:
        return snapshot_error

    # Check required fields are non-empty
    required_fields = [
        ("context", adr.context),
        ("decision", adr.decision),
        ("rationale", adr.rationale),
        ("title", adr.title),
        ("category", adr.category),
    ]

    for field_name, field_value in required_fields:
        if not field_value or not field_value.strip():
            return CoreError(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message=f"ADR field '{field_name}' cannot be empty",
                details=(("field", field_name),),
                recovery_hint=f"Provide a non-empty value for {field_name}.",
            )

    # Check alternatives has at least one entry
    if not adr.alternatives:
        return CoreError(
            code=ErrorCode.MISSING_REQUIRED_FIELD,
            message="ADR field 'alternatives' must have at least one entry",
            details=(("field", "alternatives"),),
            recovery_hint="Add at least one alternative (can be 'None considered' with rationale).",
        )

    # Check changes_in_this_version is non-empty
    if not adr.changes_in_this_version:
        return CoreError(
            code=ErrorCode.MISSING_REQUIRED_FIELD,
            message="ADR must document changes in this version",
            details=(("field", "changes_in_this_version"),),
            recovery_hint="Add at least one change description.",
        )

    return None
