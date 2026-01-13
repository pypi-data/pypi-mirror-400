"""Sequential UID provider for testing."""

from __future__ import annotations


class SequentialUIDProvider:
    """
    Deterministic UID provider for testing.

    Generates sequential UIDs starting from a fixed timestamp.
    """

    def __init__(
        self,
        start_timestamp: str = "20250106T120000",
        start_ms: int = 0,
        suffix_start: int = 0xA000,
    ) -> None:
        """
        Initialize provider.

        Args:
            start_timestamp: Base timestamp (YYYYMMDDTHHMMSS)
            start_ms: Starting millisecond value
            suffix_start: Starting suffix value (hex)
        """
        self._timestamp = start_timestamp
        self._ms = start_ms
        self._suffix = suffix_start
        self._session_counter = 0

    def generate(self) -> str:
        """Generate next UID."""
        uid = f"{self._timestamp}.{self._ms:03d}Z-{self._suffix:04X}"
        self._increment()
        return uid

    def _increment(self) -> None:
        """Increment counters."""
        self._ms += 1
        if self._ms >= 1000:
            self._ms = 0
            self._suffix += 1

    def generate_session_id(self) -> str:
        """Generate session ID."""
        self._session_counter += 1
        return f"session-{self._session_counter:04d}"

    def reset(self) -> None:
        """Reset counters (for testing)."""
        self._ms = 0
        self._suffix = 0xA000
        self._session_counter = 0

    def peek_next_uid(self) -> str:
        """Preview next UID without incrementing (for testing)."""
        return f"{self._timestamp}.{self._ms:03d}Z-{self._suffix:04X}"
