"""
Preflights Application Types.

Public types for the PreflightsApp contract.
These types are FROZEN for V1 (see PREFLIGHTS_APP_CONTRACT.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass


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
# LLM TYPES
# =============================================================================


@dataclass(frozen=True)
class LLMResponse:
    """Structured response from LLM.

    Contains questions and semantic tracking fields for cross-session state.
    """

    questions: tuple[Question, ...]
    missing_info: tuple[str, ...]  # Semantic keys (1:1 with questions)
    decision_hint: Literal["task", "adr", "unsure"]
    progress: float  # 0.0 to 1.0


@dataclass(frozen=True)
class LLMContext:
    """Filtered and redacted context sent to LLM.

    Never contains raw workspace data, secrets, or PII.
    """

    file_summary: str  # High-level file structure (not raw paths)
    technology_signals: tuple[tuple[str, str], ...]  # (signal_type, value)
    architecture_summary: str | None  # Existing decisions summary


@dataclass(frozen=True)
class SessionSnapshot:
    """Minimal session state for LLM context.

    Used to provide session history to LLM for cross-session tracking.
    """

    intention: str
    asked_questions: tuple[str, ...]  # Question IDs already asked
    answered_questions: tuple[str, ...]  # Question IDs answered
    missing_info: tuple[str, ...]  # Semantic keys still needed


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

    # LLM-specific error codes
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_INVALID_RESPONSE = "LLM_INVALID_RESPONSE"
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    LLM_CREDENTIALS_MISSING = "LLM_CREDENTIALS_MISSING"
    LLM_RATE_LIMITED = "LLM_RATE_LIMITED"


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

    # LLM semantic tracking
    missing_info: tuple[str, ...] = ()  # Semantic keys from LLM
    decision_hint: str | None = None  # "task" | "adr" | "unsure" (informative only)
    llm_provider_used: str | None = None  # Track which provider was used
    llm_fallback_occurred: bool = False  # Track if fallback happened

    def is_expired(self, current_time: float) -> bool:
        """Check if session has expired."""
        return current_time >= self.expires_at
