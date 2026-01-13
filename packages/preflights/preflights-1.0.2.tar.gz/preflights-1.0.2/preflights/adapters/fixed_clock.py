"""Fixed clock provider for testing."""

from __future__ import annotations


class FixedClockProvider:
    """
    Deterministic clock provider for testing.

    Returns fixed time that can be advanced manually.
    """

    def __init__(
        self,
        fixed_unix: float = 1736161200.0,  # 2025-01-06T11:00:00Z
        fixed_iso: str = "2025-01-06T11:00:00Z",
    ) -> None:
        """
        Initialize clock.

        Args:
            fixed_unix: Fixed Unix timestamp
            fixed_iso: Fixed ISO string (should match unix timestamp)
        """
        self._unix = fixed_unix
        self._iso = fixed_iso

    def now_unix(self) -> float:
        """Get current time as Unix timestamp."""
        return self._unix

    def now_utc_iso(self) -> str:
        """Get current time as ISO string."""
        return self._iso

    def advance(self, seconds: float) -> None:
        """Advance time by seconds (for testing)."""
        self._unix += seconds
        # Note: ISO string is not auto-updated (set manually if needed)

    def set_time(self, unix: float, iso: str) -> None:
        """Set specific time (for testing)."""
        self._unix = unix
        self._iso = iso

    def advance_minutes(self, minutes: float) -> None:
        """Advance time by minutes (for testing)."""
        self.advance(minutes * 60)
