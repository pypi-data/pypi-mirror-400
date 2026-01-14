"""
MCP-specific types for Preflights.

These types define the MCP tool inputs and outputs as per MCP_SPEC.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


# =============================================================================
# INPUT TYPES
# =============================================================================


@dataclass(frozen=True)
class RequireClarificationInput:
    """Input for require_clarification tool."""

    user_intention: str
    optional_context: str | None = None
    session_id: str | None = None
    answers: dict[str, Any] | None = None
    preferences: dict[str, Any] | None = None


@dataclass(frozen=True)
class ReadArchitectureInput:
    """Input for read_architecture tool (empty)."""

    pass


# =============================================================================
# OUTPUT TYPES - Questions
# =============================================================================


@dataclass(frozen=True)
class MCPQuestion:
    """Question in MCP format."""

    id: str
    type: Literal["single_choice", "multi_choice", "free_text"]
    question: str
    options: list[str] | None = None
    min_selections: int | None = None
    max_selections: int | None = None
    optional: bool = False


@dataclass(frozen=True)
class MCPProgress:
    """Progress tracking for clarification."""

    asked_so_far: int
    answered: int


# =============================================================================
# OUTPUT TYPES - Artifacts
# =============================================================================


@dataclass(frozen=True)
class MCPArtifact:
    """Created artifact info."""

    path: str
    type: Literal["adr", "task", "projection"]
    uid: str | None = None  # Only for ADR


# =============================================================================
# OUTPUT TYPES - Error
# =============================================================================


@dataclass(frozen=True)
class MCPError:
    """Error details."""

    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    recovery_hint: str | None = None


# =============================================================================
# OUTPUT TYPES - Results
# =============================================================================


@dataclass
class NeedsClarificationResult:
    """Result when clarification is needed."""

    status: Literal["needs_clarification"] = "needs_clarification"
    session_id: str = ""
    questions: list[MCPQuestion] = field(default_factory=list)
    progress: MCPProgress | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        result: dict[str, Any] = {
            "status": self.status,
            "session_id": self.session_id,
            "questions": [
                {
                    "id": q.id,
                    "type": q.type,
                    "question": q.question,
                    **({"options": q.options} if q.options else {}),
                    **({"min_selections": q.min_selections} if q.min_selections else {}),
                    **({"max_selections": q.max_selections} if q.max_selections else {}),
                    **({"optional": q.optional} if q.optional else {}),
                }
                for q in self.questions
            ],
        }
        if self.progress:
            result["progress"] = {
                "asked_so_far": self.progress.asked_so_far,
                "answered": self.progress.answered,
            }
        return result


@dataclass
class CompletedResult:
    """Result when clarification is complete."""

    status: Literal["completed"] = "completed"
    artifacts_created: list[MCPArtifact] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "status": self.status,
            "artifacts_created": [
                {
                    "path": a.path,
                    "type": a.type,
                    **({"uid": a.uid} if a.uid else {}),
                }
                for a in self.artifacts_created
            ],
            "summary": self.summary,
        }


@dataclass
class ErrorResult:
    """Result when an error occurs."""

    status: Literal["error"] = "error"
    error: MCPError | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        result: dict[str, Any] = {"status": self.status}
        if self.error:
            result["error"] = {
                "code": self.error.code,
                "message": self.error.message,
                **({"details": self.error.details} if self.error.details else {}),
                **({"recovery_hint": self.error.recovery_hint} if self.error.recovery_hint else {}),
            }
        return result


@dataclass
class ArchitectureResult:
    """Result for read_architecture."""

    status: Literal["success"] = "success"
    architecture: dict[str, Any] = field(default_factory=dict)
    source_file: str = "docs/ARCHITECTURE_STATE.md"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "status": self.status,
            "architecture": self.architecture,
            "source_file": self.source_file,
        }


# Union type for tool results
RequireClarificationResult = NeedsClarificationResult | CompletedResult | ErrorResult
