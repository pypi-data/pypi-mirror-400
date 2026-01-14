"""Session storage port."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from preflights.application.types import Session


class SessionNotFoundError(Exception):
    """Session not found."""

    pass


class SessionAlreadyExistsError(Exception):
    """Session already exists."""

    pass


class SessionPort(Protocol):
    """
    Port for session storage.

    V1: In-memory with 30-minute TTL.
    Future: Could be Redis, SQLite, etc.
    """

    def create(self, session: Session) -> None:
        """
        Store a new session.

        Args:
            session: Session to store

        Raises:
            SessionAlreadyExistsError: If session_id already exists
        """
        ...

    def get(self, session_id: str) -> Session | None:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session if found and not expired, None otherwise
        """
        ...

    def update(self, session: Session) -> None:
        """
        Update an existing session.

        Args:
            session: Session with updated data

        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        ...

    def delete(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session to delete

        Note: No error if session doesn't exist (idempotent).
        """
        ...

    def cleanup_expired(self, current_time: float) -> int:
        """
        Remove expired sessions.

        Args:
            current_time: Current Unix timestamp

        Returns:
            Number of sessions removed
        """
        ...
