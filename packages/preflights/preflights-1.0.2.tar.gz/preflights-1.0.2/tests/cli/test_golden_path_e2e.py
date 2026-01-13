"""
End-to-end test for Golden Path CLI.

This test proves that the full wiring works:
CLI → App → Core → Filesystem

One happy path only. No edge cases.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _git_init(repo_root: Path) -> None:
    """Initialize a git repository with minimal config."""
    subprocess.run(["git", "init"], cwd=repo_root, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a minimal git repository with auth-related structure."""
    _git_init(tmp_path)

    # Create project structure so derive_allowlist() can find auth paths
    (tmp_path / "README.md").write_text("# Test Project\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "auth").mkdir()
    (tmp_path / "src" / "auth" / "login.ts").write_text("// Login\n")
    (tmp_path / "src" / "components").mkdir()
    (tmp_path / "src" / "components" / "Button.tsx").write_text("// Button\n")

    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    return tmp_path


@pytest.mark.e2e
def test_golden_path_interactive_creates_task(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Golden Path e2e test: pf start → answer questions → CURRENT_TASK.md created.

    Tests:
    - Repo auto-discovery from subdirectory
    - Interactive question/answer flow
    - Artifact creation (CURRENT_TASK.md)
    - .preflights/ directory created
    - .gitignore updated with .preflights/
    """
    from click.testing import CliRunner

    from preflights.cli.main import app

    # Run from subdirectory to validate repo auto-discovery
    workdir = git_repo / "src" / "components"
    monkeypatch.chdir(workdir)

    runner = CliRunner()

    # MockLLM questions for "Add OAuth authentication":
    #   Q1: auth_strategy (single_choice): OAuth, Email/Password, Magic Link, Other
    #   Q2: auth_library (single_choice): next-auth, passport, custom, Other
    # Using numeric indexes (more robust than text matching)
    user_input = "1\n1\n"

    result = runner.invoke(
        app,
        ["start", "Add OAuth authentication"],
        input=user_input,
        catch_exceptions=False,
    )

    # Assert CLI completed successfully
    assert result.exit_code == 0, f"CLI failed:\n{result.output}"

    # Assert CURRENT_TASK.md was created
    task_path = git_repo / "docs" / "CURRENT_TASK.md"
    assert task_path.exists(), f"CURRENT_TASK.md not found. Files: {list(git_repo.rglob('*'))}"

    # Assert task content has required structure
    content = task_path.read_text()

    # Must have title (may have metadata comments before it)
    assert "\n# " in content or content.startswith("# "), "Task must have a markdown title"

    # Must have key sections (structure validation)
    assert "## Objective" in content or "**Objective" in content, "Task must have Objective section"
    assert "OAuth" in content or "authentication" in content.lower(), "Task should mention OAuth/auth"

    # Must have allowlist (critical for AI agent)
    assert "Allowed" in content or "allowlist" in content.lower(), "Task must specify allowed files"

    # Must have acceptance criteria
    assert "Acceptance" in content or "Criteria" in content, "Task must have acceptance criteria"

    # Assert .preflights/ directory was created
    preflights_dir = git_repo / ".preflights"
    assert preflights_dir.exists(), ".preflights/ directory should exist"

    # Assert .gitignore contains .preflights/
    gitignore = git_repo / ".gitignore"
    assert gitignore.exists(), ".gitignore should exist (auto-created)"
    assert ".preflights/" in gitignore.read_text(), ".preflights/ must be git-ignored"

    # Assert AGENT_PROMPT.md was created
    agent_prompt_path = git_repo / "docs" / "AGENT_PROMPT.md"
    assert agent_prompt_path.exists(), "AGENT_PROMPT.md must be created"
    prompt_content = agent_prompt_path.read_text()
    assert "You are a coding agent" in prompt_content, "Prompt must have role definition"
    assert "docs/CURRENT_TASK.md" in prompt_content, "Prompt must reference task file"


@pytest.mark.e2e
def test_golden_path_with_explicit_repo_path(git_repo: Path) -> None:
    """
    Golden Path with explicit --repo-path (no auto-discovery).

    Verifies that --repo-path works when not running from inside the repo.
    """
    from click.testing import CliRunner

    from preflights.cli.main import app

    runner = CliRunner()

    user_input = "1\n1\n"

    result = runner.invoke(
        app,
        ["start", "Add OAuth authentication", "--repo-path", str(git_repo)],
        input=user_input,
        catch_exceptions=False,
    )

    assert result.exit_code == 0, f"CLI failed:\n{result.output}"

    # Artifacts should be created
    assert (git_repo / "docs" / "CURRENT_TASK.md").exists()


@pytest.mark.e2e
def test_golden_path_produces_adr_when_needed(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Golden Path with ADR creation.

    When decision detector triggers ADR, both ADR and ARCHITECTURE_STATE.md
    should be created.
    """
    from click.testing import CliRunner

    from preflights.cli.main import app

    monkeypatch.chdir(git_repo)

    runner = CliRunner()
    user_input = "1\n1\n"

    result = runner.invoke(
        app,
        ["start", "Add OAuth authentication"],
        input=user_input,
        catch_exceptions=False,
    )

    assert result.exit_code == 0, f"CLI failed:\n{result.output}"

    # "Add OAuth authentication" MUST trigger ADR creation (architectural decision)
    docs_dir = git_repo / "docs"
    adr_dir = docs_dir / "adr"

    # ADR MUST be created for auth intention (not optional)
    assert adr_dir.exists(), "ADR directory must exist for auth intention"
    adr_files = list(adr_dir.glob("*.md"))
    assert len(adr_files) == 1, f"Exactly one ADR expected, got {len(adr_files)}"

    # ADR file must have UID in filename
    adr_file = adr_files[0]
    assert "_" in adr_file.name, f"ADR filename must contain UID: {adr_file.name}"

    # ADR content must be meaningful (may have metadata comments before title)
    adr_content = adr_file.read_text()
    assert "\n# " in adr_content or adr_content.startswith("# "), "ADR must have a markdown title"
    assert "Authentication" in adr_content, "ADR must mention Authentication category"
    assert "OAuth" in adr_content, "ADR must mention OAuth decision"

    # Architecture state MUST exist when ADR is created
    arch_state = docs_dir / "ARCHITECTURE_STATE.md"
    assert arch_state.exists(), "ARCHITECTURE_STATE.md must exist when ADR is created"
    arch_content = arch_state.read_text()
    assert "Authentication" in arch_content, "Architecture state must include Authentication"


@pytest.mark.e2e
def test_golden_path_with_user_provided_allowlist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Golden Path when derive_allowlist() returns None.

    When repo has no recognizable structure, Core asks for allowlist_paths.
    User's answer should be used.
    """
    from click.testing import CliRunner

    from preflights.cli.main import app

    # Create minimal git repo WITHOUT auth structure
    _git_init(tmp_path)
    (tmp_path / "README.md").write_text("# Empty Project\n")

    monkeypatch.chdir(tmp_path)

    runner = CliRunner()

    # Flow:
    # Round 1 (MockLLM questions):
    #   Q1: auth_strategy → "1" (OAuth)
    #   Q2: auth_library → "1" (next-auth)
    # Round 2 (Core clarification - derive_allowlist returned None):
    #   Q1: allowlist_paths → "src/auth, lib/oauth"
    #   Q2: acceptance_criteria → "Users can login"
    user_input = "1\n1\nsrc/auth, lib/oauth\nUsers can login\n"

    result = runner.invoke(
        app,
        ["start", "Add OAuth authentication"],
        input=user_input,
        catch_exceptions=False,
    )

    assert result.exit_code == 0, f"CLI failed:\n{result.output}"

    # Task should be created with user-provided allowlist
    task_path = tmp_path / "docs" / "CURRENT_TASK.md"
    assert task_path.exists()

    content = task_path.read_text()
    # Verify user's allowlist is in the task
    assert "src/auth" in content or "lib/oauth" in content
