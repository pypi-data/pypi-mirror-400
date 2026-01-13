"""
MCP Tool implementations for Preflights.

Implements the 2 MCP tools:
- require_clarification: Start/continue clarification sessions
- read_architecture: Read current architecture snapshot

These tools wrap PreflightsApp and translate to MCP format.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from preflights.application.preflights_app import PreflightsApp


class RepoNotFoundError(Exception):
    """Raised when no git repository is found."""

    pass


def discover_repo_root(start_path: str | None = None) -> str:
    """
    Discover repository root by climbing up to find .git directory.

    Args:
        start_path: Starting path (defaults to cwd)

    Returns:
        Absolute path to repository root

    Raises:
        RepoNotFoundError: If no .git directory found
    """
    if start_path is None:
        start_path = os.getcwd()

    current = Path(start_path).resolve()

    # Climb up until we find .git or hit root
    while current != current.parent:
        if (current / ".git").exists():
            return str(current)
        current = current.parent

    # Check root as well
    if (current / ".git").exists():
        return str(current)

    raise RepoNotFoundError(
        f"No git repository found from {start_path}. "
        "Initialize a git repository or provide explicit repo_path."
    )


from preflights.application.types import PreflightArtifacts, Question
from preflights.mcp.types import (
    ArchitectureResult,
    CompletedResult,
    ErrorResult,
    MCPArtifact,
    MCPError,
    MCPProgress,
    MCPQuestion,
    NeedsClarificationResult,
    RequireClarificationResult,
)


class MCPTools:
    """
    MCP tool implementations.

    Wraps PreflightsApp for MCP protocol.
    Sessions are stored in-memory per server lifetime.
    """

    def __init__(self, app: PreflightsApp, default_repo_path: str | None = None) -> None:
        """
        Initialize MCP tools.

        Args:
            app: PreflightsApp instance (with all adapters configured)
            default_repo_path: Default repository path (fallback for tool calls)
        """
        self._app = app
        self._default_repo_path = default_repo_path
        # Track session intentions for multi-turn
        self._session_intentions: dict[str, str] = {}
        # Track session repo paths
        self._session_repo_paths: dict[str, str] = {}

    def _resolve_repo_path(self, repo_path: str | None) -> str:
        """
        Resolve repository root path.

        Args:
            repo_path: Explicit repo path (optional)

        Returns:
            Resolved repository root path

        Raises:
            RepoNotFoundError: If no git repository found
        """
        # Priority: explicit > default > cwd
        start_path = repo_path or self._default_repo_path or os.getcwd()
        return discover_repo_root(start_path)

    def require_clarification(
        self,
        user_intention: str,
        optional_context: str | None = None,
        session_id: str | None = None,
        answers: dict[str, Any] | None = None,
        preferences: dict[str, Any] | None = None,
        repo_path: str | None = None,
    ) -> RequireClarificationResult:
        """
        Start or continue clarification.

        Args:
            user_intention: User's intention/request
            optional_context: Additional context
            session_id: Existing session to continue (None to start new)
            answers: Answers to questions (for continue)
            preferences: Preferences like force_adr
            repo_path: Repository path (optional, discovers from .git if not provided)

        Returns:
            NeedsClarificationResult, CompletedResult, or ErrorResult
        """
        try:
            # Resolve repo path
            if session_id is not None and session_id in self._session_repo_paths:
                # Use stored repo path for existing session
                resolved_repo = self._session_repo_paths[session_id]
            else:
                resolved_repo = self._resolve_repo_path(repo_path)

            if session_id is None:
                # Start new session
                return self._start_session(user_intention, optional_context, resolved_repo)
            else:
                # Continue existing session
                return self._continue_session(session_id, answers or {}, resolved_repo)
        except RepoNotFoundError as e:
            return ErrorResult(
                error=MCPError(
                    code="REPO_NOT_FOUND",
                    message=str(e),
                    recovery_hint="Provide repo_path or run from a git repository",
                )
            )
        except Exception as e:
            return ErrorResult(
                error=MCPError(
                    code="INTERNAL_ERROR",
                    message=str(e),
                    recovery_hint="Check server logs and retry",
                )
            )

    def _start_session(
        self,
        user_intention: str,
        optional_context: str | None,
        repo_path: str,
    ) -> RequireClarificationResult:
        """Start a new clarification session."""
        # Build full intention with context
        full_intention = user_intention
        if optional_context:
            full_intention = f"{user_intention}\n\nContext: {optional_context}"

        # Call PreflightsApp
        result = self._app.start_preflight(full_intention, repo_path)

        # Store intention and repo path for this session
        self._session_intentions[result.session_id] = user_intention
        self._session_repo_paths[result.session_id] = repo_path

        # Convert to MCP format
        questions = self._convert_questions(result.questions)

        return NeedsClarificationResult(
            session_id=result.session_id,
            questions=questions,
            progress=MCPProgress(
                asked_so_far=len(questions),
                answered=0,
            ),
        )

    def _continue_session(
        self,
        session_id: str,
        answers: dict[str, Any],
        repo_path: str,
    ) -> RequireClarificationResult:
        """Continue an existing session with answers."""
        # Convert answers to proper format
        answers_converted: dict[str, str | list[str]] = {}
        for key, value in answers.items():
            if isinstance(value, list):
                answers_converted[key] = value
            else:
                answers_converted[key] = str(value)

        # Call PreflightsApp
        result = self._app.continue_preflight(session_id, answers_converted)

        # Handle different statuses
        if result.status == "error":
            error = result.error
            return ErrorResult(
                error=MCPError(
                    code=error.code if error else "UNKNOWN_ERROR",
                    message=error.message if error else "Unknown error",
                    details=dict(error.details) if error and error.details else {},
                    recovery_hint=error.recovery_hint if error else None,
                )
            )

        if result.status == "needs_more_answers":
            questions = self._convert_questions(result.questions or ())
            answered_count = len(answers)
            return NeedsClarificationResult(
                session_id=session_id,
                questions=questions,
                progress=MCPProgress(
                    asked_so_far=len(questions) + answered_count,
                    answered=answered_count,
                ),
            )

        if result.status == "needs_clarification":
            questions = self._convert_questions(result.questions or ())
            answered_count = len(answers)
            return NeedsClarificationResult(
                session_id=session_id,
                questions=questions,
                progress=MCPProgress(
                    asked_so_far=len(questions) + answered_count,
                    answered=answered_count,
                ),
            )

        if result.status == "completed":
            # Clean up session tracking
            intention = self._session_intentions.pop(session_id, "")
            self._session_repo_paths.pop(session_id, None)
            return self._build_completed_result(result.artifacts, intention)

        # Should not reach here
        return ErrorResult(
            error=MCPError(
                code="UNEXPECTED_STATUS",
                message=f"Unexpected status: {result.status}",
            )
        )

    def _build_completed_result(
        self,
        artifacts: PreflightArtifacts | None,
        intention: str,
    ) -> CompletedResult:
        """Build completed result from artifacts."""
        if artifacts is None:
            return CompletedResult(
                artifacts_created=[],
                summary="Clarification completed.",
            )

        created: list[MCPArtifact] = []

        # Task is always created
        created.append(MCPArtifact(path=artifacts.task_path, type="task"))

        # ADR if present
        if artifacts.adr_path:
            # Extract UID from path
            uid = self._extract_uid_from_path(artifacts.adr_path)
            created.append(MCPArtifact(path=artifacts.adr_path, type="adr", uid=uid))

        # Architecture state if present
        if artifacts.architecture_state_path:
            created.append(MCPArtifact(path=artifacts.architecture_state_path, type="projection"))

        # Build summary
        has_adr = artifacts.adr_path is not None
        summary = f"{'Decision documented and ' if has_adr else ''}Task created for: {intention}"

        return CompletedResult(
            artifacts_created=created,
            summary=summary,
        )

    def _extract_uid_from_path(self, path: str) -> str | None:
        """Extract UID from file path."""
        # Pattern: docs/adr/20250106T120000.000Z-A000_slug.md
        match = re.search(r"(\d{8}T\d{6}\.\d{3}Z(?:-[A-Za-z0-9]+)?)", path)
        return match.group(1) if match else None

    def _convert_questions(self, questions: tuple[Question, ...]) -> list[MCPQuestion]:
        """Convert Application questions to MCP format."""
        result: list[MCPQuestion] = []
        for q in questions:
            # Skip conditional questions (handled internally)
            if q.depends_on_question_id is not None:
                continue

            mcp_q = MCPQuestion(
                id=q.id,
                type=q.type,
                question=q.question,
                options=list(q.options) if q.options else None,
                min_selections=q.min_selections,
                max_selections=q.max_selections,
                optional=q.optional,
            )
            result.append(mcp_q)
        return result

    def read_architecture(
        self, repo_path: str | None = None
    ) -> ArchitectureResult | ErrorResult:
        """
        Read current architecture snapshot.

        Args:
            repo_path: Repository path (optional, discovers from .git if not provided)

        Returns:
            ArchitectureResult with architecture data, or ErrorResult on failure
        """
        try:
            # Resolve repo path
            resolved_repo = self._resolve_repo_path(repo_path)

            # Read architecture state via filesystem adapter
            state = self._app._fs.read_architecture_state(resolved_repo)

            if state is None:
                # No architecture exists yet
                return ArchitectureResult(
                    architecture={"uid": None, "categories": {}},
                    source_file="docs/ARCHITECTURE_STATE.md",
                )

            # Convert to MCP format
            categories: dict[str, dict[str, str]] = {}
            for cat_name, cat_fields in state.categories:
                categories[cat_name] = {}
                for field_name, field_value in cat_fields:
                    # Strip ADR reference if present (e.g., "OAuth (ADR 20250106...)")
                    clean_value = re.sub(r"\s*\(ADR [^)]+\)", "", field_value)
                    categories[cat_name][field_name] = clean_value

            return ArchitectureResult(
                architecture={
                    "uid": state.uid,
                    "categories": categories,
                },
                source_file="docs/ARCHITECTURE_STATE.md",
            )

        except RepoNotFoundError as e:
            return ErrorResult(
                error=MCPError(
                    code="REPO_NOT_FOUND",
                    message=str(e),
                    recovery_hint="Provide repo_path or run from a git repository",
                )
            )
        except Exception as e:
            return ErrorResult(
                error=MCPError(
                    code="FILESYSTEM_ERROR",
                    message=f"Failed to read architecture: {e}",
                    recovery_hint="Check that the repository exists and is accessible",
                )
            )
