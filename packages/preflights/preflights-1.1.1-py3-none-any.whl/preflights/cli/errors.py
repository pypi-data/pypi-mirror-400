"""CLI error types and exit codes."""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """CLI exit codes."""

    SUCCESS = 0
    USER_ERROR = 1  # Bad input, validation failed, no session
    SYSTEM_ERROR = 2  # LLM failure, filesystem error


class CLIError(Exception):
    """Base CLI error with structured output."""

    def __init__(
        self,
        code: str,
        message: str,
        hint: str | None = None,
        exit_code: ExitCode = ExitCode.USER_ERROR,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint
        self.exit_code = exit_code


class NotARepositoryError(CLIError):
    """No git repository found."""

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(
            code="NOT_A_REPOSITORY",
            message=message,
            hint=hint or "Run from repository root, or use --repo-path",
            exit_code=ExitCode.USER_ERROR,
        )


class NoActiveSessionError(CLIError):
    """No active session."""

    def __init__(self) -> None:
        super().__init__(
            code="NO_ACTIVE_SESSION",
            message="No active session",
            hint="Use 'preflights start \"<intention>\"' to begin",
            exit_code=ExitCode.USER_ERROR,
        )


class SessionAlreadyActiveError(CLIError):
    """Session already active."""

    def __init__(self, expires_in_minutes: int) -> None:
        super().__init__(
            code="SESSION_ALREADY_ACTIVE",
            message=f"Session already active (expires in {expires_in_minutes}m)",
            hint="Use 'preflights answer' to continue, or 'preflights reset' to start fresh",
            exit_code=ExitCode.USER_ERROR,
        )


class SessionExpiredError(CLIError):
    """Session expired."""

    def __init__(self) -> None:
        super().__init__(
            code="SESSION_EXPIRED",
            message="Session expired after 30 minutes",
            hint="Use 'preflights resume' to restart with same intention",
            exit_code=ExitCode.USER_ERROR,
        )


class InvalidAnswerError(CLIError):
    """Invalid answer format or value."""

    def __init__(self, question_id: str, message: str, options: tuple[str, ...] | None = None) -> None:
        hint = f"Expected one of: {', '.join(options)}" if options else "Check question options with 'preflights status'"
        super().__init__(
            code="INVALID_ANSWER",
            message=f"Invalid answer for '{question_id}': {message}",
            hint=hint,
            exit_code=ExitCode.USER_ERROR,
        )


class NoPreviousSessionError(CLIError):
    """No previous session to resume."""

    def __init__(self) -> None:
        super().__init__(
            code="NO_PREVIOUS_SESSION",
            message="No previous session to resume",
            hint="Use 'preflights start \"<intention>\"' to begin",
            exit_code=ExitCode.USER_ERROR,
        )
