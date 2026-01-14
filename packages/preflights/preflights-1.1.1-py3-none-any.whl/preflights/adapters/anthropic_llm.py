"""
Anthropic LLM Adapter.

Uses Claude via Anthropic API with tool use for structured output.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from preflights.adapters.llm_base import BaseLLMAdapter
from preflights.adapters.llm_errors import (
    LLMInvalidResponseError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)

if TYPE_CHECKING:
    from preflights.application.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class AnthropicLLMAdapter(BaseLLMAdapter):
    """Anthropic Claude adapter using tool use."""

    def __init__(self, config: "LLMConfig") -> None:
        """
        Initialize Anthropic adapter.

        Args:
            config: LLM configuration with API key

        Raises:
            LLMProviderError: If anthropic package not installed
        """
        super().__init__(config)

        try:
            import anthropic

            self._anthropic = anthropic
            self._client = anthropic.Anthropic(
                api_key=config.api_key,
                timeout=config.timeout_seconds,
            )
        except ImportError as e:
            raise LLMProviderError(
                "anthropic package not installed. Run: pip install anthropic"
            ) from e

    def _call_api(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Make API call to Anthropic with tool use.

        Args:
            system_prompt: System prompt
            user_message: User message
            tools: Tool schemas

        Returns:
            Parsed tool use result

        Raises:
            LLMTimeoutError: On timeout
            LLMProviderError: On API error
            LLMInvalidResponseError: On invalid response
        """
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                tools=tools,
            )

            return self._extract_tool_use(response)

        except self._anthropic.APITimeoutError as e:
            raise LLMTimeoutError(f"Anthropic API timeout: {e}") from e
        except self._anthropic.RateLimitError as e:
            raise LLMRateLimitError(f"Anthropic rate limit exceeded: {e}") from e
        except self._anthropic.APIError as e:
            raise LLMProviderError(f"Anthropic API error: {e}") from e

    def _extract_tool_use(self, response: Any) -> dict[str, Any]:
        """Extract structured data from tool use response."""
        for block in response.content:
            if block.type == "tool_use":
                return dict(block.input)

        # If no tool use, try to extract from text
        for block in response.content:
            if block.type == "text":
                logger.warning(
                    "No tool use in Anthropic response, got text instead"
                )
                raise LLMInvalidResponseError(
                    f"Expected tool use, got text: {block.text[:100]}..."
                )

        raise LLMInvalidResponseError("No content in Anthropic response")
