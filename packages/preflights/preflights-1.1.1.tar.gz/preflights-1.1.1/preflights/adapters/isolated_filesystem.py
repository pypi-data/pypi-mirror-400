"""Isolated filesystem adapter for use with pytest tmp_path."""

from __future__ import annotations

from pathlib import Path

from preflights.adapters.filesystem import FilesystemAdapter
from preflights.application.ports.filesystem import ParseError
from preflights.core.types import Task


class IsolatedFilesystemAdapter(FilesystemAdapter):
    """
    Isolated filesystem adapter that redirects all operations to a base path.

    Used for testing with pytest's tmp_path fixture.
    Inherits all behavior from FilesystemAdapter but overrides path resolution.
    """

    def __init__(self, base_path: Path | None = None) -> None:
        """
        Initialize isolated adapter.

        Args:
            base_path: If provided, all operations use this as root.
                       Used for testing with tmp_path.
        """
        self._base_path = base_path
        self._malformed_current_task: bool = False

    def _resolve_path(self, repo_path: str, relative: str) -> Path:
        """Resolve path relative to base_path (for test isolation)."""
        if self._base_path is not None:
            return self._base_path / relative
        return Path(repo_path) / relative

    def repo_exists(self, repo_path: str) -> bool:
        """Check if repository exists."""
        if self._base_path is not None:
            return self._base_path.exists()
        return Path(repo_path).exists()

    def read_current_task(self, repo_path: str) -> Task | None:
        """Read CURRENT_TASK.md (with test hook for malformed content)."""
        path = self._resolve_path(repo_path, self.CURRENT_TASK_PATH)

        if not path.exists():
            return None

        content = path.read_text()

        # Test hook: simulate malformed content
        if self._malformed_current_task:
            raise ParseError(
                "CURRENT_TASK.md is malformed: missing UID",
                str(path),
            )

        return self._parse_task_from_markdown(content, path)

    def set_malformed_current_task(self, malformed: bool) -> None:
        """Set flag to simulate malformed CURRENT_TASK.md (for testing)."""
        self._malformed_current_task = malformed
