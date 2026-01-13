"""Local answer validation for CLI."""

from __future__ import annotations

from preflights.cli.errors import InvalidAnswerError
from preflights.cli.state import StoredQuestion

# Canonical value for "Other" option
OTHER_SPECIFY = "Other (specify)"


def validate_single_choice(
    question_id: str,
    answer: str,
    options: tuple[str, ...],
) -> str:
    """
    Validate single choice answer.

    Args:
        question_id: Question ID for error messages
        answer: User's answer
        options: Valid options

    Returns:
        Normalized answer (original case from options)

    Raises:
        InvalidAnswerError: If answer not in options
    """
    answer_lower = answer.lower()
    for opt in options:
        if opt.lower() == answer_lower:
            return opt  # Return original case

    raise InvalidAnswerError(
        question_id,
        f"'{answer}' is not a valid option",
        options,
    )


def validate_multi_choice(
    question_id: str,
    answers: list[str],
    options: tuple[str, ...],
    min_selections: int | None,
    max_selections: int | None,
) -> list[str]:
    """
    Validate multi choice answer.

    Args:
        question_id: Question ID for error messages
        answers: User's answers (list)
        options: Valid options
        min_selections: Minimum required selections
        max_selections: Maximum allowed selections

    Returns:
        Normalized answers (original case from options)

    Raises:
        InvalidAnswerError: If validation fails
    """
    if not answers:
        if min_selections and min_selections > 0:
            raise InvalidAnswerError(
                question_id,
                f"requires at least {min_selections} selection(s)",
                options,
            )
        return []

    # Validate each answer
    normalized: list[str] = []
    options_lower = {opt.lower(): opt for opt in options}

    for ans in answers:
        ans_lower = ans.lower()
        if ans_lower not in options_lower:
            raise InvalidAnswerError(
                question_id,
                f"'{ans}' is not a valid option",
                options,
            )
        normalized.append(options_lower[ans_lower])

    # Check min/max
    if min_selections and len(normalized) < min_selections:
        raise InvalidAnswerError(
            question_id,
            f"requires at least {min_selections} selection(s), got {len(normalized)}",
            options,
        )

    if max_selections and len(normalized) > max_selections:
        raise InvalidAnswerError(
            question_id,
            f"allows at most {max_selections} selection(s), got {len(normalized)}",
            options,
        )

    return normalized


def validate_free_text(question_id: str, answer: str) -> str:
    """
    Validate free text answer.

    Args:
        question_id: Question ID for error messages
        answer: User's answer

    Returns:
        Trimmed answer

    Raises:
        InvalidAnswerError: If answer is empty
    """
    trimmed = answer.strip()
    if not trimmed:
        raise InvalidAnswerError(question_id, "cannot be empty")
    return trimmed


def validate_answer(
    question: StoredQuestion,
    answer: str | list[str],
) -> str | list[str]:
    """
    Validate answer against question type.

    Args:
        question: Question definition
        answer: User's answer

    Returns:
        Validated and normalized answer

    Raises:
        InvalidAnswerError: If validation fails
    """
    if question.type == "single_choice":
        if not question.options:
            raise InvalidAnswerError(question.id, "question has no options defined")
        if isinstance(answer, list):
            if len(answer) != 1:
                raise InvalidAnswerError(question.id, "expected single value, got list")
            answer = answer[0]
        return validate_single_choice(question.id, answer, question.options)

    elif question.type == "multi_choice":
        if not question.options:
            raise InvalidAnswerError(question.id, "question has no options defined")
        if isinstance(answer, str):
            # Split on comma for multi-choice
            answer = [a.strip() for a in answer.split(",") if a.strip()]
        return validate_multi_choice(
            question.id,
            answer,
            question.options,
            question.min_selections,
            question.max_selections,
        )

    elif question.type == "free_text":
        if isinstance(answer, list):
            answer = ", ".join(answer)
        return validate_free_text(question.id, answer)

    else:
        # Unknown type, pass through
        return answer


def parse_key_value_answers(args: tuple[str, ...]) -> dict[str, str | list[str]]:
    """
    Parse key=value answer arguments.

    Args:
        args: Tuple of "key=value" strings

    Returns:
        Dict mapping question_id to answer value

    Format:
        - Single: key=value
        - Multi: key=value1,value2,value3
        - URL with = allowed: url=https://example.com?key=value
    """
    result: dict[str, str | list[str]] = {}

    for arg in args:
        if "=" not in arg:
            continue

        key, value = arg.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        # Check if it looks like a multi-value (contains comma, not in URL)
        # Heuristic: if value contains :// it's probably a URL
        if "," in value and "://" not in value:
            result[key] = [v.strip() for v in value.split(",") if v.strip()]
        else:
            result[key] = value

    return result
