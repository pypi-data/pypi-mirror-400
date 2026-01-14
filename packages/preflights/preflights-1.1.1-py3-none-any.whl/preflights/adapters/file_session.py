"""File-based session adapter for CLI persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from preflights.application.ports.session import (
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from preflights.application.types import Question, Session


class FileSessionAdapter:
    """
    File-based session storage.

    Persists sessions to JSON files in a global directory (~/.preflights/sessions/).
    Supports multi-process CLI usage where each command is a separate process.

    Sessions are stored globally (not per-repo) to avoid cwd() issues.
    Each session contains repo_path for context.
    """

    def __init__(self, sessions_dir: Path | None = None) -> None:
        """
        Initialize file session adapter.

        Args:
            sessions_dir: Directory for session files.
                         If None, uses ~/.preflights/sessions/ (user home).
        """
        if sessions_dir is None:
            sessions_dir = Path.home() / ".preflights" / "sessions"
        self._sessions_dir = sessions_dir

    def _get_session_path(self, session_id: str) -> Path:
        """Get path for a session file."""
        # Sanitize session_id for filesystem
        safe_id = session_id.replace("/", "_").replace("\\", "_")
        return self._sessions_dir / f"{safe_id}.json"

    def _serialize_session(self, session: Session) -> dict[str, Any]:
        """Serialize Session to JSON-compatible dict."""
        return {
            "id": session.id,
            "repo_path": session.repo_path,
            "intention": session.intention,
            "created_at": session.created_at,
            "expires_at": session.expires_at,
            "asked_questions": [
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
                for q in session.asked_questions
            ],
            "answers": {
                k: list(v) if isinstance(v, tuple) else v
                for k, v in session.answers.items()
            },
            "core_questions_asked": [
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
                for q in session.core_questions_asked
            ],
            "all_answers": {
                k: list(v) if isinstance(v, tuple) else v
                for k, v in session.all_answers.items()
            },
            "decision_patch_category": session.decision_patch_category,
            "decision_patch_fields": (
                [list(f) for f in session.decision_patch_fields]
                if session.decision_patch_fields
                else None
            ),
            "missing_info": list(session.missing_info),
            "decision_hint": session.decision_hint,
            "llm_provider_used": session.llm_provider_used,
            "llm_fallback_occurred": session.llm_fallback_occurred,
        }

    def _deserialize_session(self, data: dict[str, Any]) -> Session:
        """Deserialize Session from JSON dict."""
        return Session(
            id=data["id"],
            repo_path=data["repo_path"],
            intention=data["intention"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            asked_questions=tuple(
                Question(
                    id=q["id"],
                    type=q["type"],
                    question=q["question"],
                    options=tuple(q["options"]) if q["options"] else None,
                    min_selections=q.get("min_selections"),
                    max_selections=q.get("max_selections"),
                    optional=q.get("optional", False),
                    depends_on_question_id=q.get("depends_on_question_id"),
                    depends_on_value=q.get("depends_on_value"),
                )
                for q in data.get("asked_questions", [])
            ),
            answers={
                k: tuple(v) if isinstance(v, list) else v
                for k, v in data.get("answers", {}).items()
            },
            core_questions_asked=tuple(
                Question(
                    id=q["id"],
                    type=q["type"],
                    question=q["question"],
                    options=tuple(q["options"]) if q["options"] else None,
                    min_selections=q.get("min_selections"),
                    max_selections=q.get("max_selections"),
                    optional=q.get("optional", False),
                    depends_on_question_id=q.get("depends_on_question_id"),
                    depends_on_value=q.get("depends_on_value"),
                )
                for q in data.get("core_questions_asked", [])
            ),
            all_answers={
                k: tuple(v) if isinstance(v, list) else v
                for k, v in data.get("all_answers", {}).items()
            },
            decision_patch_category=data.get("decision_patch_category"),
            decision_patch_fields=(
                tuple(tuple(f) for f in data["decision_patch_fields"])
                if data.get("decision_patch_fields")
                else None
            ),
            missing_info=tuple(data.get("missing_info", [])),
            decision_hint=data.get("decision_hint"),
            llm_provider_used=data.get("llm_provider_used"),
            llm_fallback_occurred=data.get("llm_fallback_occurred", False),
        )

    def create(self, session: Session) -> None:
        """Store a new session to file."""
        path = self._get_session_path(session.id)
        if path.exists():
            raise SessionAlreadyExistsError(f"Session {session.id} already exists")

        self._sessions_dir.mkdir(parents=True, exist_ok=True)
        data = self._serialize_session(session)
        path.write_text(json.dumps(data, indent=2))

    def get(self, session_id: str) -> Session | None:
        """Retrieve a session from file."""
        path = self._get_session_path(session_id)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text())
            return self._deserialize_session(data)
        except (json.JSONDecodeError, KeyError):
            # Corrupted session file - treat as non-existent
            return None

    def update(self, session: Session) -> None:
        """Update an existing session file."""
        path = self._get_session_path(session.id)
        if not path.exists():
            raise SessionNotFoundError(f"Session {session.id} not found")

        data = self._serialize_session(session)
        path.write_text(json.dumps(data, indent=2))

    def delete(self, session_id: str) -> None:
        """Delete a session file (idempotent)."""
        path = self._get_session_path(session_id)
        if path.exists():
            path.unlink()

    def cleanup_expired(self, current_time: float) -> int:
        """Remove expired session files."""
        if not self._sessions_dir.exists():
            return 0

        removed = 0
        for path in self._sessions_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                if data.get("expires_at", 0) < current_time:
                    path.unlink()
                    removed += 1
            except (json.JSONDecodeError, KeyError):
                # Corrupted file - remove it
                path.unlink()
                removed += 1

        return removed

    def clear(self) -> None:
        """Clear all sessions (for testing)."""
        if self._sessions_dir.exists():
            for path in self._sessions_dir.glob("*.json"):
                path.unlink()

    def count(self) -> int:
        """Get number of sessions (for testing)."""
        if not self._sessions_dir.exists():
            return 0
        return len(list(self._sessions_dir.glob("*.json")))
