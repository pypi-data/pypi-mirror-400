"""In-memory session adapter."""

from __future__ import annotations

from preflights.application.ports.session import (
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from preflights.application.types import Session

# Re-export for backward compatibility
__all__ = [
    "InMemorySessionAdapter",
    "SessionAlreadyExistsError",
    "SessionNotFoundError",
]


class InMemorySessionAdapter:
    """
    In-memory session storage with TTL support.

    Sessions expire after TTL_SECONDS (30 minutes by default).
    """

    TTL_SECONDS: float = 30 * 60  # 30 minutes

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, session: Session) -> None:
        """Store a new session."""
        if session.id in self._sessions:
            raise SessionAlreadyExistsError(f"Session {session.id} already exists")
        self._sessions[session.id] = session

    def get(self, session_id: str) -> Session | None:
        """
        Retrieve a session by ID.

        Returns None if:
        - Session doesn't exist
        - Session has expired (lazy cleanup)
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None

        # Don't check expiry here - let caller handle with current time
        return session

    def update(self, session: Session) -> None:
        """Update an existing session."""
        if session.id not in self._sessions:
            raise SessionNotFoundError(f"Session {session.id} not found")
        self._sessions[session.id] = session

    def delete(self, session_id: str) -> None:
        """Delete a session (idempotent)."""
        self._sessions.pop(session_id, None)

    def cleanup_expired(self, current_time: float) -> int:
        """Remove expired sessions."""
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if session.is_expired(current_time)
        ]
        for sid in expired_ids:
            del self._sessions[sid]
        return len(expired_ids)

    def clear(self) -> None:
        """Clear all sessions (for testing)."""
        self._sessions.clear()

    def count(self) -> int:
        """Get number of sessions (for testing)."""
        return len(self._sessions)
