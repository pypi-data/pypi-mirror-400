"""Tests for the agent prompt builder."""

from __future__ import annotations

import pytest

from preflights.application.prompt_builder import (
    AGENT_PROMPT_PATH,
    build_agent_prompt,
    extract_prompt_content,
)


class TestBuildAgentPrompt:
    """Tests for build_agent_prompt function."""

    def test_includes_task_path(self) -> None:
        """Prompt includes task path."""
        # When: build_agent_prompt called with task path
        result = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path=None,
            architecture_state_path=None,
        )

        # Then: Task path is included
        assert "docs/CURRENT_TASK.md" in result

    def test_includes_adr_path_when_present(self) -> None:
        """Prompt includes ADR path when provided."""
        # When: build_agent_prompt called with ADR path
        result = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path="docs/adr/20250106T120000.000Z_auth.md",
            architecture_state_path=None,
        )

        # Then: ADR path is included
        assert "docs/adr/20250106T120000.000Z_auth.md" in result

    def test_includes_architecture_state_when_present(self) -> None:
        """Prompt includes architecture state path when provided."""
        # When: build_agent_prompt called with architecture state path
        result = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path=None,
            architecture_state_path="docs/ARCHITECTURE_STATE.md",
        )

        # Then: Architecture state path is included
        assert "docs/ARCHITECTURE_STATE.md" in result

    def test_includes_all_artifacts(self) -> None:
        """Prompt includes all artifact paths."""
        # When: build_agent_prompt called with all paths
        result = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path="docs/adr/20250106T120000.000Z_auth.md",
            architecture_state_path="docs/ARCHITECTURE_STATE.md",
        )

        # Then: All paths are included
        assert "docs/CURRENT_TASK.md" in result
        assert "docs/adr/20250106T120000.000Z_auth.md" in result
        assert "docs/ARCHITECTURE_STATE.md" in result

    def test_has_role_definition(self) -> None:
        """Prompt includes role definition."""
        # When: build_agent_prompt called
        result = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path=None,
            architecture_state_path=None,
        )

        # Then: Role definition is present
        assert "You are a coding agent" in result

    def test_has_strict_rules(self) -> None:
        """Prompt includes strict rules."""
        # When: build_agent_prompt called
        result = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path=None,
            architecture_state_path=None,
        )

        # Then: Strict rules are present
        assert "Do NOT make architectural decisions" in result
        assert "Implement strictly" in result
        assert "stop and ask" in result

    def test_has_usage_instructions(self) -> None:
        """Prompt includes usage instructions."""
        # When: build_agent_prompt called
        result = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path=None,
            architecture_state_path=None,
        )

        # Then: Usage instructions are present
        assert "How to use" in result
        assert "Claude Code" in result
        assert "Cursor" in result
        assert "Windsurf" in result

    def test_has_code_block_markers(self) -> None:
        """Prompt has code block markers for easy copy-paste."""
        # When: build_agent_prompt called
        result = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path=None,
            architecture_state_path=None,
        )

        # Then: Code block markers are present
        assert "```" in result


class TestExtractPromptContent:
    """Tests for extract_prompt_content function."""

    def test_extracts_content_between_markers(self) -> None:
        """Extracts content between code block markers."""
        # Given: A full prompt with code block markers
        full_prompt = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path=None,
            architecture_state_path=None,
        )

        # When: Content is extracted
        extracted = extract_prompt_content(full_prompt)

        # Then: Core content is present without wrapper
        assert "You are a coding agent" in extracted
        assert "docs/CURRENT_TASK.md" in extracted
        assert "```" not in extracted
        assert "How to use" not in extracted

    def test_extracted_is_clean(self) -> None:
        """Extracted content is ready for agent input."""
        # Given: A full prompt with all paths
        full_prompt = build_agent_prompt(
            task_path="docs/CURRENT_TASK.md",
            adr_path="docs/adr/test.md",
            architecture_state_path="docs/ARCHITECTURE_STATE.md",
        )

        # When: Content is extracted
        extracted = extract_prompt_content(full_prompt)

        # Then: Meaningful content is present
        lines = extracted.strip().split("\n")
        assert len(lines) > 5


class TestAgentPromptPath:
    """Tests for AGENT_PROMPT_PATH constant."""

    def test_path_is_in_docs(self) -> None:
        """Prompt path is in docs directory."""
        # Then: Path starts with docs/
        assert AGENT_PROMPT_PATH.startswith("docs/")

    def test_path_is_markdown(self) -> None:
        """Prompt path is a markdown file."""
        # Then: Path ends with .md
        assert AGENT_PROMPT_PATH.endswith(".md")

    def test_path_is_agent_prompt(self) -> None:
        """Prompt path is AGENT_PROMPT.md."""
        # Then: Path is exactly docs/AGENT_PROMPT.md
        assert AGENT_PROMPT_PATH == "docs/AGENT_PROMPT.md"
