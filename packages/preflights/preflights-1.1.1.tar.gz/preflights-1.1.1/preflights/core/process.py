"""
Preflights Core - Main Entry Point.

Single function API: process()
Pure function. Stateless. Deterministic.
No I/O.
"""

from __future__ import annotations

from preflights.core.adr_builder import (
    build_adr,
    generate_adr_title,
    generate_changes_description,
    generate_context,
    generate_decision,
    generate_rationale,
)
from preflights.core.clarifier import generate_questions
from preflights.core.decision_detector import detect_adr_need
from preflights.core.snapshot_builder import apply_patch
from preflights.core.task_builder import (
    build_task,
    derive_allowlist,
    derive_forbidden,
    generate_objective,
    generate_title,
)
from preflights.core.types import (
    ArchitectureState,
    Completed,
    ConversationState,
    CoreError,
    DecisionPatch,
    ErrorCode,
    FileContext,
    HeuristicsConfig,
    Intention,
    NeedsClarification,
    ProcessResult,
    ReadyToBuild,
)
from preflights.core.validators import (
    validate_adr,
    validate_decision_patch,
    validate_snapshot,
    validate_task,
)


def process(
    *,
    intention: Intention,
    current_architecture: ArchitectureState | None,
    file_context: FileContext,
    conversation_state: ConversationState | None,
    heuristics_config: HeuristicsConfig,
    decision_patch: DecisionPatch | None,
    # Injected only when ready to produce artifacts
    uid_for_adr: str | None = None,
    uid_for_task: str | None = None,
    now_utc: str | None = None,
) -> ProcessResult:
    """
    Main entry point for Preflights Core.

    Pure function. Stateless. Deterministic.

    Behavior depends on inputs:
    1. No decision_patch → NeedsClarification (generate questions)
    2. Valid patch, no UIDs → ReadyToBuild (signal Application to inject UIDs)
    3. Valid patch with UIDs → Completed (produce artifacts)
    4. Invalid inputs → CoreError

    Args:
        intention: User's intention
        current_architecture: Current architecture state (None if none exists)
        file_context: Repository file topology
        conversation_state: Previous questions/answers (None if first call)
        heuristics_config: Configuration for heuristics
        decision_patch: Structured decision patch (None if not yet extracted)
        uid_for_adr: UID for ADR (injected by Application)
        uid_for_task: UID for Task (injected by Application)
        now_utc: Current UTC time (injected by Application)

    Returns:
        ProcessResult: One of NeedsClarification, ReadyToBuild, Completed, CoreError
    """
    # ==========================================================================
    # PHASE 1: Generate questions if no patch
    # ==========================================================================
    if decision_patch is None:
        return _generate_clarification_questions(
            intention,
            current_architecture,
            file_context,
            conversation_state,
            heuristics_config,
        )

    # ==========================================================================
    # PHASE 2: Validate decision patch
    # ==========================================================================
    patch_error = validate_decision_patch(decision_patch, heuristics_config.schema)
    if patch_error is not None:
        return patch_error

    # ==========================================================================
    # PHASE 3: Detect if ADR is needed
    # ==========================================================================
    adr_decision = detect_adr_need(
        intention,
        decision_patch,
        heuristics_config,
        current_architecture,
    )

    # ==========================================================================
    # PHASE 4: Derive allowlist
    # ==========================================================================
    # First check if user already provided allowlist_paths
    allowlist = _extract_allowlist_from_answers(conversation_state)
    if allowlist is None:
        # Try to derive from file context
        allowlist = derive_allowlist(intention, file_context, decision_patch)
    if allowlist is None:
        # Cannot determine allowlist, need clarification
        return _request_allowlist_clarification(
            intention, file_context, conversation_state
        )

    # ==========================================================================
    # PHASE 5: If no UIDs, return ReadyToBuild
    # ==========================================================================
    if uid_for_task is None:
        return _create_ready_to_build(
            intention,
            decision_patch,
            adr_decision.needs_adr,
            adr_decision.category,
            allowlist,
            file_context,
            conversation_state,
        )

    # ==========================================================================
    # PHASE 6: Build artifacts (UIDs provided)
    # ==========================================================================
    return _build_artifacts(
        intention=intention,
        current_architecture=current_architecture,
        file_context=file_context,
        heuristics_config=heuristics_config,
        decision_patch=decision_patch,
        adr_decision_needs_adr=adr_decision.needs_adr,
        adr_decision_category=adr_decision.category,
        allowlist=allowlist,
        uid_for_adr=uid_for_adr,
        uid_for_task=uid_for_task,
        now_utc=now_utc,
        conversation_state=conversation_state,
    )


def _generate_clarification_questions(
    intention: Intention,
    current_architecture: ArchitectureState | None,
    file_context: FileContext,
    conversation_state: ConversationState | None,
    heuristics_config: HeuristicsConfig,
) -> NeedsClarification:
    """Generate clarification questions when no patch provided."""
    already_asked: frozenset[str] = frozenset()
    if conversation_state is not None:
        already_asked = frozenset(q.id for q in conversation_state.asked_questions)

    questions = generate_questions(
        intention,
        current_architecture,
        file_context,
        heuristics_config,
        already_asked,
    )

    return NeedsClarification(questions=questions)


def _extract_allowlist_from_answers(
    conversation_state: ConversationState | None,
) -> tuple[str, ...] | None:
    """
    Extract allowlist from user's answer to allowlist_paths question.

    Returns None if not answered.
    """
    if conversation_state is None:
        return None

    for answer in conversation_state.answers:
        if answer.question_id == "allowlist_paths":
            value = answer.value
            if isinstance(value, str) and value.strip():
                # Parse comma-separated paths
                paths = [p.strip() for p in value.split(",") if p.strip()]
                if paths:
                    return tuple(paths)
            elif isinstance(value, tuple) and value:
                return value

    return None


def _request_allowlist_clarification(
    intention: Intention,
    file_context: FileContext,
    conversation_state: ConversationState | None,
) -> NeedsClarification:
    """Request clarification for allowlist when cannot be determined."""
    from preflights.core.types import Question

    already_asked: frozenset[str] = frozenset()
    if conversation_state is not None:
        already_asked = frozenset(q.id for q in conversation_state.asked_questions)

    # Generate allowlist question
    questions: list[Question] = []

    if "allowlist_paths" not in already_asked:
        questions.append(
            Question(
                id="allowlist_paths",
                type="free_text",
                question="Which files or directories should this change affect? (comma-separated paths or patterns)",
            )
        )

    if "acceptance_criteria" not in already_asked:
        questions.append(
            Question(
                id="acceptance_criteria",
                type="free_text",
                question="How will we know this is complete? (acceptance criteria)",
            )
        )

    return NeedsClarification(questions=tuple(questions))


def _create_ready_to_build(
    intention: Intention,
    decision_patch: DecisionPatch,
    needs_adr: bool,
    category: str | None,
    allowlist: tuple[str, ...],
    file_context: FileContext,
    conversation_state: ConversationState | None,
) -> ReadyToBuild:
    """Create ReadyToBuild result when validation passes but no UIDs."""
    title = generate_title(intention, decision_patch)
    objective = generate_objective(intention, decision_patch)
    forbidden = derive_forbidden(allowlist, file_context)

    # Extract acceptance criteria from answers if available
    acceptance_criteria: tuple[str, ...] = ()
    context_text = intention.text
    if intention.optional_context:
        context_text = f"{intention.text}\n\n{intention.optional_context}"

    if conversation_state is not None:
        for answer in conversation_state.answers:
            if answer.question_id == "acceptance_criteria":
                if isinstance(answer.value, str):
                    # Split by newlines or commas
                    criteria = [
                        c.strip()
                        for c in answer.value.replace("\n", ",").split(",")
                        if c.strip()
                    ]
                    acceptance_criteria = tuple(criteria)

    # Default acceptance criteria if none provided
    if not acceptance_criteria:
        acceptance_criteria = (f"Implementation of '{intention.text}' is complete and working",)

    # Extract technical constraints from answers
    technical_constraints: tuple[str, ...] = ()
    if decision_patch.fields:
        constraints = [f"Use {v} for {k}" for k, v in decision_patch.fields]
        technical_constraints = tuple(constraints)

    return ReadyToBuild(
        needs_adr=needs_adr,
        category=category,
        title=title,
        allowlist=allowlist,
        forbidden=forbidden,
        technical_constraints=technical_constraints,
        acceptance_criteria=acceptance_criteria,
        objective=objective,
        context_text=context_text,
        # ADR fields
        decision_context=generate_context(intention.text, category or decision_patch.category),
        decision_text=generate_decision(decision_patch),
        rationale=generate_rationale(decision_patch),
        alternatives=("No alternatives explicitly considered",),
        consequences_positive=("Addresses the requirement",),
        consequences_negative=(),
        consequences_neutral=(),
    )


def _build_artifacts(
    *,
    intention: Intention,
    current_architecture: ArchitectureState | None,
    file_context: FileContext,
    heuristics_config: HeuristicsConfig,
    decision_patch: DecisionPatch,
    adr_decision_needs_adr: bool,
    adr_decision_category: str | None,
    allowlist: tuple[str, ...],
    uid_for_adr: str | None,
    uid_for_task: str,
    now_utc: str | None,
    conversation_state: ConversationState | None,
) -> ProcessResult:
    """Build artifacts when UIDs are provided."""
    # Validate required inputs for Completed
    if now_utc is None:
        return CoreError(
            code=ErrorCode.VALIDATION_FAILED,
            message="now_utc is required when building artifacts",
            recovery_hint="Provide now_utc parameter",
        )

    if adr_decision_needs_adr and uid_for_adr is None:
        return CoreError(
            code=ErrorCode.VALIDATION_FAILED,
            message="uid_for_adr is required when ADR is needed",
            recovery_hint="Provide uid_for_adr parameter",
        )

    # Build ADR if needed
    adr = None
    updated_architecture: ArchitectureState | None = None

    if adr_decision_needs_adr and uid_for_adr is not None:
        # Build new snapshot
        new_snapshot = apply_patch(
            current_architecture,
            decision_patch,
            uid_for_adr,
            heuristics_config.schema,
        )

        # Validate snapshot
        snapshot_error = validate_snapshot(
            new_snapshot, current_architecture, heuristics_config.schema
        )
        if snapshot_error is not None:
            return snapshot_error

        # Generate ADR content
        previous_uid = current_architecture.uid if current_architecture else None
        category = adr_decision_category or decision_patch.category
        title = generate_adr_title(category, decision_patch)
        changes = generate_changes_description(
            current_architecture, decision_patch, uid_for_adr
        )

        # Build ADR
        adr = build_adr(
            uid=uid_for_adr,
            date_utc=now_utc[:10] if len(now_utc) >= 10 else now_utc,  # Extract date
            title=title,
            category=category,
            decision_patch=decision_patch,
            new_snapshot=new_snapshot,
            previous_uid=previous_uid,
            context=generate_context(intention.text, category),
            decision=generate_decision(decision_patch),
            rationale=generate_rationale(decision_patch),
            alternatives=("No alternatives explicitly considered",),
            consequences_positive=("Addresses the requirement",),
            consequences_negative=(),
            consequences_neutral=(),
            changes_in_this_version=changes,
        )

        # Validate ADR
        adr_error = validate_adr(adr, heuristics_config.schema)
        if adr_error is not None:
            return adr_error

        updated_architecture = new_snapshot

    # Build Task
    title = generate_title(intention, decision_patch)
    objective = generate_objective(intention, decision_patch)
    forbidden = derive_forbidden(allowlist, file_context)

    # Context for task
    context_text = intention.text
    if intention.optional_context:
        context_text = f"{intention.text}\n\n{intention.optional_context}"
    if adr is not None:
        context_text = f"{context_text}\n\nRelated ADR: {adr.uid}"

    # Technical constraints from patch
    technical_constraints: tuple[str, ...] = ()
    if decision_patch.fields:
        constraints = [f"Use {v} for {k}" for k, v in decision_patch.fields]
        technical_constraints = tuple(constraints)

    # Acceptance criteria from conversation
    acceptance_criteria: tuple[str, ...] = (
        f"Implementation of '{intention.text}' is complete and working",
    )
    if conversation_state is not None:
        for answer in conversation_state.answers:
            if answer.question_id == "acceptance_criteria":
                if isinstance(answer.value, str) and answer.value.strip():
                    criteria = [
                        c.strip()
                        for c in answer.value.replace("\n", ",").split(",")
                        if c.strip()
                    ]
                    acceptance_criteria = tuple(criteria)

    task = build_task(
        uid=uid_for_task,
        created_at_utc=now_utc,
        title=title,
        objective=objective,
        context=context_text,
        allowlist=allowlist,
        forbidden=forbidden,
        technical_constraints=technical_constraints,
        acceptance_criteria=acceptance_criteria,
        related_adr_uid=adr.uid if adr else None,
    )

    # Validate task
    task_error = validate_task(task)
    if task_error is not None:
        return task_error

    return Completed(
        task=task,
        adr=adr,
        updated_architecture=updated_architecture,
    )
