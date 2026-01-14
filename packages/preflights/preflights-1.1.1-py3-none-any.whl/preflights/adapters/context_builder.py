"""
Context Builder with Redaction.

Builds filtered and redacted context for LLM interactions.
Never sends raw workspace data, secrets, or PII.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from preflights.application.types import LLMContext

if TYPE_CHECKING:
    from preflights.core.types import FileContext

# =============================================================================
# REDACTION PATTERNS
# =============================================================================

REDACTION_PATTERNS: list[tuple[str, str]] = [
    # Anthropic API keys
    (r"sk-ant-[A-Za-z0-9\-_]{90,}", "[REDACTED_ANTHROPIC_KEY]"),
    # OpenAI API keys
    (r"sk-[A-Za-z0-9]{48,}", "[REDACTED_OPENAI_KEY]"),
    # Generic long tokens/keys (32+ chars)
    (r"(?<![A-Za-z0-9])[A-Za-z0-9_\-]{40,}(?![A-Za-z0-9])", "[REDACTED_TOKEN]"),
    # JWT tokens
    (
        r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "[REDACTED_JWT]",
    ),
    # Email addresses
    (
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "[REDACTED_EMAIL]",
    ),
    # AWS access keys
    (r"AKIA[0-9A-Z]{16}", "[REDACTED_AWS_KEY]"),
    # AWS secret keys
    (r"(?<![A-Za-z0-9])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9])", "[REDACTED_AWS_SECRET]"),
    # Generic secrets in key=value format
    (
        r'(?i)(password|secret|token|api_key|apikey|auth)\s*[:=]\s*["\'][^"\']+["\']',
        r"\1=[REDACTED]",
    ),
    # Bearer tokens
    (r"Bearer\s+[A-Za-z0-9\-_\.]+", "Bearer [REDACTED]"),
]

# =============================================================================
# FILE EXCLUSION PATTERNS
# =============================================================================

EXCLUDED_FILE_PATTERNS: list[str] = [
    # Environment files
    r"\.env.*",
    r"\.envrc",
    # Key and certificate files
    r".*\.pem$",
    r".*\.key$",
    r".*\.crt$",
    r".*\.p12$",
    r".*\.pfx$",
    # Credentials files
    r"credentials\.json",
    r"credentials\.yaml",
    r"credentials\.yml",
    r"secrets\.json",
    r"secrets\.yaml",
    r"secrets\.yml",
    r"\.secrets",
    # Log files
    r".*\.log$",
    r".*\.log\.\d+$",
    # Dump and export files
    r".*\.dump$",
    r".*\.sql$",
    r".*\.csv$",
    # System and IDE directories
    r"node_modules/.*",
    r"\.git/.*",
    r"__pycache__/.*",
    r"\.venv/.*",
    r"venv/.*",
    r"\.idea/.*",
    r"\.vscode/.*",
    # Build artifacts
    r"dist/.*",
    r"build/.*",
    r"\.next/.*",
    r"target/.*",
]


class ContextBuilder:
    """Builds filtered and redacted context for LLM."""

    def __init__(
        self,
        additional_redaction_patterns: list[tuple[str, str]] | None = None,
        additional_exclusion_patterns: list[str] | None = None,
    ) -> None:
        """
        Initialize context builder.

        Args:
            additional_redaction_patterns: Extra patterns to redact
            additional_exclusion_patterns: Extra file patterns to exclude
        """
        self._redaction_patterns = REDACTION_PATTERNS.copy()
        if additional_redaction_patterns:
            self._redaction_patterns.extend(additional_redaction_patterns)

        self._exclusion_patterns = EXCLUDED_FILE_PATTERNS.copy()
        if additional_exclusion_patterns:
            self._exclusion_patterns.extend(additional_exclusion_patterns)

        # Compile patterns for performance
        self._compiled_exclusions = [
            re.compile(p) for p in self._exclusion_patterns
        ]

    def build(
        self,
        file_context: "FileContext",
        architecture_summary: str | None = None,
    ) -> LLMContext:
        """
        Build redacted context from file context.

        Args:
            file_context: Repository file context
            architecture_summary: Optional existing architecture summary

        Returns:
            Filtered and redacted LLMContext
        """
        # Filter paths
        filtered_paths = self._filter_paths(file_context.paths)

        # Build high-level summary (not raw paths)
        file_summary = self._build_file_summary(filtered_paths)

        # Redact architecture summary if provided
        redacted_summary = None
        if architecture_summary:
            redacted_summary = self.redact_text(architecture_summary)

        return LLMContext(
            file_summary=file_summary,
            technology_signals=file_context.signals,
            architecture_summary=redacted_summary,
        )

    def _filter_paths(self, paths: tuple[str, ...]) -> tuple[str, ...]:
        """Filter out sensitive paths."""
        result: list[str] = []
        for path in paths:
            if not self._should_exclude(path):
                result.append(path)
        return tuple(result)

    def _should_exclude(self, path: str) -> bool:
        """Check if path should be excluded."""
        for pattern in self._compiled_exclusions:
            if pattern.match(path) or pattern.search(path):
                return True
        return False

    def _build_file_summary(self, paths: tuple[str, ...]) -> str:
        """Build high-level summary instead of raw paths."""
        if not paths:
            return "Repository structure: (empty or all files excluded)"

        # Group by top-level directory
        dirs: dict[str, int] = {}
        extensions: dict[str, int] = {}

        for path in paths:
            # Count directories
            parts = path.split("/")
            top_dir = parts[0] if len(parts) > 1 else "(root)"
            dirs[top_dir] = dirs.get(top_dir, 0) + 1

            # Count extensions
            if "." in path:
                ext = path.rsplit(".", 1)[-1].lower()
                extensions[ext] = extensions.get(ext, 0) + 1

        # Build summary
        lines = ["Repository structure:"]

        # Top directories (sorted by count, max 10)
        sorted_dirs = sorted(dirs.items(), key=lambda x: -x[1])[:10]
        for dir_name, count in sorted_dirs:
            if dir_name == "(root)":
                lines.append(f"  {count} files in root")
            else:
                lines.append(f"  {dir_name}/ ({count} files)")

        if len(dirs) > 10:
            remaining = sum(c for _, c in sorted_dirs[10:])
            lines.append(f"  ... and {len(dirs) - 10} more directories ({remaining} files)")

        # Main technologies (from extensions)
        if extensions:
            lines.append("\nMain file types:")
            sorted_exts = sorted(extensions.items(), key=lambda x: -x[1])[:5]
            for ext, count in sorted_exts:
                lines.append(f"  .{ext}: {count} files")

        return "\n".join(lines)

    def redact_text(self, text: str) -> str:
        """Apply redaction patterns to text."""
        result = text
        for pattern, replacement in self._redaction_patterns:
            try:
                result = re.sub(pattern, replacement, result)
            except re.error:
                # Skip invalid patterns
                continue
        return result
