"""Fake filesystem adapter for testing."""

from __future__ import annotations

import re
from pathlib import Path

from preflights.application.ports.filesystem import FileExistsError, FilesystemError, ParseError
from preflights.core.types import ADR, ArchitectureState, Task


class FakeFilesystemAdapter:
    """
    Fake filesystem adapter that writes to a real directory.

    Used for testing with pytest's tmp_path fixture.
    Respects archive semantics and immutability rules.
    """

    CURRENT_TASK_PATH = "docs/CURRENT_TASK.md"
    ADR_DIR = "docs/adr"
    ARCHIVE_TASK_DIR = "docs/archive/task"
    ARCHITECTURE_STATE_PATH = "docs/ARCHITECTURE_STATE.md"
    AGENT_PROMPT_PATH = "docs/AGENT_PROMPT.md"

    def __init__(self, base_path: Path | None = None) -> None:
        """
        Initialize adapter.

        Args:
            base_path: If provided, all operations use this as root.
                       Used for testing with tmp_path.
        """
        self._base_path = base_path
        self._malformed_current_task: bool = False  # For testing parse errors

    def _resolve_path(self, repo_path: str, relative: str) -> Path:
        """Resolve path relative to repo or base path."""
        if self._base_path is not None:
            return self._base_path / relative
        return Path(repo_path) / relative

    def repo_exists(self, repo_path: str) -> bool:
        """Check if repository exists."""
        if self._base_path is not None:
            return self._base_path.exists()
        return Path(repo_path).exists()

    def read_current_task(self, repo_path: str) -> Task | None:
        """Read CURRENT_TASK.md."""
        path = self._resolve_path(repo_path, self.CURRENT_TASK_PATH)

        if not path.exists():
            return None

        content = path.read_text()

        # Check for malformed content (testing hook)
        if self._malformed_current_task:
            raise ParseError(
                "CURRENT_TASK.md is malformed: missing UID",
                str(path),
            )

        # Parse task from markdown
        return self._parse_task_from_markdown(content, path)

    def _parse_task_from_markdown(self, content: str, path: Path) -> Task:
        """Parse Task from markdown content."""
        # Extract UID from header comment
        uid_match = re.search(r"<!-- UID: (\S+) -->", content)
        if not uid_match:
            raise ParseError(
                f"CURRENT_TASK.md missing UID comment: {path}",
                str(path),
            )
        uid = uid_match.group(1)

        # Extract title from first # heading
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled"

        # Extract other fields (simplified parsing)
        objective_match = re.search(r"## Objective\n\n(.+?)(?=\n\n##|\Z)", content, re.DOTALL)
        objective = objective_match.group(1).strip() if objective_match else ""

        context_match = re.search(r"## Context\n\n(.+?)(?=\n\n##|\Z)", content, re.DOTALL)
        context = context_match.group(1).strip() if context_match else ""

        # Extract created_at
        created_match = re.search(r"<!-- Created: (.+?) -->", content)
        created_at = created_match.group(1) if created_match else "1970-01-01T00:00:00Z"

        # Extract ADR reference
        adr_match = re.search(r"<!-- Related ADR: (\S+) -->", content)
        related_adr_uid = adr_match.group(1) if adr_match else None

        return Task(
            uid=uid,
            title=title,
            objective=objective,
            context=context,
            allowlist=(".",),  # Simplified
            forbidden=(),
            technical_constraints=(),
            acceptance_criteria=("Task completed",),
            created_at_utc=created_at,
            related_adr_uid=related_adr_uid,
        )

    def write_task(self, repo_path: str, task: Task) -> str:
        """Write CURRENT_TASK.md (archives existing first)."""
        # Archive existing task first
        self.archive_current_task(repo_path)

        # Write new task
        path = self._resolve_path(repo_path, self.CURRENT_TASK_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)

        content = self._render_task_markdown(task)
        path.write_text(content)

        return self.CURRENT_TASK_PATH

    def _render_task_markdown(self, task: Task) -> str:
        """Render Task as markdown."""
        adr_comment = f"\n<!-- Related ADR: {task.related_adr_uid} -->" if task.related_adr_uid else ""

        return f"""<!-- UID: {task.uid} -->
<!-- Created: {task.created_at_utc} -->{adr_comment}

# {task.title}

## Objective

{task.objective}

## Context

{task.context}

## Allowlist

{chr(10).join(f"- `{p}`" for p in task.allowlist)}

## Forbidden

{chr(10).join(f"- `{p}`" for p in task.forbidden) if task.forbidden else "_None_"}

## Technical Constraints

{chr(10).join(f"- {c}" for c in task.technical_constraints) if task.technical_constraints else "_None_"}

## Acceptance Criteria

{chr(10).join(f"- [ ] {c}" for c in task.acceptance_criteria)}
"""

    def archive_current_task(self, repo_path: str) -> str | None:
        """Archive existing CURRENT_TASK.md."""
        path = self._resolve_path(repo_path, self.CURRENT_TASK_PATH)

        if not path.exists():
            return None

        # Read existing task
        task = self.read_current_task(repo_path)
        if task is None:
            return None

        # Use existing UID for archive (NOT a new UID)
        slug = self._slugify(task.title)
        archive_filename = f"{task.uid}_{slug}.md"
        archive_path = self._resolve_path(repo_path, f"{self.ARCHIVE_TASK_DIR}/{archive_filename}")

        # Check archive doesn't already exist
        if archive_path.exists():
            raise FileExistsError(
                f"Archive already exists: {archive_path}",
                str(archive_path),
            )

        # Create archive directory and write
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(path.read_text())

        # Delete current task
        path.unlink()

        return f"{self.ARCHIVE_TASK_DIR}/{archive_filename}"

    def write_adr(self, repo_path: str, adr: ADR) -> str:
        """Write ADR file (immutable - never overwrites)."""
        slug = self._slugify(adr.title)
        filename = f"{adr.uid}_{slug}.md"
        relative_path = f"{self.ADR_DIR}/{filename}"
        path = self._resolve_path(repo_path, relative_path)

        # ADRs are immutable - never overwrite
        if path.exists():
            raise FileExistsError(
                f"ADR already exists: {path}",
                str(path),
            )

        path.parent.mkdir(parents=True, exist_ok=True)

        content = self._render_adr_markdown(adr)
        path.write_text(content)

        return relative_path

    def _render_adr_markdown(self, adr: ADR) -> str:
        """Render ADR as markdown."""
        prev_link = f"[{adr.previous_uid}](../{adr.previous_uid}.md)" if adr.previous_uid else "_None_"

        # Render snapshot categories
        snapshot_lines: list[str] = []
        for cat_name, cat_fields in adr.snapshot.categories:
            snapshot_lines.append(f"### {cat_name}")
            for field_name, field_value in cat_fields:
                snapshot_lines.append(f"- **{field_name}**: {field_value}")
            snapshot_lines.append("")
        snapshot_content = "\n".join(snapshot_lines)

        return f"""<!-- UID: {adr.uid} -->
<!-- Category: {adr.category} -->
<!-- Date: {adr.date_utc} -->
<!-- Previous: {adr.previous_uid or 'None'} -->

# ADR: {adr.title}

**Category:** {adr.category}
**Date:** {adr.date_utc}
**Status:** Accepted
**Previous:** {prev_link}

## Context

{adr.context}

## Decision

{adr.decision}

## Rationale

{adr.rationale}

## Alternatives Considered

{chr(10).join(f"- {alt}" for alt in adr.alternatives)}

## Consequences

### Positive
{chr(10).join(f"- {c}" for c in adr.consequences_positive) if adr.consequences_positive else "_None_"}

### Negative
{chr(10).join(f"- {c}" for c in adr.consequences_negative) if adr.consequences_negative else "_None_"}

### Neutral
{chr(10).join(f"- {c}" for c in adr.consequences_neutral) if adr.consequences_neutral else "_None_"}

## Changes in This Version

{chr(10).join(f"- {c}" for c in adr.changes_in_this_version)}

## Architecture Snapshot

{snapshot_content}
"""

    def read_architecture_state(self, repo_path: str) -> ArchitectureState | None:
        """Read ARCHITECTURE_STATE.md."""
        path = self._resolve_path(repo_path, self.ARCHITECTURE_STATE_PATH)

        if not path.exists():
            return None

        content = path.read_text()
        return self._parse_architecture_state(content, path)

    def _parse_architecture_state(self, content: str, path: Path) -> ArchitectureState:
        """Parse ArchitectureState from markdown."""
        # Extract UID
        uid_match = re.search(r"<!-- UID: (\S+) -->", content)
        if not uid_match:
            raise ParseError(
                f"ARCHITECTURE_STATE.md missing UID: {path}",
                str(path),
            )
        uid = uid_match.group(1)

        # Simplified parsing - extract categories
        categories: list[tuple[str, tuple[tuple[str, str], ...]]] = []

        # Find category sections (### CategoryName)
        cat_pattern = re.compile(r"^### (\w+)\n((?:- \*\*\w+\*\*: .+\n?)+)", re.MULTILINE)
        for cat_match in cat_pattern.finditer(content):
            cat_name = cat_match.group(1)
            fields_text = cat_match.group(2)

            fields: list[tuple[str, str]] = []
            field_pattern = re.compile(r"- \*\*(\w+)\*\*: (.+)")
            for field_match in field_pattern.finditer(fields_text):
                fields.append((field_match.group(1), field_match.group(2).strip()))

            if fields:
                categories.append((cat_name, tuple(fields)))

        return ArchitectureState(
            uid=uid,
            schema_version="v1",
            categories=tuple(categories),
        )

    def write_architecture_state(
        self, repo_path: str, state: ArchitectureState
    ) -> str:
        """Write ARCHITECTURE_STATE.md."""
        path = self._resolve_path(repo_path, self.ARCHITECTURE_STATE_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)

        content = self._render_architecture_state(state)
        path.write_text(content)

        return self.ARCHITECTURE_STATE_PATH

    def _render_architecture_state(self, state: ArchitectureState) -> str:
        """Render ArchitectureState as markdown."""
        # Render categories
        cat_lines: list[str] = []
        for cat_name, cat_fields in state.categories:
            cat_lines.append(f"### {cat_name}")
            for field_name, field_value in cat_fields:
                cat_lines.append(f"- **{field_name}**: {field_value}")
            cat_lines.append("")
        cat_content = "\n".join(cat_lines)

        return f"""<!-- UID: {state.uid} -->
<!-- Schema: {state.schema_version} -->

# Architecture State

Current architecture decisions snapshot.

## Categories

{cat_content}
"""

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        # Lowercase
        slug = text.lower()
        # Replace spaces with underscores
        slug = slug.replace(" ", "_")
        # Remove non-alphanumeric except underscores
        slug = re.sub(r"[^a-z0-9_]", "", slug)
        # Limit length
        slug = slug[:50]
        return slug or "untitled"

    def write_agent_prompt(self, repo_path: str, content: str) -> str:
        """Write AGENT_PROMPT.md (overwrites existing)."""
        path = self._resolve_path(repo_path, self.AGENT_PROMPT_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return self.AGENT_PROMPT_PATH

    def set_malformed_current_task(self, malformed: bool) -> None:
        """Set flag to simulate malformed CURRENT_TASK.md (for testing)."""
        self._malformed_current_task = malformed
