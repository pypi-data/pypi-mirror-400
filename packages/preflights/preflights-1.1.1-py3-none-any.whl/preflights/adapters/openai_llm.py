"""
OpenAI LLM Adapter.

Uses OpenAI API with function calling for structured output.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from preflights.adapters.llm_base import BaseLLMAdapter
from preflights.adapters.llm_errors import (
    LLMInvalidResponseError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from preflights.adapters.llm_prompts import (
    get_clarification_function_schema,
    get_decision_function_schema,
)

if TYPE_CHECKING:
    from preflights.application.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class OpenAILLMAdapter(BaseLLMAdapter):
    """OpenAI adapter using function calling."""

    def __init__(self, config: "LLMConfig") -> None:
        """
        Initialize OpenAI adapter.

        Args:
            config: LLM configuration with API key

        Raises:
            LLMProviderError: If openai package not installed
        """
        super().__init__(config)

        try:
            import openai

            self._openai = openai
            self._client = openai.OpenAI(
                api_key=config.api_key,
                timeout=config.timeout_seconds,
            )
        except ImportError as e:
            raise LLMProviderError(
                "openai package not installed. Run: pip install openai"
            ) from e

    def _call_api(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Make API call to OpenAI with function calling.

        Args:
            system_prompt: System prompt
            user_message: User message
            tools: Tool schemas (will be converted to functions)

        Returns:
            Parsed function call result

        Raises:
            LLMTimeoutError: On timeout
            LLMProviderError: On API error
            LLMInvalidResponseError: On invalid response
        """
        # Convert tools to OpenAI functions format
        functions = self._tools_to_functions(tools)
        function_name = functions[0]["name"] if functions else None

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                functions=functions,
                function_call={"name": function_name} if function_name else "auto",
            )

            return self._extract_function_call(response)

        except self._openai.APITimeoutError as e:
            raise LLMTimeoutError(f"OpenAI API timeout: {e}") from e
        except self._openai.RateLimitError as e:
            raise LLMRateLimitError(f"OpenAI rate limit exceeded: {e}") from e
        except self._openai.APIError as e:
            raise LLMProviderError(f"OpenAI API error: {e}") from e

    def _tools_to_functions(
        self, tools: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert Anthropic tool schema to OpenAI function format."""
        functions = []
        for tool in tools:
            name = tool.get("name", "")
            if name == "submit_clarification":
                functions.append(get_clarification_function_schema())
            elif name == "submit_decision":
                functions.append(get_decision_function_schema())
            else:
                # Generic conversion
                functions.append({
                    "name": name,
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {}),
                })
        return functions

    def _extract_function_call(self, response: Any) -> dict[str, Any]:
        """Extract structured data from function call response."""
        message = response.choices[0].message

        if message.function_call:
            try:
                result: dict[str, Any] = json.loads(message.function_call.arguments)
                return result
            except json.JSONDecodeError as e:
                raise LLMInvalidResponseError(
                    f"Invalid JSON in function call: {e}"
                ) from e

        # No function call
        if message.content:
            logger.warning(
                "No function call in OpenAI response, got text instead"
            )
            raise LLMInvalidResponseError(
                f"Expected function call, got text: {message.content[:100]}..."
            )

        raise LLMInvalidResponseError("No content in OpenAI response")
