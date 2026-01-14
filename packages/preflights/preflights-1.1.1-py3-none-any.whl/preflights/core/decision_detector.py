"""
Preflights Core DecisionDetector.

Pure logic for detecting if an ADR is required.
No I/O.
"""

from __future__ import annotations

from dataclasses import dataclass

from preflights.core.types import (
    ArchitectureState,
    DecisionPatch,
    HeuristicsConfig,
    Intention,
)


@dataclass(frozen=True)
class ADRDecision:
    """Result of ADR need detection."""

    needs_adr: bool
    category: str | None
    triggered_by: tuple[str, ...]
    rationale: str


def detect_adr_need(
    intention: Intention,
    decision_patch: DecisionPatch,
    heuristics_config: HeuristicsConfig,
    current_architecture: ArchitectureState | None = None,
    metadata: tuple[tuple[str, str], ...] | None = None,
) -> ADRDecision:
    """
    Decide if ADR is required based on heuristics.

    ADR triggers (any match → ADR required):
    1. Category keywords detected in intention
    2. Modifies an existing ADR category
    3. File impact >= threshold (from metadata)
    4. New dependency introduced (from metadata)
    5. User explicitly asks for strategy/architecture

    No ADR triggers (explicit skip):
    - Bug fix
    - Pure refactor
    - Config-only change
    - Typo fix

    Args:
        intention: User's intention
        decision_patch: The decision patch to apply
        heuristics_config: Configuration with keywords and thresholds
        current_architecture: Current architecture state (to detect category modification)
        metadata: Optional metadata (estimated_file_impact, new_dependencies, etc.)

    Returns:
        ADRDecision with needs_adr, category, triggers, and rationale
    """
    triggers: list[str] = []
    intention_lower = intention.text.lower()

    # Check non-triggers first (explicit skip)
    for non_trigger in heuristics_config.non_triggers:
        if non_trigger in intention_lower:
            return ADRDecision(
                needs_adr=False,
                category=None,
                triggered_by=(),
                rationale=f"Detected non-trigger keyword: {non_trigger}",
            )

    # Check category keywords
    matched_category: str | None = None
    for cat_name, keywords in heuristics_config.category_keywords:
        for keyword in keywords:
            if keyword in intention_lower:
                triggers.append(f"keyword:{keyword}")
                if matched_category is None:
                    matched_category = cat_name

    # Use patch category if available and no keyword match
    if matched_category is None:
        matched_category = decision_patch.category

    # Check if modifying existing category
    if current_architecture is not None:
        existing_categories = {
            cat_name.lower() for cat_name, _ in current_architecture.categories
        }
        if decision_patch.category.lower() in existing_categories:
            triggers.append(f"modifies_existing_category:{decision_patch.category}")

    # Check metadata triggers
    if metadata:
        metadata_dict = dict(metadata)

        # File impact threshold
        file_impact_str = metadata_dict.get("estimated_file_impact")
        if file_impact_str:
            try:
                file_impact = int(file_impact_str)
                if file_impact >= heuristics_config.file_impact_threshold:
                    triggers.append(f"file_impact:{file_impact}")
            except ValueError:
                pass

        # New dependency
        if metadata_dict.get("new_dependencies"):
            triggers.append("new_dependencies")

    # Check explicit architecture keywords in intention
    architecture_keywords = ("architecture", "strategy", "approach", "design decision")
    for keyword in architecture_keywords:
        if keyword in intention_lower:
            triggers.append(f"explicit:{keyword}")

    # Determine if ADR is needed
    needs_adr = len(triggers) > 0

    if needs_adr:
        rationale = f"ADR required due to: {', '.join(triggers)}"
    else:
        rationale = "No ADR triggers detected"

    return ADRDecision(
        needs_adr=needs_adr,
        category=matched_category if needs_adr else None,
        triggered_by=tuple(triggers),
        rationale=rationale,
    )


def extract_category_from_intention(
    intention: Intention,
    heuristics_config: HeuristicsConfig,
) -> str | None:
    """
    Extract the most likely category from intention text.

    Uses keyword matching from heuristics config.

    Args:
        intention: User's intention
        heuristics_config: Configuration with category keywords

    Returns:
        Category name or None if no match
    """
    intention_lower = intention.text.lower()

    # Score each category by keyword matches
    scores: dict[str, int] = {}
    for cat_name, keywords in heuristics_config.category_keywords:
        score = 0
        for keyword in keywords:
            if keyword in intention_lower:
                score += 1
        if score > 0:
            scores[cat_name] = score

    if not scores:
        return None

    # Return category with highest score
    return max(scores, key=lambda k: scores[k])
