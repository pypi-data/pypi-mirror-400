"""Clock provider port."""

from __future__ import annotations

from typing import Protocol


class ClockPort(Protocol):
    """
    Port for time operations.

    V1: Fixed clock for testing (deterministic).
    Production: System clock.
    """

    def now_unix(self) -> float:
        """
        Get current time as Unix timestamp.

        Returns:
            Current time in seconds since epoch
        """
        ...

    def now_utc_iso(self) -> str:
        """
        Get current time as ISO 8601 UTC string.

        Returns:
            Time string like "2025-01-06T12:00:00Z"
        """
        ...
