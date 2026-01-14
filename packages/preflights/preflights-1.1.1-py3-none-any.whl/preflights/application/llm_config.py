"""
LLM Configuration Types.

Configuration for LLM providers (BYOK - Bring Your Own Key).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Supported LLM providers
LLMProvider = Literal["mock", "anthropic", "openai", "openrouter"]


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for LLM provider."""

    provider: LLMProvider
    model: str | None = None  # None = use provider default
    api_key: str | None = None  # None for mock
    timeout_seconds: float = 15.0
    max_retries: int = 2
    strict_mode: bool = False  # True = fail on error, False = fallback to mock


# Default models per provider
DEFAULT_MODELS: dict[LLMProvider, str] = {
    "mock": "mock",
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "openrouter": "anthropic/claude-sonnet-4-20250514",
}
