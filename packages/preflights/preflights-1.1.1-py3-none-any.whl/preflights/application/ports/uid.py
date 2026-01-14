"""UID provider port."""

from __future__ import annotations

from typing import Protocol


class UIDProviderPort(Protocol):
    """
    Port for UID generation.

    UIDs follow format: YYYYMMDDTHHMMSS.mmmZ-XXXX
    Where XXXX is a 4-char hex anti-collision suffix.

    V1: Sequential provider for testing (deterministic).
    Production: Timestamp + random suffix.
    """

    def generate(self) -> str:
        """
        Generate a new unique UID.

        Returns:
            UID string in format "YYYYMMDDTHHMMSS.mmmZ-XXXX"

        Note: Each call MUST return a unique UID.
        """
        ...

    def generate_session_id(self) -> str:
        """
        Generate a new session ID.

        Returns:
            Unique session identifier (format is implementation-defined)
        """
        ...
