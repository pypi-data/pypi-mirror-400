"""
Preflights Application Types.

Public types for the PreflightsApp contract.
These types are FROZEN for V1 (see PREFLIGHTS_APP_CONTRACT.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# =============================================================================
# QUESTION TYPE (shared with Core but Application-owned representation)
# =============================================================================


@dataclass(frozen=True)
class Question:
    """A clarification question."""

    id: str
    type: Literal["single_choice", "multi_choice", "free_text"]
    question: str
    options: tuple[str, ...] | None = None
    min_selections: int | None = None
    max_selections: int | None = None
    optional: bool = False
    # Conditional visibility (for __other fields)
    depends_on_question_id: str | None = None
    depends_on_value: str | None = None


# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass(frozen=True)
class PreflightStartResult:
    """Result of start_preflight()."""

    session_id: str
    questions: tuple[Question, ...]


@dataclass(frozen=True)
class PreflightArtifacts:
    """Artifacts created upon completion."""

    task_path: str  # Relative path to CURRENT_TASK.md
    adr_path: str | None = None  # Relative path to ADR file (if created)
    architecture_state_path: str | None = None  # Relative path to ARCHITECTURE_STATE.md
    agent_prompt_path: str | None = None  # Relative path to AGENT_PROMPT.md
    agent_prompt: str | None = None  # The prompt content for the coding agent


@dataclass(frozen=True)
class PreflightError:
    """Error details."""

    code: str
    message: str
    details: tuple[tuple[str, str], ...] = ()
    recovery_hint: str | None = None


@dataclass(frozen=True)
class PreflightContinueResult:
    """Result of continue_preflight()."""

    status: Literal["needs_more_answers", "needs_clarification", "completed", "error"]

    # If status = "needs_more_answers" or "needs_clarification"
    questions: tuple[Question, ...] | None = None

    # If status = "completed"
    artifacts: PreflightArtifacts | None = None

    # If status = "error"
    error: PreflightError | None = None


# =============================================================================
# ERROR CODES (aligned with contract)
# =============================================================================


class AppErrorCode:
    """Application error codes (aligned with PREFLIGHTS_APP_CONTRACT.md)."""

    SESSION_EXPIRED = "SESSION_EXPIRED"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    FILESYSTEM_ERROR = "FILESYSTEM_ERROR"
    PARSE_ERROR = "PARSE_ERROR"
    STATE_CORRUPTION = "STATE_CORRUPTION"
    PATCH_EXTRACTION_FAILED = "PATCH_EXTRACTION_FAILED"
    INVALID_ANSWER = "INVALID_ANSWER"
    REPO_NOT_FOUND = "REPO_NOT_FOUND"
    CONFIG_ERROR = "CONFIG_ERROR"


# =============================================================================
# SESSION TYPES (internal)
# =============================================================================


@dataclass
class Session:
    """Internal session state."""

    id: str
    repo_path: str
    intention: str
    created_at: float  # Unix timestamp
    expires_at: float  # Unix timestamp (created_at + 30min)

    # Questions asked and answers received
    asked_questions: tuple[Question, ...] = ()
    answers: dict[str, str | tuple[str, ...]] = field(default_factory=dict)

    # Core conversation state tracking
    core_questions_asked: tuple[Question, ...] = ()  # Questions from Core
    all_answers: dict[str, str | tuple[str, ...]] = field(default_factory=dict)

    # Decision patch (extracted by LLM)
    decision_patch_category: str | None = None
    decision_patch_fields: tuple[tuple[str, str], ...] | None = None

    def is_expired(self, current_time: float) -> bool:
        """Check if session has expired."""
        return current_time >= self.expires_at
