"""File context builder port."""

from __future__ import annotations

from typing import Protocol

from preflights.core.types import FileContext


class FileContextBuilderPort(Protocol):
    """
    Port for building FileContext from repository.

    Scans repository to extract:
    - File paths
    - High-level directory structure
    - Technology signals (package.json, requirements.txt, etc.)

    V1: Simple scanner with basic limits.
    Future: Optimized with caching, gitignore support, etc.
    """

    def build(self, repo_path: str) -> FileContext:
        """
        Build FileContext from repository.

        Args:
            repo_path: Repository root path

        Returns:
            FileContext with paths, dirs, and signals

        Note: May apply limits (max depth, max files) to prevent
              performance issues on large repos.
        """
        ...
