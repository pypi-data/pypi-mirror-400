"""Simple file context builder for testing."""

from __future__ import annotations

from pathlib import Path

from preflights.core.types import FileContext


class SimpleFileContextBuilder:
    """
    Simple file context builder.

    Scans repository with basic limits.
    V1: Simplified implementation for testing.
    """

    MAX_FILES = 100
    MAX_DEPTH = 5

    def __init__(
        self,
        fixed_context: FileContext | None = None,
    ) -> None:
        """
        Initialize builder.

        Args:
            fixed_context: If provided, always return this context
                          (for deterministic testing)
        """
        self._fixed_context = fixed_context

    def build(self, repo_path: str) -> FileContext:
        """Build FileContext from repository."""
        if self._fixed_context is not None:
            return self._fixed_context

        root = Path(repo_path)

        if not root.exists():
            return FileContext(paths=(), high_level_dirs=(), signals=())

        paths: list[str] = []
        high_level_dirs: set[str] = set()
        signals: list[tuple[str, str]] = []

        # Collect files with limits
        for path in root.rglob("*"):
            if len(paths) >= self.MAX_FILES:
                break

            # Skip hidden files and common ignored directories
            if any(part.startswith(".") for part in path.parts):
                continue
            if any(part in ("node_modules", "__pycache__", "venv", ".venv", "dist", "build")
                   for part in path.parts):
                continue

            # Check depth
            rel_parts = path.relative_to(root).parts
            if len(rel_parts) > self.MAX_DEPTH:
                continue

            if path.is_file():
                rel_path = str(path.relative_to(root))
                paths.append(rel_path)

                # Collect high-level directory
                if len(rel_parts) >= 2:
                    high_level_dirs.add(f"{rel_parts[0]}/")

        # Detect signals from common files
        signals.extend(self._detect_signals(root))

        return FileContext(
            paths=tuple(sorted(paths)),
            high_level_dirs=tuple(sorted(high_level_dirs)),
            signals=tuple(signals),
        )

    def _detect_signals(self, root: Path) -> list[tuple[str, str]]:
        """Detect technology signals from common files."""
        signals: list[tuple[str, str]] = []

        # Python
        if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
            signals.append(("language", "python"))

        # Node/TypeScript
        if (root / "package.json").exists():
            signals.append(("language", "javascript"))
            if (root / "tsconfig.json").exists():
                signals.append(("language", "typescript"))

        # React
        if (root / "next.config.js").exists() or (root / "next.config.mjs").exists():
            signals.append(("framework", "nextjs"))
        elif (root / "vite.config.ts").exists() or (root / "vite.config.js").exists():
            signals.append(("framework", "vite"))

        # Database indicators
        if (root / "prisma").exists():
            signals.append(("orm", "prisma"))

        return signals

    def set_fixed_context(self, context: FileContext) -> None:
        """Set fixed context for testing."""
        self._fixed_context = context
