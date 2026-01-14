"""
Preflights Core TaskBuilder.

Pure logic for building Task artifacts.
No I/O.
"""

from __future__ import annotations

from preflights.core.types import (
    DecisionPatch,
    FileContext,
    Intention,
    Task,
)


def build_task(
    uid: str,
    created_at_utc: str,
    title: str,
    objective: str,
    context: str,
    allowlist: tuple[str, ...],
    forbidden: tuple[str, ...],
    technical_constraints: tuple[str, ...],
    acceptance_criteria: tuple[str, ...],
    related_adr_uid: str | None,
) -> Task:
    """
    Build a Task artifact.

    Args:
        uid: Task UID (injected)
        created_at_utc: Creation timestamp (injected)
        title: Task title
        objective: What the task should achieve
        context: Background context and relevant ADRs
        allowlist: Files/patterns allowed to modify
        forbidden: Files/patterns forbidden to modify
        technical_constraints: Technical requirements
        acceptance_criteria: Observable/testable criteria
        related_adr_uid: UID of related ADR (if any)

    Returns:
        Task artifact
    """
    return Task(
        uid=uid,
        title=title,
        objective=objective,
        context=context,
        allowlist=allowlist,
        forbidden=forbidden,
        technical_constraints=technical_constraints,
        acceptance_criteria=acceptance_criteria,
        created_at_utc=created_at_utc,
        related_adr_uid=related_adr_uid,
    )


def derive_allowlist(
    intention: Intention,
    file_context: FileContext,
    decision_patch: DecisionPatch | None,
) -> tuple[str, ...] | None:
    """
    Derive allowlist from file_context based on intention and patch.

    This is a heuristic-based derivation. Returns None if cannot determine
    (needs clarification).

    Strategy:
    1. Look for category-specific directories in file_context
    2. Match intention keywords to directory patterns
    3. Return None if no confident match (needs user clarification)

    Args:
        intention: User's intention
        file_context: Repository file topology
        decision_patch: Optional decision patch

    Returns:
        Tuple of allowlist paths/patterns, or None if undetermined
    """
    if not file_context.paths:
        return None

    intention_lower = intention.text.lower()
    matched_paths: list[str] = []

    # Category-specific directory patterns
    category_patterns: dict[str, tuple[str, ...]] = {
        "authentication": ("auth", "login", "session", "user"),
        "database": ("db", "database", "models", "migrations", "schema"),
        "frontend": ("components", "pages", "views", "ui", "src/app"),
        "backend": ("api", "server", "routes", "controllers", "handlers"),
        "infra": ("infra", "deploy", "docker", "k8s", "ci", "config"),
    }

    # Determine target category
    target_category: str | None = None
    if decision_patch:
        target_category = decision_patch.category.lower()
    else:
        # Try to infer from intention
        for cat, keywords in category_patterns.items():
            for keyword in keywords:
                if keyword in intention_lower:
                    target_category = cat
                    break
            if target_category:
                break

    if target_category is None:
        # Can't determine category, need clarification
        return None

    # Find matching paths
    patterns = category_patterns.get(target_category, ())
    for path in file_context.paths:
        path_lower = path.lower()
        for pattern in patterns:
            if pattern in path_lower:
                # Add parent directory, not individual file
                if "/" in path:
                    dir_path = "/".join(path.split("/")[:-1]) + "/"
                    if dir_path not in matched_paths:
                        matched_paths.append(dir_path)
                else:
                    if path not in matched_paths:
                        matched_paths.append(path)
                break

    if not matched_paths:
        # No matches found, need clarification
        return None

    return tuple(sorted(set(matched_paths)))


def derive_forbidden(
    allowlist: tuple[str, ...],
    file_context: FileContext,
) -> tuple[str, ...]:
    """
    Derive forbidden list based on allowlist and file context.

    Default strategy: forbid common sensitive/legacy directories.

    Args:
        allowlist: Current allowlist
        file_context: Repository file topology

    Returns:
        Tuple of forbidden paths/patterns
    """
    # Common forbidden patterns
    common_forbidden = (
        ".git/",
        "node_modules/",
        "dist/",
        "build/",
        "__pycache__/",
        ".env",
        "credentials",
        "secrets",
    )

    forbidden: list[str] = []

    # Check if patterns exist in file_context
    for pattern in common_forbidden:
        for path in file_context.paths:
            if pattern.rstrip("/") in path:
                forbidden.append(pattern)
                break

    # Don't forbid anything in allowlist
    forbidden = [f for f in forbidden if f not in allowlist]

    return tuple(sorted(set(forbidden)))


def generate_title(
    intention: Intention,
    decision_patch: DecisionPatch | None,
) -> str:
    """
    Generate a title for the task.

    Args:
        intention: User's intention
        decision_patch: Optional decision patch

    Returns:
        Generated title
    """
    # Use intention text, truncated and cleaned
    title = intention.text.strip()

    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]

    # Truncate if too long
    if len(title) > 80:
        title = title[:77] + "..."

    return title


def generate_objective(
    intention: Intention,
    decision_patch: DecisionPatch | None,
) -> str:
    """
    Generate an objective for the task.

    Args:
        intention: User's intention
        decision_patch: Optional decision patch

    Returns:
        Generated objective
    """
    objective = intention.text.strip()

    # Add context from patch if available
    if decision_patch:
        fields_str = ", ".join(f"{k}={v}" for k, v in decision_patch.fields)
        objective = f"{objective}\n\nDecision: {decision_patch.category} - {fields_str}"

    return objective
