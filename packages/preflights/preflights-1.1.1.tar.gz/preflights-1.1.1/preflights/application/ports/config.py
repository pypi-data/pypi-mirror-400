"""Config loader port."""

from __future__ import annotations

from typing import Protocol

from preflights.core.types import HeuristicsConfig


class ConfigLoaderPort(Protocol):
    """
    Port for loading configuration.

    Loads HeuristicsConfig from:
    - Built-in defaults
    - Repository .preflights/config.yaml (future)
    - Global config (future)

    V1: Built-in defaults only.
    """

    def load(self, repo_path: str) -> HeuristicsConfig:
        """
        Load configuration for repository.

        Args:
            repo_path: Repository root path

        Returns:
            HeuristicsConfig for this repository

        Note: V1 always returns default config.
              Future may merge repo-specific overrides.
        """
        ...
