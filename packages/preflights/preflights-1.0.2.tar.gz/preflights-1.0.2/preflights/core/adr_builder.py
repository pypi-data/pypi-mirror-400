"""
Preflights Core ADRBuilder.

Pure logic for building ADR artifacts.
No I/O.
"""

from __future__ import annotations

from preflights.core.types import (
    ADR,
    ArchitectureState,
    DecisionPatch,
)


def build_adr(
    uid: str,
    date_utc: str,
    title: str,
    category: str,
    decision_patch: DecisionPatch,
    new_snapshot: ArchitectureState,
    previous_uid: str | None,
    context: str,
    decision: str,
    rationale: str,
    alternatives: tuple[str, ...],
    consequences_positive: tuple[str, ...],
    consequences_negative: tuple[str, ...],
    consequences_neutral: tuple[str, ...],
    changes_in_this_version: tuple[str, ...],
    supersedes_uid: str | None = None,
) -> ADR:
    """
    Build an ADR artifact.

    Args:
        uid: ADR UID (injected)
        date_utc: Date in UTC (YYYY-MM-DD format)
        title: ADR title
        category: Primary category affected
        decision_patch: The decision patch applied
        new_snapshot: The new architecture snapshot
        previous_uid: UID of the previous ADR (None if first)
        context: Why this decision was needed
        decision: What was decided
        rationale: Why this decision
        alternatives: List of alternatives considered
        consequences_positive: Positive consequences
        consequences_negative: Negative consequences
        consequences_neutral: Neutral consequences
        changes_in_this_version: List of changes made
        supersedes_uid: UID of ADR this supersedes (if any)

    Returns:
        ADR artifact
    """
    return ADR(
        uid=uid,
        title=title,
        category=category,
        date_utc=date_utc,
        previous_uid=previous_uid,
        snapshot=new_snapshot,
        changes_in_this_version=changes_in_this_version,
        context=context,
        decision=decision,
        rationale=rationale,
        alternatives=alternatives,
        consequences_positive=consequences_positive,
        consequences_negative=consequences_negative,
        consequences_neutral=consequences_neutral,
        supersedes_uid=supersedes_uid,
    )


def generate_adr_title(
    category: str,
    decision_patch: DecisionPatch,
) -> str:
    """
    Generate a title for the ADR.

    Format: "{Category} - {Primary Decision}"

    Args:
        category: Category name
        decision_patch: The decision patch

    Returns:
        Generated title
    """
    if decision_patch.fields:
        primary_field, primary_value = decision_patch.fields[0]
        return f"{category}: {primary_field} = {primary_value}"
    return f"{category} Decision"


def generate_context(
    intention_text: str,
    category: str,
) -> str:
    """
    Generate context text for the ADR.

    Args:
        intention_text: User's original intention
        category: Category being decided

    Returns:
        Context description
    """
    return f"A decision is needed for {category}.\n\nUser intention: {intention_text}"


def generate_decision(
    decision_patch: DecisionPatch,
) -> str:
    """
    Generate decision text from patch.

    Args:
        decision_patch: The decision patch

    Returns:
        Decision description
    """
    lines = [f"We have decided on the following for {decision_patch.category}:"]
    for field, value in decision_patch.fields:
        lines.append(f"- {field}: {value}")
    return "\n".join(lines)


def generate_rationale(
    decision_patch: DecisionPatch,
) -> str:
    """
    Generate rationale text.

    This is a placeholder - in practice, LLM or user input would provide this.

    Args:
        decision_patch: The decision patch

    Returns:
        Rationale description
    """
    return f"This decision was made based on project requirements and team expertise in {decision_patch.category}."


def generate_changes_description(
    previous: ArchitectureState | None,
    patch: DecisionPatch,
    new_uid: str,
) -> tuple[str, ...]:
    """
    Generate changes description for ADR.

    Args:
        previous: Previous architecture state
        patch: Decision patch being applied
        new_uid: New ADR UID

    Returns:
        Tuple of change descriptions
    """
    changes: list[str] = []

    for field, value in patch.fields:
        # Check if field existed before
        previous_value: str | None = None
        if previous is not None:
            for cat_name, cat_fields in previous.categories:
                if cat_name.lower() == patch.category.lower():
                    for prev_field, prev_val in cat_fields:
                        if prev_field.lower() == field.lower():
                            previous_value = prev_val
                            break
                    break

        if previous_value is None:
            changes.append(f"Added: {patch.category}.{field} = {value}")
        else:
            changes.append(
                f"Modified: {patch.category}.{field} = {value} (was: {previous_value})"
            )

    return tuple(changes)
