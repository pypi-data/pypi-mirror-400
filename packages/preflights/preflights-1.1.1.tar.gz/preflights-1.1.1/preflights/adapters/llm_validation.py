"""
LLM Response Validation & Repair.

This module enforces behavioral invariants for all LLM adapters.
It is the last line of defense between probabilistic LLM outputs
and deterministic Preflights logic.

The MockLLMAdapter defines the source of truth for:
- Question budget (1-2 per turn)
- Progress semantics
- DecisionPatch validity rules
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, replace
from typing import Any, Iterable

from preflights.application.types import LLMResponse, Question

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

MAX_QUESTIONS_PER_TURN = 2

ALLOWED_DECISION_CATEGORIES = frozenset({
    "Authentication",
    "Database",
    "Frontend",
    "Backend",
    "Infra",
    "Other",
})

# Defensive normalization for category aliases
CATEGORY_ALIASES: dict[str, str] = {
    "Infrastructure": "Infra",
    "Auth": "Authentication",
    "DB": "Database",
    "UI": "Frontend",
}


def normalize_category(category: str) -> str:
    """Normalize category name using aliases."""
    return CATEGORY_ALIASES.get(category, category)


# Patterns that indicate placeholder/guessed values (forbidden)
PLACEHOLDER_PATTERNS = [
    r"\bTBD\b",
    r"\bTODO\b",
    r"\bunknown\b",
    r"\bn/?a\b",
    r"\bto be defined\b",
    r"\bto be determined\b",
    r"\bplaceholder\b",
]

PLACEHOLDER_REGEX = re.compile("|".join(PLACEHOLDER_PATTERNS), re.IGNORECASE)


# =============================================================================
# VALIDATION ERRORS
# =============================================================================


class LLMValidationError(Exception):
    """Raised when LLM response fails validation in strict mode."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


# =============================================================================
# VALIDATION RESULT
# =============================================================================


@dataclass
class ValidationResult:
    """Result of validation with optional repairs."""

    valid: bool
    repaired: bool = False
    warnings: list[str] | None = None
    data: Any = None  # Repaired data (LLMResponse, dict, etc.)


# =============================================================================
# UTILITIES
# =============================================================================


def _contains_placeholder(value: str) -> bool:
    """Check if value contains forbidden placeholder patterns."""
    return bool(PLACEHOLDER_REGEX.search(value))


def _ensure(condition: bool, code: str, message: str, strict: bool = True) -> bool:
    """
    Assert a condition, raising in strict mode or returning False otherwise.

    Returns True if condition is met, False if not (in non-strict mode).
    """
    if not condition:
        if strict:
            raise LLMValidationError(code, message)
        return False
    return True


# =============================================================================
# CLARIFICATION RESPONSE VALIDATION
# =============================================================================


def validate_clarification_response(
    response: LLMResponse | dict[str, Any],
    strict: bool = False,
) -> ValidationResult:
    """
    Validate and optionally repair a clarification response.

    Checks:
    - Max 2 questions per turn
    - len(questions) == len(missing_info) for non-conditional questions
    - Each question has id, type, question
    - Options present and valid if type is single_choice/multi_choice
    - progress == 1.0 if missing_info is empty

    Args:
        response: LLMResponse or raw dict from tool call
        strict: If True, raise on validation errors. If False, repair + warn.

    Returns:
        ValidationResult with valid flag and repaired data.

    Raises:
        LLMValidationError: In strict mode when validation fails.
    """
    warnings: list[str] = []
    repaired = False

    # Normalize to dict for processing
    if isinstance(response, LLMResponse):
        data: dict[str, Any] = {
            "questions": list(response.questions),
            "missing_info": list(response.missing_info),
            "decision_hint": response.decision_hint,
            "progress": response.progress,
        }
        is_typed = True
    else:
        data = dict(response)
        is_typed = False

    raw_questions = data.get("questions", [])
    questions: list[dict[str, Any] | Question] = raw_questions if isinstance(raw_questions, list) else []
    raw_missing = data.get("missing_info", [])
    missing_info: list[str] = list(raw_missing) if isinstance(raw_missing, (list, tuple)) else []
    raw_progress = data.get("progress", 0.5)
    progress: float = float(raw_progress) if isinstance(raw_progress, (int, float)) else 0.5

    # -------------------------------------------------------------------------
    # Check 1: Max questions per turn
    # -------------------------------------------------------------------------
    if len(questions) > MAX_QUESTIONS_PER_TURN:
        msg = f"Too many questions: {len(questions)} > {MAX_QUESTIONS_PER_TURN}"
        if strict:
            raise LLMValidationError("TOO_MANY_QUESTIONS", msg, {"count": len(questions)})
        questions = questions[:MAX_QUESTIONS_PER_TURN]
        data["questions"] = questions
        warnings.append(f"REPAIR: {msg}. Truncated to {MAX_QUESTIONS_PER_TURN}.")
        repaired = True

    # -------------------------------------------------------------------------
    # Check 2: Validate each question
    # -------------------------------------------------------------------------
    valid_questions: list[dict[str, Any] | Question] = []
    for i, q in enumerate(questions):
        q_dict = _question_to_dict(q)
        q_valid, q_repaired, q_warnings = _validate_question(q_dict, i, strict)

        if q_valid:
            valid_questions.append(q_dict if not is_typed else q)
        else:
            repaired = True

        if q_repaired:
            repaired = True
            valid_questions[-1] = q_dict  # Use repaired version

        warnings.extend(q_warnings)

    data["questions"] = valid_questions
    questions = valid_questions

    # -------------------------------------------------------------------------
    # Check 3: questions/missing_info length match (non-conditional only)
    # -------------------------------------------------------------------------
    non_conditional = [
        q for q in questions
        if not _question_to_dict(q).get("depends_on_question_id")
    ]

    if len(non_conditional) != len(missing_info):
        msg = f"Mismatch: {len(non_conditional)} questions vs {len(missing_info)} missing_info"
        if strict:
            raise LLMValidationError("QUESTION_MISSING_INFO_MISMATCH", msg)
        # Repair: regenerate missing_info from question IDs
        missing_info = [_question_to_dict(q).get("id", f"q_{i}") for i, q in enumerate(non_conditional)]
        data["missing_info"] = missing_info
        warnings.append(f"REPAIR: {msg}. Regenerated missing_info.")
        repaired = True

    # -------------------------------------------------------------------------
    # Check 4: Progress invariant
    # -------------------------------------------------------------------------
    if not missing_info and progress != 1.0:
        data["progress"] = 1.0
        warnings.append(f"REPAIR: missing_info empty but progress={progress}. Set to 1.0.")
        repaired = True
    elif missing_info and progress == 1.0:
        data["progress"] = 0.99
        warnings.append("REPAIR: missing_info not empty but progress=1.0. Clamped to 0.99.")
        repaired = True

    # -------------------------------------------------------------------------
    # Build result
    # -------------------------------------------------------------------------
    if warnings:
        for w in warnings:
            logger.warning(f"[LLM Validation] {w}")

    # Convert back to LLMResponse if input was typed
    result_data: LLMResponse | dict[str, Any]
    if is_typed:
        final_questions = data.get("questions", [])
        final_missing = data.get("missing_info", [])
        final_hint = data.get("decision_hint", "unsure")
        final_progress = data.get("progress", 0.5)

        result_data = LLMResponse(
            questions=tuple(_dict_to_question(q) if isinstance(q, dict) else q for q in final_questions),
            missing_info=tuple(str(m) for m in final_missing),
            decision_hint=final_hint if final_hint in ("task", "adr", "unsure") else "unsure",
            progress=float(final_progress) if isinstance(final_progress, (int, float)) else 0.5,
        )
    else:
        result_data = data

    return ValidationResult(
        valid=not warnings,
        repaired=repaired,
        warnings=warnings if warnings else None,
        data=result_data,
    )


def _question_to_dict(q: Question | dict[str, Any]) -> dict[str, Any]:
    """Convert Question to dict if needed."""
    if isinstance(q, dict):
        return q
    return {
        "id": q.id,
        "type": q.type,
        "question": q.question,
        "options": q.options,
        "optional": q.optional,
        "depends_on_question_id": q.depends_on_question_id,
        "depends_on_value": q.depends_on_value,
    }


def _dict_to_question(d: dict[str, Any]) -> Question:
    """Convert dict to Question."""
    return Question(
        id=d.get("id", ""),
        type=d.get("type", "free_text"),
        question=d.get("question", ""),
        options=tuple(d["options"]) if d.get("options") else None,
        optional=d.get("optional", False),
        depends_on_question_id=d.get("depends_on_question_id"),
        depends_on_value=d.get("depends_on_value"),
    )


def _validate_question(
    q: dict[str, Any],
    index: int,
    strict: bool,
) -> tuple[bool, bool, list[str]]:
    """
    Validate a single question.

    Returns: (valid, repaired, warnings)
    """
    warnings: list[str] = []
    repaired = False
    valid = True

    q_id = q.get("id")
    q_type = q.get("type")
    q_text = q.get("question")

    # Required fields
    if not q_id or not q_type or not q_text:
        msg = f"Question {index} missing required fields"
        if strict:
            raise LLMValidationError("INVALID_QUESTION", msg, {"question": q})
        warnings.append(f"REPAIR: {msg}. Skipping.")
        return False, False, warnings

    # Options for choice questions
    if q_type in ("single_choice", "multi_choice"):
        options = q.get("options")
        if not options or len(options) < 2:
            msg = f"Question '{q_id}' is {q_type} but has insufficient options"
            if strict:
                raise LLMValidationError("MISSING_OPTIONS", msg)
            # Repair: convert to free_text
            q["type"] = "free_text"
            q.pop("options", None)
            warnings.append(f"REPAIR: {msg}. Converted to free_text.")
            repaired = True

    # Free text should not have options
    elif q_type == "free_text" and q.get("options"):
        q.pop("options", None)
        repaired = True

    return valid, repaired, warnings


# =============================================================================
# DECISION RESPONSE VALIDATION
# =============================================================================


def validate_decision_response(
    response: dict[str, Any],
    strict: bool = False,
) -> ValidationResult:
    """
    Validate and optionally repair a decision extraction response.

    Checks:
    - status is present and valid ("extracted" or "insufficient")
    - If extracted: category must be valid, fields must be non-empty
    - If extracted: no placeholder values in fields
    - If insufficient: reason must be present

    Args:
        response: Raw dict from tool call
        strict: If True, raise on validation errors. If False, repair + warn.

    Returns:
        ValidationResult with valid flag and repaired data.

    Raises:
        LLMValidationError: In strict mode when validation fails.
    """
    warnings: list[str] = []
    repaired = False
    data = dict(response)

    status = data.get("status")
    raw_category = data.get("category")
    category = normalize_category(str(raw_category)) if raw_category else None
    data["category"] = category  # Store normalized
    fields = data.get("fields", [])
    reason = data.get("reason")

    # -------------------------------------------------------------------------
    # Check 1: Status present and valid
    # -------------------------------------------------------------------------
    if status not in ("extracted", "insufficient"):
        msg = f"Invalid or missing status: {status}"
        if strict:
            raise LLMValidationError("INVALID_STATUS", msg)
        # Infer from other fields
        if category and fields:
            data["status"] = "extracted"
            status = "extracted"
            warnings.append(f"REPAIR: {msg}. Inferred 'extracted'.")
        else:
            data["status"] = "insufficient"
            data["reason"] = reason or "Status was missing or invalid"
            status = "insufficient"
            warnings.append(f"REPAIR: {msg}. Set to 'insufficient'.")
        repaired = True

    # -------------------------------------------------------------------------
    # Check 2: Insufficient requires reason
    # -------------------------------------------------------------------------
    if status == "insufficient":
        if not reason or not reason.strip():
            msg = "status='insufficient' but reason is missing"
            if strict:
                raise LLMValidationError("MISSING_REASON", msg)
            data["reason"] = "Insufficient information to extract decision"
            warnings.append(f"REPAIR: {msg}. Added generic reason.")
            repaired = True
        return _build_decision_result(data, warnings, repaired)

    # -------------------------------------------------------------------------
    # Check 3: Extracted requires valid category
    # -------------------------------------------------------------------------
    if category not in ALLOWED_DECISION_CATEGORIES:
        msg = f"Invalid decision category: {category}"
        if strict:
            raise LLMValidationError("INVALID_CATEGORY", msg, {"category": category})
        data["status"] = "insufficient"
        data["reason"] = f"Invalid category: {category}"
        warnings.append(f"REPAIR: {msg}. Switched to 'insufficient'.")
        repaired = True
        return _build_decision_result(data, warnings, repaired)

    # -------------------------------------------------------------------------
    # Check 4: Extracted requires non-empty fields
    # -------------------------------------------------------------------------
    if not fields:
        msg = "status='extracted' but fields is empty"
        if strict:
            raise LLMValidationError("EMPTY_FIELDS", msg)
        data["status"] = "insufficient"
        data["reason"] = f"No fields extracted for category {category}"
        warnings.append(f"REPAIR: {msg}. Switched to 'insufficient'.")
        repaired = True
        return _build_decision_result(data, warnings, repaired)

    # -------------------------------------------------------------------------
    # Check 5: No placeholder values in fields
    # -------------------------------------------------------------------------
    clean_fields = []
    for field in fields:
        key = field.get("key", "")
        value = field.get("value", "")

        if _contains_placeholder(value):
            msg = f"Placeholder detected in field '{key}': {value}"
            if strict:
                raise LLMValidationError("PLACEHOLDER_VALUE", msg, {"field": key, "value": value})
            warnings.append(f"REPAIR: {msg}. Removed field.")
            repaired = True
            continue

        if key and value:
            clean_fields.append(field)

    if not clean_fields:
        data["status"] = "insufficient"
        data["reason"] = "All fields contained placeholder values"
        data["fields"] = []
        warnings.append("REPAIR: No valid fields remain. Switched to 'insufficient'.")
        repaired = True
    else:
        data["fields"] = clean_fields

    return _build_decision_result(data, warnings, repaired)


def _build_decision_result(
    data: dict[str, Any],
    warnings: list[str],
    repaired: bool,
) -> ValidationResult:
    """Build ValidationResult for decision response."""
    if warnings:
        for w in warnings:
            logger.warning(f"[LLM Validation] {w}")

    return ValidationResult(
        valid=not warnings,
        repaired=repaired,
        warnings=warnings if warnings else None,
        data=data,
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def validate_and_repair_clarification(
    response: LLMResponse | dict[str, Any],
) -> LLMResponse | dict[str, Any]:
    """
    Validate and repair clarification response (production mode).

    Always returns usable data, logging warnings for repairs.
    """
    result = validate_clarification_response(response, strict=False)
    return result.data if result.data is not None else response


def validate_and_repair_decision(
    response: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate and repair decision response (production mode).

    Always returns usable data, logging warnings for repairs.
    """
    result = validate_decision_response(response, strict=False)
    data = result.data
    return data if isinstance(data, dict) else response


def validate_clarification_strict(response: LLMResponse | dict[str, Any]) -> LLMResponse | dict[str, Any]:
    """
    Validate clarification response in strict mode.

    Raises LLMValidationError if invalid.
    Returns validated response.
    """
    result = validate_clarification_response(response, strict=True)
    return result.data if result.data is not None else response


def validate_decision_strict(response: dict[str, Any]) -> dict[str, Any]:
    """
    Validate decision response in strict mode.

    Raises LLMValidationError if invalid.
    Returns validated dict.
    """
    result = validate_decision_response(response, strict=True)
    data = result.data
    return data if isinstance(data, dict) else response


# =============================================================================
# BATCH HELPERS
# =============================================================================


def validate_clarification_batch(
    responses: Iterable[LLMResponse | dict[str, Any]],
    strict: bool = False,
) -> list[ValidationResult]:
    """Validate multiple clarification responses."""
    return [validate_clarification_response(r, strict=strict) for r in responses]


def validate_decision_batch(
    responses: Iterable[dict[str, Any]],
    strict: bool = False,
) -> list[ValidationResult]:
    """Validate multiple decision responses."""
    return [validate_decision_response(r, strict=strict) for r in responses]
