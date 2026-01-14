"""
LLM Adapter Factory.

Creates LLM adapters from environment configuration.
Supports BYOK (Bring Your Own Key) with fallback to mock.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from preflights.adapters.llm_errors import LLMCredentialsError, LLMProviderError
from preflights.application.llm_config import LLMConfig, LLMProvider

if TYPE_CHECKING:
    from preflights.application.ports.llm import LLMPort

logger = logging.getLogger(__name__)


# Credential environment variable names (in priority order)
CREDENTIAL_ENV_VARS: dict[str, tuple[str, ...]] = {
    "anthropic": ("PREFLIGHTS_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
    "openai": ("PREFLIGHTS_OPENAI_API_KEY", "OPENAI_API_KEY"),
    "openrouter": ("PREFLIGHTS_OPENROUTER_API_KEY", "OPENROUTER_API_KEY"),
}


def create_llm_adapter(
    provider_override: str | None = None,
    strict_mode: bool = False,
) -> "LLMPort":
    """
    Create LLM adapter from environment configuration.

    Environment variables (in priority order):
    - PREFLIGHTS_LLM_PROVIDER: mock | anthropic | openai | openrouter
    - PREFLIGHTS_LLM_MODEL: Optional model override
    - Credentials: PREFLIGHTS_*_API_KEY or standard env vars

    Args:
        provider_override: Override provider (for --llm-provider flag)
        strict_mode: If True, error on failure; if False, fallback to mock

    Returns:
        Configured LLM adapter

    Raises:
        LLMCredentialsError: If credentials missing in strict mode
        LLMProviderError: If adapter creation fails in strict mode
    """
    # Determine provider
    provider = provider_override or os.environ.get("PREFLIGHTS_LLM_PROVIDER", "mock")

    # Validate provider
    if provider not in ("mock", "anthropic", "openai", "openrouter"):
        logger.warning(f"Unknown provider '{provider}', falling back to mock")
        provider = "mock"

    # Mock is always available
    if provider == "mock":
        return _create_mock_adapter()

    # Get API key
    api_key = _get_api_key(provider)
    if api_key is None:
        if strict_mode:
            raise LLMCredentialsError(
                f"No API key found for {provider}. "
                f"Set {CREDENTIAL_ENV_VARS.get(provider, ('',))[0]} environment variable."
            )
        logger.warning(f"No API key for {provider}, falling back to mock")
        return _create_mock_with_fallback_flag()

    # Get optional model override
    model = os.environ.get("PREFLIGHTS_LLM_MODEL")

    # Create config
    config = LLMConfig(
        provider=provider,  # type: ignore[arg-type]
        model=model,
        api_key=api_key,
        strict_mode=strict_mode,
    )

    # Try to create adapter
    try:
        return _create_adapter(config)
    except LLMProviderError as e:
        if strict_mode:
            raise
        logger.warning(f"Failed to create {provider} adapter: {e}, falling back to mock")
        return _create_mock_with_fallback_flag()


def _get_api_key(provider: str) -> str | None:
    """
    Get API key with prefixed env var priority.

    PREFLIGHTS_*_API_KEY takes priority over standard env vars.
    """
    env_vars = CREDENTIAL_ENV_VARS.get(provider, ())
    for var_name in env_vars:
        value = os.environ.get(var_name)
        if value:
            return value
    return None


def _create_mock_adapter() -> "LLMPort":
    """Create mock adapter (default behavior)."""
    from preflights.adapters.mock_llm import MockLLMAdapter

    return MockLLMAdapter()


def _create_mock_with_fallback_flag() -> "LLMPort":
    """Create mock adapter with fallback flag set."""
    from preflights.adapters.mock_llm import MockLLMAdapter

    adapter = MockLLMAdapter()
    # Mark that this is a fallback
    adapter._is_fallback = True
    return adapter


def _create_adapter(config: LLMConfig) -> "LLMPort":
    """Create adapter instance based on provider."""
    provider = config.provider

    if provider == "anthropic":
        from preflights.adapters.anthropic_llm import AnthropicLLMAdapter

        return AnthropicLLMAdapter(config)

    elif provider == "openai":
        from preflights.adapters.openai_llm import OpenAILLMAdapter

        return OpenAILLMAdapter(config)

    elif provider == "openrouter":
        from preflights.adapters.openrouter_llm import OpenRouterLLMAdapter

        return OpenRouterLLMAdapter(config)

    else:
        raise ValueError(f"Unknown provider: {provider}")


def is_llm_available(provider: str | None = None) -> bool:
    """
    Check if LLM is available (credentials present).

    Args:
        provider: Specific provider to check (default: from env)

    Returns:
        True if credentials are available
    """
    if provider is None:
        provider = os.environ.get("PREFLIGHTS_LLM_PROVIDER", "mock")

    if provider == "mock":
        return True

    return _get_api_key(provider) is not None


def get_configured_provider() -> LLMProvider:
    """Get configured provider from environment."""
    provider = os.environ.get("PREFLIGHTS_LLM_PROVIDER", "mock")
    if provider in ("mock", "anthropic", "openai", "openrouter"):
        return provider  # type: ignore[return-value]
    return "mock"
