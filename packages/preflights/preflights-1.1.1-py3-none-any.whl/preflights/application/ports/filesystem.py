"""Filesystem adapter port."""

from __future__ import annotations

from typing import Protocol

from preflights.core.types import ADR, ArchitectureState, Task


class FilesystemError(Exception):
    """Base class for filesystem errors."""

    def __init__(self, message: str, path: str | None = None) -> None:
        super().__init__(message)
        self.path = path


class ParseError(FilesystemError):
    """File exists but content is malformed."""

    pass


class FileExistsError(FilesystemError):
    """File already exists (for immutable writes)."""

    pass


class FilesystemPort(Protocol):
    """
    Port for filesystem operations.

    Responsible for:
    - Reading/writing ADRs
    - Reading/writing CURRENT_TASK.md
    - Archiving tasks
    - Reading/writing ARCHITECTURE_STATE.md

    All paths are relative to repo_path.
    """

    def read_current_task(self, repo_path: str) -> Task | None:
        """
        Read CURRENT_TASK.md.

        Args:
            repo_path: Repository root path

        Returns:
            Task if exists and valid, None if doesn't exist

        Raises:
            ParseError: If file exists but is malformed (missing UID, etc.)
        """
        ...

    def write_task(self, repo_path: str, task: Task) -> str:
        """
        Write CURRENT_TASK.md (archives existing first).

        Args:
            repo_path: Repository root path
            task: Task to write

        Returns:
            Relative path to written file (e.g., "docs/CURRENT_TASK.md")

        Raises:
            FilesystemError: If archive or write fails
            ParseError: If existing CURRENT_TASK.md is malformed

        Note: MUST archive existing CURRENT_TASK.md before overwriting.
              Archive uses UID from existing task (not a new UID).
        """
        ...

    def archive_current_task(self, repo_path: str) -> str | None:
        """
        Archive existing CURRENT_TASK.md.

        Args:
            repo_path: Repository root path

        Returns:
            Relative path to archive (e.g., "docs/archive/task/20250106T...md")
            None if no CURRENT_TASK.md exists

        Raises:
            ParseError: If CURRENT_TASK.md exists but is malformed
            FileExistsError: If archive already exists (duplicate UID)
            FilesystemError: If write fails
        """
        ...

    def write_adr(self, repo_path: str, adr: ADR) -> str:
        """
        Write ADR file (immutable - never overwrites).

        Args:
            repo_path: Repository root path
            adr: ADR to write

        Returns:
            Relative path to written file (e.g., "docs/adr/20250106T...md")

        Raises:
            FileExistsError: If ADR file already exists (duplicate UID)
            FilesystemError: If write fails
        """
        ...

    def read_architecture_state(self, repo_path: str) -> ArchitectureState | None:
        """
        Read ARCHITECTURE_STATE.md.

        Args:
            repo_path: Repository root path

        Returns:
            ArchitectureState if exists and valid, None if doesn't exist

        Raises:
            ParseError: If file exists but is malformed
        """
        ...

    def write_architecture_state(
        self, repo_path: str, state: ArchitectureState
    ) -> str:
        """
        Write ARCHITECTURE_STATE.md.

        Args:
            repo_path: Repository root path
            state: Architecture state to write

        Returns:
            Relative path to written file (e.g., "docs/ARCHITECTURE_STATE.md")

        Raises:
            FilesystemError: If write fails
        """
        ...

    def repo_exists(self, repo_path: str) -> bool:
        """
        Check if repository exists.

        Args:
            repo_path: Repository root path

        Returns:
            True if directory exists
        """
        ...

    def write_agent_prompt(self, repo_path: str, content: str) -> str:
        """
        Write AGENT_PROMPT.md (overwrites existing).

        Args:
            repo_path: Repository root path
            content: Prompt content to write

        Returns:
            Relative path to written file (e.g., "docs/AGENT_PROMPT.md")

        Raises:
            FilesystemError: If write fails
        """
        ...
