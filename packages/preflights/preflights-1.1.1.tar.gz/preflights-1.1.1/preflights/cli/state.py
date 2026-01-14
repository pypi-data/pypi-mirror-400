"""Session state management for CLI."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from preflights.cli.errors import NoActiveSessionError, NoPreviousSessionError, SessionExpiredError
from preflights.cli.repo import (
    ensure_preflights_ignored,
    ensure_state_dir,
    get_last_intention_file,
    get_session_file,
)


@dataclass
class StoredQuestion:
    """Question stored in session state."""

    id: str
    type: str
    question: str
    options: tuple[str, ...] | None = None
    min_selections: int | None = None
    max_selections: int | None = None
    optional: bool = False
    depends_on_question_id: str | None = None
    depends_on_value: str | None = None


@dataclass
class SessionState:
    """CLI session state stored in .preflights/current_session.json."""

    session_id: str
    intention: str
    started_at: str  # ISO format
    expires_at: str  # ISO format
    expires_at_unix: float
    questions: list[StoredQuestion] = field(default_factory=list)
    answers: dict[str, str | list[str]] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return time.time() >= self.expires_at_unix

    def get_expires_in_minutes(self) -> int:
        """Get minutes until expiration."""
        remaining = self.expires_at_unix - time.time()
        return max(0, int(remaining / 60))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "session_id": self.session_id,
            "intention": self.intention,
            "started_at": self.started_at,
            "expires_at": self.expires_at,
            "expires_at_unix": self.expires_at_unix,
            "questions": [
                {
                    "id": q.id,
                    "type": q.type,
                    "question": q.question,
                    "options": list(q.options) if q.options else None,
                    "min_selections": q.min_selections,
                    "max_selections": q.max_selections,
                    "optional": q.optional,
                    "depends_on_question_id": q.depends_on_question_id,
                    "depends_on_value": q.depends_on_value,
                }
                for q in self.questions
            ],
            "answers": self.answers,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionState":
        """Create from dict (JSON deserialization)."""
        questions = [
            StoredQuestion(
                id=q["id"],
                type=q["type"],
                question=q["question"],
                options=tuple(q["options"]) if q.get("options") else None,
                min_selections=q.get("min_selections"),
                max_selections=q.get("max_selections"),
                optional=q.get("optional", False),
                depends_on_question_id=q.get("depends_on_question_id"),
                depends_on_value=q.get("depends_on_value"),
            )
            for q in data.get("questions", [])
        ]
        return cls(
            session_id=data["session_id"],
            intention=data["intention"],
            started_at=data["started_at"],
            expires_at=data["expires_at"],
            expires_at_unix=data["expires_at_unix"],
            questions=questions,
            answers=data.get("answers", {}),
        )


def load_session(repo_root: str) -> SessionState:
    """
    Load session from .preflights/current_session.json.

    Raises:
        NoActiveSessionError: If no session file exists
        SessionExpiredError: If session has expired
    """
    session_file = get_session_file(repo_root)

    if not session_file.exists():
        raise NoActiveSessionError()

    with open(session_file) as f:
        data = json.load(f)

    state = SessionState.from_dict(data)

    if state.is_expired():
        # Delete expired session
        session_file.unlink()
        raise SessionExpiredError()

    return state


def save_session(repo_root: str, state: SessionState) -> None:
    """Save session to .preflights/current_session.json."""
    ensure_state_dir(repo_root)
    ensure_preflights_ignored(repo_root)

    session_file = get_session_file(repo_root)
    with open(session_file, "w") as f:
        json.dump(state.to_dict(), f, indent=2)


def delete_session(repo_root: str) -> None:
    """Delete current session file."""
    session_file = get_session_file(repo_root)
    if session_file.exists():
        session_file.unlink()


def session_exists(repo_root: str) -> bool:
    """Check if session file exists (may be expired)."""
    return get_session_file(repo_root).exists()


def save_last_intention(repo_root: str, intention: str) -> None:
    """Save last intention to .preflights/last_intention.txt."""
    ensure_state_dir(repo_root)
    intention_file = get_last_intention_file(repo_root)
    intention_file.write_text(intention)


def load_last_intention(repo_root: str) -> str:
    """
    Load last intention from .preflights/last_intention.txt.

    Raises:
        NoPreviousSessionError: If no last intention file exists
    """
    intention_file = get_last_intention_file(repo_root)

    if not intention_file.exists():
        raise NoPreviousSessionError()

    return intention_file.read_text().strip()


def update_session_questions(repo_root: str, questions: list[StoredQuestion]) -> None:
    """Update session with new questions (from follow-up)."""
    state = load_session(repo_root)
    # Add new questions (don't replace, accumulate)
    existing_ids = {q.id for q in state.questions}
    for q in questions:
        if q.id not in existing_ids:
            state.questions.append(q)
    save_session(repo_root, state)


def update_session_answers(repo_root: str, answers: dict[str, str | list[str]]) -> None:
    """Update session with new answers."""
    state = load_session(repo_root)
    state.answers.update(answers)
    save_session(repo_root, state)
