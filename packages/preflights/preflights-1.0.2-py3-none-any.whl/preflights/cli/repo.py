"""Repository discovery and path utilities."""

from __future__ import annotations

import os
from pathlib import Path

from preflights.cli.errors import NotARepositoryError


def discover_repo_root(start_path: str | None = None) -> str:
    """
    Discover git repository root.

    Args:
        start_path: Starting directory (default: current working directory)

    Returns:
        Absolute path to repository root

    Raises:
        NotARepositoryError: If no .git found
    """
    current = os.path.abspath(start_path or os.getcwd())

    while True:
        git_dir = os.path.join(current, ".git")
        if os.path.exists(git_dir):
            return current

        parent = os.path.dirname(current)
        if parent == current:  # Reached filesystem root
            raise NotARepositoryError(
                "Could not find git repository (no .git directory found)"
            )

        current = parent


def get_repo_root(repo_path: str | None) -> str:
    """
    Get repository root from explicit path or auto-discovery.

    Args:
        repo_path: Explicit repo path, or None for auto-discovery

    Returns:
        Absolute path to repository root
    """
    if repo_path:
        # Validate explicit path has .git
        abs_path = os.path.abspath(repo_path)
        if not os.path.exists(os.path.join(abs_path, ".git")):
            raise NotARepositoryError(
                f"Path '{repo_path}' is not a git repository",
                hint="Ensure path contains .git directory",
            )
        return abs_path

    return discover_repo_root()


def get_state_dir(repo_root: str) -> Path:
    """Get .preflights/ state directory path."""
    return Path(repo_root) / ".preflights"


def get_session_file(repo_root: str) -> Path:
    """Get current_session.json path."""
    return get_state_dir(repo_root) / "current_session.json"


def get_last_intention_file(repo_root: str) -> Path:
    """Get last_intention.txt path."""
    return get_state_dir(repo_root) / "last_intention.txt"


def ensure_state_dir(repo_root: str) -> Path:
    """Create .preflights/ directory if it doesn't exist."""
    state_dir = get_state_dir(repo_root)
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def ensure_preflights_ignored(repo_root: str) -> None:
    """
    Ensure .preflights/ is in .gitignore.

    Args:
        repo_root: Repository root path
    """
    gitignore_path = os.path.join(repo_root, ".gitignore")
    preflights_entry = ".preflights/"

    if os.path.exists(gitignore_path):
        with open(gitignore_path) as f:
            content = f.read()

        # Check if .preflights/ already ignored
        if preflights_entry in content:
            return  # Already ignored

        # Append to .gitignore
        with open(gitignore_path, "a") as f:
            if not content.endswith("\n"):
                f.write("\n")
            f.write(f"# Preflights ephemeral state\n{preflights_entry}\n")
    else:
        # Create .gitignore with .preflights/ entry
        with open(gitignore_path, "w") as f:
            f.write(f"# Preflights ephemeral state\n{preflights_entry}\n")
