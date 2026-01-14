"""Default config loader."""

from __future__ import annotations

from preflights.core.types import HeuristicsConfig, default_v1_heuristics


class DefaultConfigLoader:
    """
    Default config loader.

    V1: Always returns built-in defaults.
    Future: May merge repo-specific config from .preflights/config.yaml
    """

    def __init__(
        self,
        override_config: HeuristicsConfig | None = None,
    ) -> None:
        """
        Initialize loader.

        Args:
            override_config: If provided, always return this config
                            (for testing specific configurations)
        """
        self._override_config = override_config

    def load(self, repo_path: str) -> HeuristicsConfig:
        """Load configuration for repository."""
        if self._override_config is not None:
            return self._override_config

        # V1: Always return defaults
        return default_v1_heuristics()

    def set_override(self, config: HeuristicsConfig) -> None:
        """Set override config (for testing)."""
        self._override_config = config
